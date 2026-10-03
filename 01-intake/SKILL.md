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

## Step 1 — Detect the surface (no question)

```bash
echo "surface=${CORTEX_CODE_CLIENT_SURFACE:-unknown} os=$(uname -s)"; test -d /workspace && echo cloud_mount
```

| Result | Surface | Staging tool |
|---|---|---|
| `coco_desktop` / `coco_cli`, or `Darwin`/Windows with no `/workspace` | Desktop / CLI | `PUT file://` |
| `coco_snowsight`, or Linux with `/workspace` | Snowsight | `COPY FILES FROM snow://workspace` |
| Still unclear | Ask once | — |

---

## Step 2 — Get, stage, and analyze ONE baseline file

### 2a. Ask for the file (one question)

| Surface | Ask |
|---|---|
| Desktop / CLI | "Path to your Tableau or Power BI file? (or `none`)" |
| Snowsight | "Upload your Tableau or Power BI file into this workspace, then say `done`. (or `none`)" |

- `none` -> skip to `02-build/autopilot.md`.
- Snowsight: find the file yourself (`find /workspace -maxdepth 4 -type f \( -iname '*.twb*' -o -iname '*.tds*' -o -iname '*.pbi[tx]' \) -mmin -60`).
- One dashboard only — do not bulk-import the BI estate.
- File name has `[` or `]`: stage downloads fail. Rename it (Desktop) or ask the
  user to rename it (Snowsight).

### 2b. Stage it (no question)

agent-studio's tools only take stage paths, so stage first, in the session's
current database and schema:

```sql
CREATE STAGE IF NOT EXISTS <DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE
  DIRECTORY = (ENABLE = TRUE) ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');
-- Desktop / CLI
PUT 'file://<abs path>' @<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- Snowsight
COPY FILES INTO @<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE
  FROM 'snow://workspace/<workspace>/versions/live/<path>' FILES = ('<file>');
LIST @<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE;
```

Never use `cortex ws cp` to reach a stage — it copies to the sandbox and still
reports success. File missing after one retry: give the clicks *Data » Databases
» <DB> » <SCHEMA> » Stages » SEMANTIC_IMPORT_STAGE » + Files*.

### 2c. Analyze it (no question)

Use agent-studio's built-in tools. Read its
`semantic-view/reference/tableau_tool_reference.md` (or `pbi_tool_reference.md`)
first for exact parameter names.

```bash
cortex agent-studio backend --tool tableau_analyze --parameters '{"file_path":"@<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE/<file>"}'
cortex agent-studio backend --tool pbi_analyze --parameters '{"file_path":"@<DB>.<SCHEMA>.SEMANTIC_IMPORT_STAGE/<file>","validate_in_snowflake":true}'
```

No `cortex` CLI? `SELECT SYSTEM$CORTEX_ANALYST_SVA_TOOL('<tool>', '<params json>');`

Take from it: worksheets (Tableau) or tables (Power BI), `has_custom_sql`,
non-Snowflake sources (`m_query_warnings`), and missing tables
(`validation_warnings`).

### 2d. Fix only what's broken

| Sign | Action |
|---|---|
| Tableau published data source (`relation_count: 0`) | Ask for that source as `.tdsx`; stage and analyze it too. |
| Power BI "does not contain a data model" | Ask for the model's `.pbix` or a `.pbit`. |
| CSV / Excel / extract sources | Find the Snowflake tables behind the columns (`snowflake_object_search`, `INFORMATION_SCHEMA.COLUMNS`, query history). If it lands on an existing Semantic View, offer to reuse it. |

### 2e. One confirm, pre-filled

One ask_user_question call with two questions: **tabs/tables** (all
pre-selected) and **target `DATABASE.SCHEMA`** (default: the source tables'
schema). Put one line above it with what you found.

---

## Exit criteria for discovery

Before moving to Step 3, you should have:
- One staged baseline file (or `none`).
- Its analyze result: tabs/tables, source tables, any fixes made.
- The confirmed tabs and target schema.

Then proceed to `02-build/SKILL.md` and apply the routing rule.
