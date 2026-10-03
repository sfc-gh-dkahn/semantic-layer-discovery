---
name: semantic-layer-discovery
description: "Guide a customer end-to-end through evaluating and standing up a governed, agentic BI experience on Snowflake, following the 'Quick to Evaluate, Even Quicker to Production' path. Use when a user wants to: run semantic-layer discovery, walk a customer through building a semantic layer/semantic view, replace or modernize an existing dashboard/report with a Cortex Agent, or decide whether to import Power BI/Tableau vs. build from scratch. Ends by building the customer's choice of front end (Streamlit app, App Runtime app, or Dashboard in CoWork (PrPr)) over the validated semantic view and agent. Detects Snowsight vs Desktop/CLI, has the user upload the Tableau/Power BI file to a stage with the right tool, and analyzes it with agent-studio's built-in tools; with no file it routes to Autopilot/build-from-scratch. Delegates the actual semantic-view import/build mechanics to the 'agent-studio' skill."
---

# Semantic Layer Discovery

## When to Use

Load this skill when you are helping a customer go from "we have dashboards" to a
**governed, agentic BI experience** — a certified Semantic View wired to a Cortex
Agent. It front-loads discovery, then routes to the correct build path depending
on whether the customer already has Power BI or Tableau.

Triggers: *semantic layer discovery, semantic model discovery, enable a semantic
layer, walk me through semantic setup, sit with a customer on semantics, replace a
dashboard with an agent, agentic BI path, build a semantic view with a customer.*

## What this skill is

An **orchestrator**, not a re-implementation. It sequences the customer through
the five-step "Path Forward" and, for the mechanical work of creating the semantic
view (importing Power BI/Tableau or building from metadata), it hands off to the
existing **`agent-studio`** skill.

## The Path Forward — six steps (plus an optional pre-step)

```
Step 0 (optional, Cortex Sense — Public Preview Nov 2026)
  Run Cortex Sense first to surface naming conflicts, metric gaps, and coverage
  issues from Snowflake metadata, query history, dbt, Tableau, and Power BI —
  BEFORE building Semantic Views.

Step 1  Detect the surface (Snowsight vs Desktop/CLI)     -> discovery/SKILL.md
Step 2  Upload + stage the file, analyze it with agent-studio's
        Tableau / Power BI tools, confirm tabs + schema      -> discovery/SKILL.md
Step 3  Create the Semantic View                            -> build/SKILL.md
          ├─ HAS a Power BI / Tableau file -> build/import.md
          └─ answered `none`               -> build/autopilot.md
Step 4  Create a Cortex Agent on the certified view         -> agent/SKILL.md
Step 5  Validate against the baseline, add VQRs, ship        -> validate/SKILL.md
Step 6  (opt-in) ASK: Streamlit app, App Runtime app, or Dashboard (PrPr) -> app/SKILL.md
```

## The routing rule (no question)

The file from **Step 2** decides the route — don't ask "Do you have Power BI or
Tableau?":

- **Power BI** (`.pbit` / `.pbix`) -> `build/import.md` (Power BI path)
- **Tableau** (`.twb` / `.twbx` / `.tds` / `.tdsx`) -> `build/import.md` (Tableau path)
- **`none`** -> `build/autopilot.md` (build from metadata / Autopilot)

Importing carries **DAX measures, relationships, and calculations directly in**,
so if the customer has a BI tool, prefer import — it reflects already-validated
business definitions and is faster than starting cold.

## Deliverables — Definition of Done (this is a SETUP skill, not just discovery)

This skill is not complete until **real Snowflake objects exist**. Discovery
(Steps 1-2) is only the front half; the run is done only when ALL of these are
true:

1. A **Semantic View object exists** in Snowflake (created via import or
   Autopilot in Step 3) — verifiable with `SHOW SEMANTIC VIEWS` / `DESCRIBE
   SEMANTIC VIEW`.
2. A **Cortex Agent exists** and is wired to that certified view (Step 4).
3. The agent has been **validated** against the baseline dashboard's questions
   and **surfaced** (CoWork or an app), with Verified Queries
   added (Step 5).
4. The customer was **asked what to build** (Streamlit app, App Runtime app,
   Dashboard (Private Preview), or not now). If they chose one, it **exists** and shows the
   baseline KPIs from the Semantic View (plus an agent chat for the two app
   options), with access granted to the customer's role(s) (Step 6). If not,
   record that it was declined.

If you finish the conversation without creating these objects, the skill has
**failed** — you produced discovery notes, not a semantic layer. Do not stop at
Step 2.

## How to run this skill

### Interaction rule (REQUIRED) — fewest touches

The file answers most questions, so don't ask them. You MUST:
- Ask only for the file (Step 2), one pre-filled confirm (tabs + schema), and the
  Step 6 build choice. Anything else is a **fix**, asked only when something is
  wrong.
- Never ask for business context, metric definitions, consumers, or "do you
  have Power BI or Tableau?" — read them from the file.
- When you need more than one input, ask for all of them in **one**
  ask_user_question call, with every answer pre-filled.
- Pass every value into agent-studio's tools yourself so it never stops to ask.

1. Read `discovery/SKILL.md` and run Steps 1-2: detect the surface, then get,
   stage, and analyze the file.
2. At Step 3, apply the routing rule above and read `build/SKILL.md`.
3. Continue through `agent/SKILL.md` (Step 4), `validate/SKILL.md` (Step 5), and
   `app/SKILL.md` (Step 6).
4. For the actual semantic-view import or build, delegate to the `agent-studio`
   skill (its `import_tableau`, `import_powerbi`, and `creation` workflows).
5. For the Step 6 build, delegate to the skill for the chosen option and the
   user's surface (Desktop/CLI vs Snowsight) — see the table in `app/SKILL.md`.

## Guiding principle

**One dashboard replaced is the fastest proof point for broader adoption.** Keep
the customer anchored on a single, trusted baseline all the way through Step 5 —
resist scope creep until the first agent is validated and shipped.
