# Step 3: Create the Semantic View (the branch point)

This is the one decision point in the whole workflow. Model the tables,
relationships, metrics, and descriptions from Step 2 into a **Semantic View** —
but *how* you create it depends on the file from Step 1.

---

## The route (no question — the Step 1 file decides)

| File | Route to | Why |
|---|---|---|
| **Power BI** (`.pbit` / `.pbix`) | `02-build/import.md` → Power BI path | DAX measures, relationships, calcs carry directly in |
| **Tableau** (`.twb` / `.twbx` / `.tds` / `.tdsx`) | `02-build/import.md` → Tableau path | Datasource joins, calcs, and fields carry in |
| **Screenshots (any other BI tool) or `none`** | `02-build/autopilot.md` | Build fresh from Snowflake metadata via Autopilot |

**Prefer import when a BI tool exists.** The workbook already encodes
business-validated definitions, so importing is faster and more trustworthy than
rebuilding from scratch — and it maps directly to the baseline you chose in Step 1.

---

## Metrics: find each one, trace its SQL, or say you can't (both paths)

Every metric on the dashboard needs a Snowflake SQL definition in the view.

1. **List the metrics.** Take them from the file (measures, calculated fields)
   and from screenshots (KPI tiles, chart values). This list is the target.
2. **Find each one's SQL**, in this order:
   - **The file.** DAX measures and Tableau calcs that import transpiles.
   - **Query history.** BI tools that query Snowflake live (Tableau live
     connections, Power BI DirectQuery, Domo, Hex, Sigma, ...) push their calcs
     down as SQL. Find the BI service user's queries on the source tables and
     read the expression behind each metric (`SUM(...) / NULLIF(...)`,
     `COUNT(DISTINCT ...)`, `CASE WHEN ...`).
   - Match on the metric name, column alias, or the numbers in the screenshot.
3. **Can't find it? Say so; don't guess.** A calc can stay inside the BI tool:
   import extracts, Power BI import mode, DAX that doesn't transpile, or table
   calcs (running totals, rank, % of total) computed after the query. Then no
   SQL exists in the file or query history. Leave it out of the view and list
   it for the user:

   > Couldn't find Snowflake SQL for: **Margin %**, **YoY Growth**. These run
   > inside Power BI, not Snowflake. Add them to the semantic view yourself
   > (or give me the SQL and I'll add them); I'll validate them in Step 5.

   Never write a formula from the metric's name, or fill one in from a
   "standard" definition.

## After the branch

Both paths produce a **Semantic View** (GA). Once it exists:
- Every dashboard metric is either in the view with its traced SQL, or on the
  "couldn't find" list shown to the user.
- Add descriptions and synonyms so Cortex Analyst understands business language.
- Mark/treat the view as **certified** — Step 4 wires the agent to a certified view.

Then proceed to `03-agent/SKILL.md` (Step 4).

## Delegation (REQUIRED — actually create the object, do not narrate)

You **MUST** invoke the **`agent-studio`** skill and let it run the real
creation — this step produces an actual Semantic View object in Snowflake, not a
description of how one would be made:
- Power BI / Tableau import → its `import_powerbi` / `import_tableau` workflows.
- Build from metadata → its `creation` workflow (Autopilot / fastgen).

Do **not** treat Step 3 as complete until a Semantic View object exists and you
have confirmed it (e.g. `SHOW SEMANTIC VIEWS` / `DESCRIBE SEMANTIC VIEW`).
Explaining the steps without invoking the sub-skill and creating the object is a
failure of this step. This skill orchestrates; `agent-studio` does the heavy
lifting — but the object must actually get built here.
