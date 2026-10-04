# Steps 1-2: Discovery

This covers the first two steps of the Path Forward: detect where the user is
working, then get the baseline file into a stage and let agent-studio's
Tableau / Power BI tools read it. The file answers the discovery questions —
metrics, filters, tables, joins — so don't ask them.

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

### 1b. Ask for the file (one question)

| Surface | Ask |
|---|---|
| Desktop / CLI | "Path to your Tableau or Power BI file? Using another BI tool (Domo, Hex, ...)? Paste dashboard screenshots instead. (or `none`)" |
| Snowsight | "Upload your Tableau or Power BI file into this workspace, then say `done`. Using another BI tool (Domo, Hex, ...)? Paste dashboard screenshots instead. (or `none`)" |

- Screenshots or `none` -> skip to `02-build/autopilot.md`.
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

The analyze tools read these from the file; don't ask for them.

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

Take from it: worksheets (Tableau) or tables (Power BI), `has_custom_sql`,
non-Snowflake sources (`m_query_warnings`), missing tables
(`validation_warnings`), and calcs it can't convert (`warnings`;
Power BI also `unsupported_measure_count`). Those calcs start the "couldn't
find" list (`02-build/SKILL.md` » Metrics).

### 2b. Fix only what's broken

| Sign | Action |
|---|---|
| Tableau published data source (`relation_count: 0`) | Ask for that source as `.tdsx` (Tableau Cloud/Server: download the data source); stage it and pass it as `additional_files`. Several sources: also set `published_datasource_stub_name`. |
| The `.tds`/`.tdsx` is itself only a server pointer | No documented fix. Tell the user plainly: the file holds no Snowflake connection, so the tables can't be read from it. Then find them through query history or `snowflake_object_search` and confirm the match with the user, or go to the Autopilot path. |
| Power BI "does not contain a data model" | Ask for the model's `.pbix` or a `.pbit`. |
| CSV / Excel / extract sources | Find the Snowflake tables behind the columns (`snowflake_object_search`, `INFORMATION_SCHEMA.COLUMNS`, query history). If it lands on an existing Semantic View, offer to reuse it. |

### 2c. One confirm, pre-filled

One ask_user_question call with two questions: **tabs/tables** (all
pre-selected) and **target `DATABASE.SCHEMA`**, pre-filled so the user can
just accept:

| Source tables live in | Default target |
|---|---|
| One schema | That schema |
| Several schemas | The schema holding the fact table(s) the dashboard reads most; tie: the most-queried table's schema |
| No write access there | First other choice the role can create in; say why |

Put one line above it with what you found, including anything the file can't
resolve (see 2b).

---

## Exit criteria for discovery

Before moving to Step 3, you should have:
- One staged baseline file (or screenshots, or `none`).
- Its analyze result: tabs/tables, source tables, any fixes made.
- The confirmed tabs and target schema.

Then proceed to `02-build/SKILL.md` and apply the routing rule.
