# Step 3: Create the Semantic View (the branch point)

This is the one decision point in the whole workflow. Model the tables,
relationships, metrics, and descriptions from Step 2 into a **Semantic View** —
but *how* you create it depends on whether the customer already has a BI tool.

---

## The routing question

Ask the customer directly (use the ask_user_question tool):

> Do you already have Power BI or Tableau in your environment?

| Answer | Route to | Why |
|---|---|---|
| **Power BI** (`.pbit` / `.pbix`) | `build/import.md` → Power BI path | DAX measures, relationships, calcs carry directly in |
| **Tableau** (`.twb` / `.twbx` / `.tds` / `.tdsx`) | `build/import.md` → Tableau path | Datasource joins, calcs, and fields carry in |
| **Both** | `build/import.md` | Import the tool that owns the Step 1 baseline dashboard first |
| **Neither** | `build/autopilot.md` | Build fresh from Snowflake metadata via Autopilot |

**Prefer import when a BI tool exists.** The workbook already encodes
business-validated definitions, so importing is faster and more trustworthy than
rebuilding from scratch — and it maps directly to the baseline you chose in Step 1.

---

## After the branch

Both paths produce a **Semantic View** (GA). Once it exists:
- Confirm the key metrics from Step 2c are present and defined correctly.
- Add descriptions and synonyms so Cortex Analyst understands business language.
- Mark/treat the view as **certified** — Step 4 wires the agent to a certified view.

Then proceed to `agent/SKILL.md` (Step 4).

## Delegation

For the actual conversion/build mechanics, hand off to the **`agent-studio`**
skill:
- Power BI / Tableau import → its `import_powerbi` / `import_tableau` workflows.
- Build from metadata → its `creation` workflow (Autopilot / fastgen).

This skill orchestrates; `agent-studio` does the heavy lifting.
