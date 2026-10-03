# Step 3: Create the Semantic View (the branch point)

This is the one decision point in the whole workflow. Model the tables,
relationships, metrics, and descriptions from Step 2 into a **Semantic View** —
but *how* you create it depends on the file from Step 2.

---

## The route (no question — the Step 2 file decides)

| File | Route to | Why |
|---|---|---|
| **Power BI** (`.pbit` / `.pbix`) | `build/import.md` → Power BI path | DAX measures, relationships, calcs carry directly in |
| **Tableau** (`.twb` / `.twbx` / `.tds` / `.tdsx`) | `build/import.md` → Tableau path | Datasource joins, calcs, and fields carry in |
| **`none`** | `build/autopilot.md` | Build fresh from Snowflake metadata via Autopilot |

**Prefer import when a BI tool exists.** The workbook already encodes
business-validated definitions, so importing is faster and more trustworthy than
rebuilding from scratch — and it maps directly to the baseline file from Step 2.

---

## After the branch

Both paths produce a **Semantic View** (GA). Once it exists:
- Confirm the dashboard's key metrics are present (check import warnings for
  dropped ones).
- Add descriptions and synonyms so Cortex Analyst understands business language.
- Mark/treat the view as **certified** — Step 4 wires the agent to a certified view.

Then proceed to `agent/SKILL.md` (Step 4).

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
