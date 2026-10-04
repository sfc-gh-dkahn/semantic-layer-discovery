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
- Snowsight: find the file yourself. The sandbox mounts only the **default**
  workspace at `/workspace`, so try `find /workspace -maxdepth 4 -type f \(
  -iname '*.twb*' -o -iname '*.tds*' -o -iname '*.pbi[tx]' \)` first. Not
  there? The file is in another workspace: run `SHOW WORKSPACES` and use the
  `name` column in 1c. A file dropped into the chat is not in `/workspace`;
  ask for a workspace upload instead.
- One dashboard only — do not bulk-import the BI estate.
- File name has `[` or `]`: stage downloads fail. Rename it (Desktop) or ask the
  user to rename it (Snowsight).

### 1c. Stage it (no question)

agent-studio's tools only take stage paths, so stage first. The stage only
holds the file; it doesn't decide where the semantic view goes (2c does). Put
it in the session's current schema (`SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()`).
None set, or `CREATE STAGE` fails? Use any schema the role can create a stage
in; ask only if there isn't one.

```sql
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

Parse the response's stringified `result` and check success. Retain worksheets
(Tableau), resolved tables/measures (Power BI), `has_custom_sql`, and warnings.
Power BI's analyze validation warnings are under `validation.validation_warnings`;
`m_query_warnings` describe unresolved sources. `unsupported_measure_count` is
an **export** result, not an analyze field. Final coverage is checked after export.
Power BI's documented tools do not expose report-page/visual/slicer context;
Tableau `usage_context` arrives at export. Mark unavailable context as missing.

### 2b. Fix only what's broken

| Sign | Action |
|---|---|
| Published Tableau source reference with missing relations (`relation_count: 0` is a clue, not proof) | Request the owning `.tds`/`.tdsx`. Keep the workbook as the primary input; stage the sidecar for **export's** `additional_files`. Only the first sidecar is used; `published_datasource_stub_name` selects one stub, not a bulk merge. If the baseline needs several unresolved sources, explain the limit and agree a narrower scope or another build route. |
| Tableau source-only `.tds`/`.tdsx` | Keep usable definitions; collect the baseline page/results separately. Do not require a workbook solely to import source metadata. |
| Power BI thin report / missing model | Request the model owner's PBIT or model-containing PBIX, not another export of the same thin report. |
| Unsupported artifact (for example bare Hyper or PBIP) | Explain the missing container/definitions and request a supported owning artifact; renaming an extension is not conversion. |
| Source pointer, unresolved M source, or external data | Check retained source metadata first, then discover and confirm compatible Snowflake objects. An extract does not automatically erase source definitions. Do not assume rows or matching column names establish lineage, or that a schema remap recovers a table dropped during parsing. |

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
