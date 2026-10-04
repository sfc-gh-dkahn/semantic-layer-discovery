# Step 3: Build the Semantic View

Turn the confirmed baseline into a Semantic View, then check that every
required metric made it. The file's contents decide the route; coverage decides
whether the view is ready for an agent.

---

## 3a. Pick the route

| What intake found | Route | Next action |
|---|---|---|
| Usable Tableau workbook/source or model-owning Power BI file; sources resolved | `02-build/import.md` | Import the selected scope, then the gate |
| Missing published-source file, thin report, or unresolved required source | Intake 2b | Recover that piece; keep finished work |
| Usable definitions, but required calculations won't convert | `02-build/import.md`, then the gate | Implement from the exact definitions with approval; don't try another file format |
| Required tables not connected to Snowflake in the file, but confirmed in Snowflake (intake 1b-3) | `02-build/autopilot.md` for those tables | Build on the confirmed objects; carry over the file's formulas and page context |
| No usable file, or an agreed metadata fallback | `02-build/autopilot.md` | Carry the baseline and any kept definitions; don't restart discovery |

- Prefer import when it keeps business definitions. A source-only Tableau file
  is still worth importing.
- A staged Tableau sidecar is used at export. Analyze doesn't merge it, so don't
  wait for a re-analyzed workbook to show the relations.
- If a required piece can't be supplied, agree on a fallback, a smaller scope,
  or a pause before going on.

## 3b. Create it through agent-studio (REQUIRED)

Invoke the **`agent-studio`** skill and let it create a real object; don't
describe one:
- Import: its `import_tableau` / `import_powerbi` workflows.
- Metadata build: its `creation` workflow (Autopilot / fastgen).
- Approved reuse of an existing view: inspect it through agent-studio and run
  the gate below. Don't create a duplicate just to finish a step.

Deploy only after the 3c gate passes (the import and Autopilot files show the
order). Keep agent-studio's approval gates, including custom-view DDL and deployment.
Step 3 is done only when `SHOW SEMANTIC VIEWS` / `DESCRIBE SEMANTIC VIEW`
confirms the object; an export or saved YAML is not a deployed view. If an
approval or input is missing, report a blocked run and its next action.

## 3c. Required coverage gate (both routes, before the agent)

Check the candidate against the baseline record **metric by metric**, not by
totals. For each required metric, record its definition source, target
expression, dependencies, and status:

| Status | Action |
|---|---|
| Converted or implemented, sources resolved | Review grain, joins, filters, and dependencies; queue for Step 5 |
| Definition found, translation unsupported | Keep the exact DAX/Tableau formula and its context. Explain the limit; ask approval to implement it in SQL through agent-studio, or to exclude it |
| Definition or dependency missing | Ask for the specific formula, context, or source; or accept a smaller scope; or pause. Never infer a formula from a name |

1. Read errors and warnings. Look for missing columns, filters, and
   relationships, not just measures. A metric whose required dependency was
   dropped is blocked, even if its name survived.
2. Use query history to support recovery, never as proof on its own. Check any
   candidate SQL against the definition, sources, grain, and filters
   (`reference/rules.md` § Query history).
3. **Pass only when** the approved scope has at least one answerable baseline
   question and all its required metrics are implemented with dependencies
   resolved. An empty export fails.
4. If the user accepts a subset, keep the original metric list and record each
   exclusion. "Unsupported" means "needs approved work", never "approximate it".
5. Re-run the gate after every fix.

## 3d. Before Step 4

- The gate passes for the approved scope and the object exists.
- Add descriptions and synonyms in the business's own words.
- Carry the baseline record, coverage table, and exclusions forward.
- Don't certify yet; Step 5 validates first.

Then go to `03-agent/SKILL.md`.
