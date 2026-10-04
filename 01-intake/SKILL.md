# Steps 1-2: Discovery

This covers the first two steps of the Path Forward: detect where the user is
working, request the artifacts that own the definitions, and let agent-studio's
Tableau / Power BI tools inspect them. Extract what is available; ask only for
missing dependencies or baseline context, not a generic discovery questionnaire.

---

## Optional Step 0 — Cortex Sense (Public Preview, November 2026)

If available, run **Cortex Sense** *before* Step 2 finishes. It auto-builds
semantic context from Snowflake metadata, query history, dbt, Tableau, and Power
BI, and surfaces **naming conflicts, metric gaps, and coverage issues** — which
makes the Step 2 mapping faster and more accurate. Mark it clearly as coming soon;
do not block the workflow on it.

---

## Step 1 — Choose ONE existing dashboard: get and stage its file

### 1a. Detect the surface (no question)

```bash
uname -s; test -d /workspace && echo cloud_mount
```

| Result | Surface | Staging tool |
|---|---|---|
| No `/workspace` (macOS, Windows, Linux laptop) | Desktop / CLI | `PUT file://` |
| Linux with `/workspace` | Snowsight | `COPY FILES FROM snow://workspace` |
| Still unclear | Ask once | — |

(No documented environment variable names the surface, so probe the
filesystem.)

### 1b. Request owning artifacts and one baseline (one interaction)

If the user already supplied files, inspect those first. Otherwise use
ask_user_question, showing only the relevant tool guidance when it is known:

> Choose one dashboard/report page. On Desktop/CLI, give its file path(s);
> in Snowsight, upload the files into the workspace and say `done`.
> - **Tableau:** its `.twb` or `.twbx` workbook. If it uses a published data
>   source, also include that source's `.tds` or `.tdsx`, if available.
> - **Power BI:** preferably a `.pbit` exported from the model-owning file
>   (Desktop: File > Export > Power BI template), or a model-containing `.pbix`.
>   If the report connects to a shared model, obtain that artifact from its owner;
>   another copy of the thin report will not supply the underlying definitions.
> - Include a screenshot or results export of the chosen page with filters and
>   date range visible. If unavailable, say so. No usable model file? Screenshots
>   from any BI tool are still useful; use `none` if there is no dashboard.

Packaged files may contain business rows; request definitions without rows when
available. Packaging does not make unsupported calculations convertible. Do not
ask users to change live/extract or Import/DirectQuery mode just to import metadata.
Screenshots provide scope/results, not proof of a formula. A source-only file
can still be useful; it just needs separate dashboard context.

- Screenshots or `none`: skip staging/analyze, but complete the baseline record
  and gap-only confirmation in 2c before the build router. With `none`, ask for
  the intended domain/questions and an approved reference query/result if absent.
  Before the router, confirm the data is in Snowflake (1b-3 "Find it" row).
- Snowsight: find the file yourself. The sandbox mounts only the **default**
  workspace at `/workspace`, so try `find /workspace -maxdepth 4 -type f \(
  -iname '*.twb*' -o -iname '*.tds*' -o -iname '*.pbi[tx]' \)` first. Not
  there? The file is in another workspace: run `SHOW WORKSPACES` and use the
  `name` column in 1c. A BI file dropped into the chat is not in `/workspace`;
  ask for a workspace upload instead. A screenshot pasted into the chat is fine:
  read it from the conversation as baseline evidence; don't look for it on disk.
- One dashboard only — do not bulk-import the BI estate.
- File name has `[` or `]`: stage downloads fail. Rename it (Desktop) or ask the
  user to rename it (Snowsight).

### 1b-2. Check sources and pages locally (no question)

Before staging a BI file, read its sources and, for Power BI, its pages. This
skill covers dashboards whose **data is in Snowflake**, whether or not the file
connects to Snowflake. Record each source table's connection; 1b-3 routes them.

**Tableau.** `.twbx`/`.tdsx` are
zip archives; `.twb`/`.tds` are plain XML. Both surfaces have a shell.

```bash
rm -rf /tmp/sld_check && mkdir -p /tmp/sld_check
unzip -o -q '<file>.twbx' -d /tmp/sld_check   # .twb/.tds: copy it into /tmp/sld_check instead
grep -ho "<connection [^>]*class='[a-z-]*'" /tmp/sld_check/*.tw[bs] 2>/dev/null \
  | grep -o "class='[a-z-]*'" | sort | uniq -c
```

Ignore `federated`; it wraps the real connections. `repository-location` alone
is publish history, not a published source.

| Finding | Meaning | Next |
|---|---|---|
| A `snowflake` connection | Importable | Stage (1c) |
| A `sqlproxy` connection | Published-source stub | Ask for the named source's `.tds`/`.tdsx` now, in this turn. Run this check on it too: if it is also `sqlproxy`, it holds no tables; ask for a copy connected straight to Snowflake, or go to 1b-3 "Find it". Stage both (1c) |
| A `hyper` extract next to a `snowflake` connection | Extract of a Snowflake source (unverified: `tableau_analyze` may reject nested Hyper) | Stage (1c). If analyze rejects it, route the extract's tables by 1b-3 "Find it" |
| Other classes (`excel-direct`, `sqlserver`, `textscan`, …) | Not connected to Snowflake | 1b-3 |

**Power BI.** `.pbix`/`.pbit` are zip archives. Power Query sources are in
`DataMashup`: a 4-byte version, a 4-byte little-endian length, then a zip holding
`Formulas/Section1.m`. Report pages are UTF-16 JSON in `Report/Layout`.

```bash
rm -rf /tmp/sld_check && mkdir -p /tmp/sld_check && unzip -o -q '<file>.pbix' -d /tmp/sld_check
python3 - <<'PY'
import io, json, re, struct, zipfile
b = open('/tmp/sld_check/DataMashup', 'rb').read()
n = struct.unpack('<I', b[4:8])[0]
m = zipfile.ZipFile(io.BytesIO(b[8:8 + n])).read('Formulas/Section1.m').decode()
for line in m.splitlines():
    if re.search(r'^shared |Source\s*=', line.strip()): print(line.strip()[:160])
L = json.loads(open('/tmp/sld_check/Report/Layout', 'rb').read().decode('utf-16-le'))
for sec in L['sections']:
    refs = set()
    for v in sec['visualContainers']:
        pj = json.loads(v['config']).get('singleVisual', {}).get('projections', {})
        refs |= {p['queryRef'] for vv in pj.values() for p in vv}
    print('PAGE', sec['displayName'], sorted(refs))
PY
```

| Finding | Meaning | Next |
|---|---|---|
| `Source =` uses `Snowflake.Databases` | Importable | Stage (1c) |
| `Source =` uses another connector (`Sql.Database`, `Excel.Workbook`, `Csv.Document`, `SharePoint.*`, embedded rows) | Not connected to Snowflake | 1b-3 |
| No `DataMashup` or no `Section1.m` | Thin report or live connection | 2b "thin report" |

Keep the page list. Measures referenced on the baseline page become the
required metrics in 2c; one missing from the model's measures (for example a
hidden or KPI-only measure) is a gap to ask about, not something to infer.

Read only the XML/JSON/M text. Do not open `.hyper` files, decompress
`DataModel`, or run file-supplied code.

### 1b-3. Route each required table by where its data lives

Check every table the baseline page needs, not just whether the file has any
Snowflake source. One table can block a metric even when the rest import.

| Required table | Route |
|---|---|
| Connected to Snowflake in the file | Import (1c onward) |
| Not connected, but the data is in Snowflake | **Find it:** ask where it lives, or search metadata/query history for matching objects and have the user confirm. Then build from metadata (`02-build/autopilot.md`), keeping the file's formulas and page context |
| Not in Snowflake | Stop for that table. Say which tables, and the next step: load the data into Snowflake, or repoint the workbook / Power Query source to Snowflake, then re-run the skill |

Mixed files: import the Snowflake-connected tables and route the rest by this
table. Never let a non-Snowflake table reach export, where it is silently
dropped. If every required table stops, stop the run with the same next step.

### 1c. Stage it (no question)

agent-studio's tools only take stage paths, so stage first. The stage only
holds the file; it doesn't decide where the semantic view goes (2c does). Put
it in the session's current schema (`SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()`).
None set, or `CREATE STAGE` fails? Use any schema the role can create a stage
in; ask only if there isn't one.

```sql
-- Not TEMPORARY: it ends with the session, before the tools read it.
CREATE STAGE IF NOT EXISTS <DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE
  DIRECTORY = (ENABLE = TRUE) ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');
-- Desktop / CLI
PUT 'file://<abs path>' @<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- Snowsight: <workspace> is the `name` from SHOW WORKSPACES (e.g. DEFAULT$),
-- double-quoted if it has spaces: USER$.PUBLIC."Agentic BI"
COPY FILES INTO @<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE/
  FROM 'snow://workspace/USER$.PUBLIC.<workspace>/versions/live/<folder>/'
  FILES = ('<file>');
LIST @<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE;
```

If the shell mangles `$` or `"`, run the SQL from a `.sql` file. If `FILES = (...)`
errors, drop it and put the full file path at the end of `FROM`.

Never use `cortex ws cp` to reach a stage — it copies to the sandbox and still
reports success. File missing after one retry: give the clicks *Data » Databases
» <DB> » <SCHEMA> » Stages » SEMANTIC_IMPORT_STAGE » + Files*.

---

## Step 2 — Map data objects, questions, and business definitions

Analyze establishes available model structure, not complete dashboard semantics
or final conversion coverage.

### 2a. Analyze it (no question)

Use agent-studio's built-in tools. Read its
`semantic-view/reference/tableau_tool_reference.md` (or `pbi_tool_reference.md`)
first for exact parameter names.

```bash
cortex agent-studio backend --tool tableau_analyze --parameters '{"file_path":"@<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE/<file>"}'
cortex agent-studio backend --tool pbi_analyze --parameters '{"file_path":"@<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE/<file>","validate_in_snowflake":true}'
```

No `cortex` CLI? One JSON argument:
`SELECT SYSTEM$CORTEX_ANALYST_SVA_TOOL($${"tool":"tableau_analyze","parameters":{"file_path":"@<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE/<file>"}}$$);`
(Undocumented. Check the result for an embedded error even when the SQL succeeds.)

Parse the response's stringified `result`. `success: true` alone is not a pass:
treat analyze as failed if `datasources` is empty or `total_columns` is 0
(Tableau) or `total_tables` is 0 (Power BI), and treat export as failed if
`errors` is non-empty, `table_count` is 0, or `yaml_content` has no tables.
Read `warnings` and `message` for the cause, then go to 2b. Otherwise retain worksheets
(Tableau), resolved tables/measures (Power BI), `has_custom_sql`, and warnings.
Power BI's analyze validation warnings are under `validation.validation_warnings`;
`m_query_warnings` describe unresolved sources. `unsupported_measure_count` is
an **export** result, not an analyze field. Final coverage is checked after export.
Power BI's documented tools do not expose report-page/visual/slicer context
(use the 1b-2 page list);
Tableau `usage_context` arrives at export. Mark unavailable context as missing.

### 2b. Fix only what's broken

| Sign | Action |
|---|---|
| Published Tableau source reference (a `sqlproxy` connection in the XML) with missing relations. `relation_count: 0` without a stub is not this case. | Use the `.tds`/`.tdsx` requested in 1b-2 (ask now only if that was skipped). Keep the workbook as the primary input; stage the sidecar for **export's** `additional_files`. Only the first sidecar is used; `published_datasource_stub_name` selects one stub, not a bulk merge. If the baseline needs several unresolved sources, explain the limit and agree a narrower scope or another build route. |
| Tableau source-only `.tds`/`.tdsx` | Keep usable definitions; collect the baseline page/results separately. Do not require a workbook solely to import source metadata. |
| Power BI thin report / missing model | Request the model owner's PBIT or model-containing PBIX, not another export of the same thin report. |
| Unsupported artifact (for example bare Hyper or PBIP) | Explain the missing container/definitions and request a supported owning artifact; renaming an extension is not conversion. |
| Source pointer, unresolved M source, or external data | Check retained source metadata first, then discover and confirm compatible Snowflake objects. An extract of a Snowflake connection still carries its source definitions. Do not assume rows or matching column names establish lineage, or that a schema remap recovers a table dropped during parsing. |

Record the missing dependency and why the replacement helps. Retry only when
the artifact, mapping, or relevant parameters change. If the owner cannot provide
it, offer metadata-based build with the evidence already collected, or pause.
Do not cycle file formats for a translator limitation or restart successful work.

### 2c. One confirm, pre-filled

Maintain one **baseline record** in the working project, populated from supplied
evidence: chosen dashboard/page; required metrics/questions and their definition
sources; grouping/filter/date context and refresh cutoff; expected results (or
missing); primary artifact and dependencies; original source FQNs; selected
scope; deployment FQN; optional confirmed source remap; unresolved gaps.

Use one ask_user_question call to confirm **baseline scope** and **deployment
`DATABASE.SCHEMA`**, adding only material missing context. Propose the worksheets
or metrics belonging to that baseline, not every object in a shared workbook/model.
Retain supporting tables, dependent measures, and join keys. If page-to-model
mapping cannot be inferred, ask rather than claiming table selection identifies a page.

| Source tables live in | Default target |
|---|---|
| One schema | That schema |
| Several schemas | The schema holding the fact table(s) the dashboard reads most; tie: the most-queried table's schema |
| No write access there | First other choice the role can create in; say why |

This is the **deployment destination**, not a source-table remap. Preserve each
original source FQN; only record a remap when the user confirms an actual source
location change. Do not pass the deployment schema as an exporter remap.

Show the proposed baseline and remaining gaps in the confirmation. Missing
expected results may remain pending during candidate construction, but Step 5
cannot claim parity until evidence is supplied. Treat visible filter selections
as the test context, not automatically as permanent agent defaults.

---

## Exit criteria for discovery

Before moving to Step 3, you should have:
- Baseline record with confirmed scope and deployment destination.
- Staged usable artifacts and analyze results when present; otherwise an explicit
  no-model/fallback decision. Missing dependencies have a specific next action.
- Required definitions and expected results captured or explicitly marked missing.

Then proceed to `02-build/SKILL.md` and apply the routing rule.
