# Steps 1-2: Intake

Get one dashboard's files, check where its data lives, stage them, analyze
them, and confirm scope. Ask about gaps only; this is not an interview.

---

## Step 1 — Get the files and a baseline

### 1a. Detect the surface (no question)

```bash
uname -s; test -d /workspace && echo cloud_mount
```

| Result | Surface | Staging tool |
|---|---|---|
| No `/workspace` (macOS, Windows, Linux laptop) | Desktop / CLI | `PUT file://` |
| Linux with `/workspace` | Snowsight | `COPY FILES FROM snow://workspace` |
| Still unclear | Ask once | — |

No environment variable names the surface, so probe the filesystem.

### 1b. Ask for the files (one question)

If the user already supplied files, inspect them first. Otherwise ask once with
ask_user_question, showing only the guidance for their BI tool if you know it:

> Choose one dashboard/report page. On Desktop/CLI, give its file path(s);
> in Snowsight, upload the files into the workspace and say `done`.
> - **Tableau:** its `.twb` or `.twbx` workbook. If it uses a published data
>   source, also include that source's `.tds` or `.tdsx`, if available.
> - **Power BI:** preferably a `.pbit` exported from the model-owning file
>   (Desktop: File > Export > Power BI template), or a model-containing `.pbix`.
>   If the report connects to a shared model, get that model's file from its owner;
>   another copy of the thin report has no definitions.
> - Include a screenshot or results export of the chosen page with filters and
>   date range visible. If unavailable, say so. No usable model file? Screenshots
>   from any BI tool are still useful; use `none` if there is no dashboard.

Then:
1. **Finding the file in Snowsight:** only the default workspace is mounted at
   `/workspace`. Try `find /workspace -maxdepth 4 -type f \( -iname '*.twb*' -o
   -iname '*.tds*' -o -iname '*.pbi[tx]' \)`. Not there? Run `SHOW WORKSPACES`
   and use the `name` column in 1c.
2. **Chat attachments:** a BI file dropped into the chat is not on disk; ask for
   a workspace upload. A pasted screenshot is fine: read it from the
   conversation as baseline evidence.
3. **File names with `[` or `]`** break stage downloads. Rename it (Desktop) or
   ask the user to (Snowsight). Quote names with spaces in `PUT` and `COPY FILES`.
4. **One dashboard only.** Don't import the whole BI estate.
5. **Screenshots only, or `none`:** skip 1b-2 through 2b. Still fill the
   baseline record and confirm in 2c. Confirm the data is in Snowflake with the
   1b-3 "Find it" row. With `none`, also ask for the domain, the questions, and
   an approved reference query or result. Screenshots from another BI tool
   (Looker, Qlik, and so on): ask once for its model or metric definitions
   (LookML, for example) if it has them; otherwise mark the formulas missing.

Ask for definitions without rows when possible. Never ask users to switch
live/extract or Import/DirectQuery. Screenshots show scope and results, not
formulas. Why: `reference/rules.md` § Inputs.

### 1b-2. Check sources and pages locally (no question)

Before staging, read each file's sources, formulas, and (Power BI) pages.
Record each source table's connection; 1b-3 routes them. Keep every formula in
the baseline record: the Autopilot route needs them when import can't run. Read
only XML, JSON, and M text: never open `.hyper` files, decompress `DataModel`,
or run code from the file.

**Tableau.** `.twbx`/`.tdsx` are zip archives; `.twb`/`.tds` are plain XML.

```bash
rm -rf /tmp/sld_check && mkdir -p /tmp/sld_check
unzip -o -q '<file>.twbx' -d /tmp/sld_check   # .twb/.tds: copy it into /tmp/sld_check instead
grep -ho "<connection [^>]*class='[a-z-]*'" /tmp/sld_check/*.tw[bs] 2>/dev/null \
  | grep -o "class='[a-z-]*'" | sort | uniq -c
python3 - <<'PY'   # calculated fields, any connection type
import glob, xml.etree.ElementTree as ET
for f in glob.glob('/tmp/sld_check/*.tw[bs]'):
    seen = set()
    for c in ET.parse(f).getroot().iter('column'):
        k = c.find('calculation')
        if k is None or not k.get('formula'): continue
        key = (c.get('caption') or c.get('name'), ' '.join(k.get('formula').split()))
        if key not in seen: seen.add(key); print('CALC', key[0], '=', key[1])
PY
```

Ignore `federated`; it wraps the real connections. `repository-location` alone
is publish history, not a published source.

| Finding | Meaning | Next |
|---|---|---|
| A `snowflake` connection | Importable | Stage (1c) |
| A `sqlproxy` connection | Published-source stub | Ask for the named source's `.tds`/`.tdsx` now, in this turn. Stage the workbook meanwhile, but analyze only once the `.tds` arrives. Run this check on the `.tds`: if it is also `sqlproxy`, it holds no tables, so don't stage it; ask for a copy connected straight to Snowflake, or go to 1b-3 "Find it". Otherwise stage it (1c) |
| A `hyper` extract next to a `snowflake` connection | Extract of a Snowflake source (unverified: `tableau_analyze` may reject nested Hyper) | Stage (1c). If analyze rejects it, route the extract's tables by 1b-3 "Find it" |
| Other classes (`excel-direct`, `sqlserver`, `textscan`, …) | Not connected to Snowflake | 1b-3 |

**Power BI.** `.pbix`/`.pbit` are zip archives. What's readable depends on the file:
- `.pbit` has `DataModelSchema`: plain JSON with every table's source and every
  DAX measure. This is the best file to have.
- Older `.pbix` files have `DataMashup` (a 4-byte version, a 4-byte
  little-endian length, then a zip holding `Formulas/Section1.m`), which names
  the sources. Their DAX sits in the compressed `DataModel`.
- Newer `.pbix` files keep sources and DAX only in `DataModel`.
- No `DataModel` or `DataModelSchema` at all: a thin report.
- Pages are in `Report/Layout` (classic) or `Report/definition/pages/` (PBIR).

```bash
rm -rf /tmp/sld_check && mkdir -p /tmp/sld_check && unzip -o -q '<file>.pbix' -d /tmp/sld_check
python3 - <<'PY'
import glob, io, json, os, re, struct, zipfile
d = '/tmp/sld_check'
has = lambda p: os.path.exists(os.path.join(d, p))
print('MODEL', 'yes' if has('DataModel') or has('DataModelSchema') else 'NO (thin report)')
if has('DataMashup'):
    b = open(f'{d}/DataMashup', 'rb').read()
    n = struct.unpack('<I', b[4:8])[0]
    m = zipfile.ZipFile(io.BytesIO(b[8:8 + n])).read('Formulas/Section1.m').decode()
    for line in m.splitlines():
        if re.search(r'^shared |Source\s*=', line.strip()): print('SRC', line.strip()[:160])
elif has('DataModel') and not has('DataModelSchema'):
    print('SRC none readable: sources and formulas are inside the compressed DataModel')
if has('DataModelSchema'):  # .pbit only: plain JSON model with every measure
    s = json.loads(open(f'{d}/DataModelSchema', 'rb').read().decode('utf-16-le').lstrip('\ufeff'))
    j = lambda e: ' '.join(e) if isinstance(e, list) else (e or '')
    for t in s['model']['tables']:
        for p in t.get('partitions', []):
            print('SRC', t['name'], j(p.get('source', {}).get('expression'))[:160])
        for ms in t.get('measures', []):
            print('MEASURE', f"{t['name']}.{ms['name']}", '=', j(ms.get('expression')))
def refs(obj):  # every queryRef in a visual definition
    if isinstance(obj, dict):
        if 'queryRef' in obj: yield obj['queryRef']
        for v in obj.values(): yield from refs(v)
    elif isinstance(obj, list):
        for v in obj: yield from refs(v)
if has('Report/Layout'):  # classic report format
    L = json.loads(open(f'{d}/Report/Layout', 'rb').read().decode('utf-16-le'))
    for sec in L['sections']:
        r = set()
        for v in sec['visualContainers']: r |= set(refs(json.loads(v['config'])))
        print('PAGE', sec['displayName'], sorted(r))
for pj in sorted(glob.glob(f'{d}/Report/definition/pages/*/page.json')):  # PBIR format
    r = set()
    for vj in glob.glob(os.path.join(os.path.dirname(pj), 'visuals/*/visual.json')):
        r |= set(refs(json.load(open(vj, encoding='utf-8'))))
    print('PAGE', json.load(open(pj, encoding='utf-8'))['displayName'], sorted(r))
PY
```

| Finding | Meaning | Next |
|---|---|---|
| `SRC` uses `Snowflake.Databases` | Importable | Stage (1c) |
| `SRC` uses another connector (`Sql.Database`, `Excel.Workbook`, `Csv.Document`, `SharePoint.*`, embedded rows) | Not connected to Snowflake | 1b-3 |
| `SRC none readable` | Sources and DAX are only in the compressed model | Stage (1c) and let `pbi_analyze` (2a) name the sources, then route them by this table. If any required table isn't connected to Snowflake, ask once for a `.pbit` (File › Export › Power BI template) so its DAX can be read for 1b-3 |
| `MODEL NO` | Thin report on a shared model | 2b "Power BI thin report / missing model" |

Keep the page list and every `CALC` / `MEASURE` line. Measures on the baseline
page are the required metrics in 2c. If one is missing from the model (a hidden
or KPI-only measure, say), ask about it; don't infer it.

### 1b-3. Route each required table by where its data lives

Check every table the baseline page needs, not just whether the file has any
Snowflake source.

| Required table | Route |
|---|---|
| Connected to Snowflake in the file | Import (1c onward) |
| Not connected, but the data is in Snowflake | **Find it:** search metadata and query history for matching objects first, then ask once, showing the candidates, for the user to confirm or correct. Build from metadata (`02-build/autopilot.md`) on the confirmed objects, passing the `CALC`/`MEASURE` formulas and page context from 1b-2 |
| Not in Snowflake | Stop for that table. Say which tables, and the next step: load the data into Snowflake, or repoint the workbook / Power Query source to Snowflake, then re-run the skill |

In a mixed file, import the Snowflake-connected tables and route the rest by
this table. Keep non-Snowflake tables out of export: it drops them silently.
If a stopped table feeds required metrics, say which ones in the 2c
confirmation and offer the remaining scope as a partial delivery, or a pause.
If every required table stops, stop the run with the same next step.

### 1c. Stage the files (no question)

agent-studio's tools read only stage paths. The stage just holds the files; 2c
picks where the Semantic View goes.

1. Use the session's schema (`SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()`). If
   none is set or `CREATE STAGE` fails, use any schema the role can create a
   stage in. Ask only if there is none.
2. Create, copy, and list:

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

3. If the shell mangles `$` or `"`, run the SQL from a `.sql` file. If
   `FILES = (...)` errors, drop it and put the full file path at the end of `FROM`.
4. Use `COPY FILES` or `PUT`, never `cortex ws cp`: it copies to the sandbox
   and still reports success.
5. File still missing after one retry? Give the clicks: *Data » Databases »
   <DB> » <SCHEMA> » Stages » SEMANTIC_IMPORT_STAGE » + Files*.

---

## Step 2 — Analyze, fix, confirm

### 2a. Analyze (no question)

1. Read agent-studio's `semantic-view/reference/tableau_tool_reference.md` (or
   `pbi_tool_reference.md`) for exact parameter names.
2. Run analyze:

```bash
cortex agent-studio backend --tool tableau_analyze --parameters '{"file_path":"@<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE/<file>"}'
cortex agent-studio backend --tool pbi_analyze --parameters '{"file_path":"@<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE/<file>","validate_in_snowflake":true}'
```

   No `cortex` CLI? Pass one JSON argument (undocumented; check the result for
   an embedded error even when the SQL succeeds):
   `SELECT SYSTEM$CORTEX_ANALYST_SVA_TOOL($${"tool":"tableau_analyze","parameters":{"file_path":"@<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE/<file>"}}$$);`

3. Parse the stringified `result`. Judge it by its contents, not `success: true`:

| Tool | Failed when |
|---|---|
| Tableau analyze | `datasources` is empty or `total_columns` is 0 |
| Power BI analyze | `total_tables` is 0 |
| Any export | `errors` is non-empty, `table_count` is 0, or `yaml_content` has no tables |

   On failure, read `warnings` and `message`, then go to 2b.
4. On success, keep worksheets (Tableau), resolved tables and measures (Power
   BI), `has_custom_sql`, and warnings. Power BI puts analyze warnings under
   `validation.validation_warnings`; `m_query_warnings` name unresolved sources.
   `unsupported_measure_count` comes only from export.
5. Analyze shows model structure, not full dashboard meaning or final coverage.
   Power BI's tools don't return page, visual, or slicer context; use the 1b-2
   page list. Tableau's `usage_context` arrives at export. Mark any context you
   lack as missing.

### 2b. Fix only what's broken

| Sign | Action |
|---|---|
| Published Tableau source reference (a `sqlproxy` connection in the XML) with missing relations. `relation_count: 0` without a stub is not this case. | Use the `.tds`/`.tdsx` requested in 1b-2 (ask now only if that was skipped). Keep the workbook as the primary input; stage the sidecar for **export's** `additional_files`. Only the first sidecar is used; `published_datasource_stub_name` selects one stub, not a bulk merge. If the baseline needs several unresolved sources, explain the limit and agree a narrower scope or another build route. |
| Tableau source-only `.tds`/`.tdsx` | Keep its definitions; collect the baseline page and results separately. A workbook is not required just to import source metadata. |
| Power BI thin report / missing model | Request the model owner's PBIT or model-containing PBIX, not another export of the same thin report. |
| Unsupported artifact (for example bare Hyper or PBIP) | Explain what's missing and request a supported owning artifact. Renaming an extension doesn't convert it. |
| Source pointer, unresolved M source, or external data | Check retained source metadata, then find and confirm the matching Snowflake objects (1b-3 "Find it"). Lineage rules: `reference/rules.md` § Sources. |
| Analyze failed and no row above fits | Re-read the 1b-2 findings for the cause and retry once with corrected inputs. Still failing: offer the metadata build with the 1b-2 formulas, or pause. |

Record each missing piece and why the replacement helps. Retry only when the
file, mapping, or parameters change. If the owner can't provide it, offer the
metadata build with the evidence you have, or pause. A translator limit is not
fixed by another file format; never restart work that succeeded.

### 2c. Confirm scope and destination (one question, pre-filled)

1. **Fill the baseline record** in the working project from the evidence:

| Field | Contents |
|---|---|
| Baseline | Dashboard and page |
| Required metrics/questions | Each with its definition source |
| Context | Grouping, filters, date range, refresh cutoff |
| Expected results | Values, or "missing" |
| Artifacts | Primary file and dependencies |
| Sources | Original source FQNs; confirmed remap, if any |
| Scope and destination | Selected scope; deployment FQN |
| Gaps | Anything unresolved |

2. **Pick the default destination:**

| Source tables live in | Default target |
|---|---|
| One schema | That schema |
| Several schemas | The schema holding the fact table(s) the dashboard reads most; tie: the most-queried table's schema |
| No write access there | Next, the other source schemas, most-read first; then the session schema. Take the first the role can create a Semantic View in, and say why |

3. **Ask one ask_user_question** confirming baseline scope and deployment
   `DATABASE.SCHEMA`, showing the proposed baseline and its gaps. Add only
   context that matters.
   - Propose only the worksheets or metrics on the baseline page, not every
     object in a shared model. Keep their supporting tables, dependent
     measures, and join keys.
   - If you can't tell which model objects a page uses, ask.
4. **Keep destination and sources apart.** The deployment schema is where the
   view goes. Keep each original source FQN, record a remap only if the user
   confirms the source moved, and never pass the deployment schema as an
   exporter remap.
5. **Treat visible filter selections as test context**, not permanent agent
   defaults. Expected results may stay pending while you build; Step 5 can't
   claim parity until they arrive.

---

## Ready for Step 3 when

- The baseline record has confirmed scope and destination.
- Usable files are staged and analyzed, or a fallback is chosen. Each missing
  piece has a next action.
- Required definitions and expected results are captured or marked missing.

Then apply the router in `02-build/SKILL.md`.
