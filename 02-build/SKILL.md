# Step 3: Create the Semantic View (the branch point)

Model the confirmed baseline from Step 2 into a **Semantic View**. The artifact's
contents determine the route; the required metric coverage determines whether
the result is ready for an agent.

---

## The route (use the intake findings, not just the extension)

| Readiness | Route to | Next action |
|---|---|---|
| Usable Tableau workbook/source or model-owning Power BI artifact; source mappings resolved | `02-build/import.md` | Convert the selected scope, then reconcile coverage |
| Missing published-source sidecar, thin report, or unresolved required source | Intake 2b | Recover the specific dependency or mapping; keep completed work |
| Usable definitions but unsupported required calculations | Import supported scope, then the coverage gate below | Seek approved implementation from exact definitions, not another file-format loop |
| Required tables not connected to Snowflake in the file, but confirmed in Snowflake (intake 1b-3) | `02-build/autopilot.md` for those tables | Build on the confirmed objects; carry over the file's formulas and page context |
| No usable artifact available, or agreed metadata-based fallback | `02-build/autopilot.md` | Carry the baseline and any retained definitions into the build; do not start discovery over |

Prefer import when it preserves usable business definitions. Source-only Tableau
files do not need to be discarded for lack of worksheets. If a required dependency
cannot be supplied, agree fallback, reduced scope, or a pause before continuing.
A staged owning Tableau sidecar is ready to try at export; analyze does not merge
it, so do not wait for a re-analyzed workbook to show the merged relations.

---

## Required coverage gate (both paths, before agent creation)

After export/generation, compare the candidate to the baseline record by **named
required metric**, not just total counts. Record its definition source, target
expression, dependencies, and status:

| Status | Action |
|---|---|
| Converted/implemented with resolved sources | Review grain, joins, filters, and dependencies; queue result validation for Step 5 |
| Definition found, translation unsupported | Preserve the exact DAX/Tableau formula and evaluation context. Explain the limitation and ask approval for a separate SQL implementation through agent-studio, or explicit exclusion |
| Definition or dependency missing | Request the specific formula/context/source, accept an explicitly reduced scope, or pause; never infer a formula from a name |

Inspect errors/warnings and missing columns, filters, or relationships as well as
measures. Required dependencies dropped during filtering or validation block the
metric even if its name survives. Re-run the gate after remediation.

**Query history supports recovery; it is not universal formula recovery.** It may
contain refresh/extract-build SQL or only part of a DirectQuery computation.
Corroborate candidate SQL against the definition, source mapping, grain, and
filter context. A name, alias, or matching snapshot alone is insufficient. Missing
SQL does not prove the formula is missing or that it runs only inside the BI tool.

Proceed only when the **approved scope** contains at least one answerable baseline
question and all its required metrics have implementations and resolved dependencies.
An empty export does not pass. If the user accepts a subset, retain the original target
list and record exclusions explicitly. Unsupported does not mean unimplementable;
it also does not authorize an unreviewed approximation.

## After the branch

Both paths produce a **candidate Semantic View**. Before Step 4:
- Required coverage passes for the approved scope and the deployed object exists.
- Add descriptions and synonyms so Cortex Analyst understands business language.
- Carry the baseline record, coverage table, and exclusions into the agent step.
- Do not certify yet: Step 5 must validate and accept the results first.

Then proceed to `03-agent/SKILL.md` (Step 4).

## Delegation (REQUIRED — actually create the object, do not narrate)

You **MUST** invoke the **`agent-studio`** skill and let it run the real
creation — this step produces an actual Semantic View object in Snowflake, not a
description of how one would be made:
- Power BI / Tableau import → its `import_powerbi` / `import_tableau` workflows.
- Build from metadata → its `creation` workflow (Autopilot / fastgen).

If the user approved reusing an existing view, inspect it through agent-studio and
apply the same coverage gate; do not create a duplicate merely to complete a step.

Do **not** treat Step 3 as complete until a Semantic View object exists and you
have confirmed it (e.g. `SHOW SEMANTIC VIEWS` / `DESCRIBE SEMANTIC VIEW`).
An export or saved YAML alone is not a deployed view. Preserve delegated approval
gates, including custom-view DDL and deployment. If approval or a required input
is unavailable, report a blocked run and its next action, not a completed setup.
