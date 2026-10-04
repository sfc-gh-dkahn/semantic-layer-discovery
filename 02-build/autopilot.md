# Step 3 — Autopilot path (screenshots from another BI tool, or no file)

Use this when there's no Tableau or Power BI file to import. Build the Semantic
View from Snowflake metadata with **Autopilot**: screenshots tell you *which*
metrics matter; query history tells you *how* they're calculated.

---

## Inputs

- **Dashboard screenshots**, if pasted (Domo, Hex, Looker, Sigma, any BI tool).
  Read them from the chat, not as a file in `/workspace`. Take the KPI names,
  chart titles, grouping fields, filters, date range, and numbers shown. These
  are the metric list, the agent's questions, and the Step 5 baseline.
- The **source tables**: search with the KPI and field names from the
  screenshots (`snowflake_object_search`, `snowflake_semantic_view_search`,
  busiest tables in query history). An existing semantic view on them: offer
  to reuse it.
- The **top queries** on those tables in query history, including the BI
  tool's service user if it queries Snowflake live. These hold the metric SQL.

Confirm the tables and target schema in one pre-filled question. Default the
schema to where the tables live (see `01-intake/SKILL.md` 2c).

## How to run it

Delegate to the **`agent-studio`** skill. "Autopilot" is the Snowsight name;
in agent-studio it is the **`creation`** workflow (`sv-generate`):
1. Pass the source tables **and** the top queries (as `sqlSource`, each with its
   question). `creation` reads only column metadata plus the SQL you pass, so
   the queries are where the business logic comes from. Then run agent-studio's
   `suggest_relationships`, `filters_and_metrics_suggestions`, and
   `generate_description` with no questions, and deploy with `upload`.
2. Check each screenshot metric against the view, following
   `02-build/SKILL.md` » Metrics: traced SQL goes in; anything without SQL goes
   on the "couldn't find" list for the user. Then:
   - Confirm relationships and fact grain against the queries' joins.
   - Take care with non-additive metrics (ratios, distinct counts, averages).
   - Add named filters for the filters shown on screen.
   - Add descriptions + synonyms using the dashboard's labels.
3. Turn the top queries into **Verified Queries (VQRs)**. Step 5 tests them.

## Why questions-first matters

Building for the dashboard's few real questions, not every column, keeps the
view scoped and gives Step 5 a clear accuracy target. Expand only after Step 5
proves the baseline.

## Exit criteria

- Semantic View created.
- Every screenshot metric is in the view with traced SQL, or on the "couldn't
  find" list shown to the user.
- Initial VQRs drafted from the top queries.
- Descriptions/synonyms added; view treated as certified.

Return to `02-build/SKILL.md` "After the branch", then continue to `03-agent/SKILL.md`.
