---
name: semantic-layer-discovery
description: "Guide a customer end-to-end through evaluating and standing up a governed, agentic BI experience on Snowflake, following the 'Quick to Evaluate, Even Quicker to Production' path. Use when a user wants to: run semantic-layer discovery, walk a customer through building a semantic layer/semantic view, replace or modernize an existing dashboard/report with a Cortex Agent, or decide whether to import Power BI/Tableau vs. build from scratch. Runs discovery questions, then branches at the Create-Semantic-View step: if the customer HAS Power BI or Tableau it routes to import; if they have NEITHER it routes to Autopilot/build-from-scratch. Delegates the actual semantic-view import/build mechanics to the 'agent-studio' skill."
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

## The Path Forward — five steps (plus an optional pre-step)

```
Step 0 (optional, Cortex Sense — Public Preview Nov 2026)
  Run Cortex Sense first to surface naming conflicts, metric gaps, and coverage
  issues from Snowflake metadata, query history, dbt, Tableau, and Power BI —
  BEFORE building Semantic Views.

Step 1  Choose ONE existing dashboard, report, or KPI set   -> discovery/SKILL.md
Step 2  Map data objects, questions, business definitions   -> discovery/SKILL.md
Step 3  Create the Semantic View                            -> build/SKILL.md
          ├─ HAS Power BI / Tableau  -> build/import.md
          └─ has NEITHER             -> build/autopilot.md
Step 4  Create a Cortex Agent on the certified view         -> agent/SKILL.md
Step 5  Validate against the baseline, add VQRs, ship        -> validate/SKILL.md
```

## The routing rule (the one decision point)

At **Step 3**, ask the customer directly (use the ask_user_question tool):

> Do you already have Power BI or Tableau in your environment?

- **Has Power BI** (`.pbit` / `.pbix`) -> `build/import.md` (Power BI path)
- **Has Tableau** (`.twb` / `.twbx` / `.tds` / `.tdsx`) -> `build/import.md` (Tableau path)
- **Has both** -> ask which dashboard from Step 1 to prioritize; import that one first
- **Has neither** -> `build/autopilot.md` (build from metadata / Autopilot)

Importing carries **DAX measures, relationships, and calculations directly in**,
so if the customer has a BI tool, prefer import — it reflects already-validated
business definitions and is faster than starting cold.

## How to run this skill

### Interaction rule (REQUIRED) — one question at a time

This is a **live, guided customer conversation**, not a form. You MUST:
- Ask **exactly one question at a time** using the ask_user_question tool, and
  **wait for the customer's answer** before asking the next.
- **Never** batch or dump multiple questions in a single message, and never
  pre-fill or assume the customer's answers.
- Briefly acknowledge/reflect each answer before the next question, so the
  customer feels heard and can correct you.
- Only advance to the next step once the current step's questions are answered.
- If an answer is vague, ask a short follow-up (still one at a time) rather than
  guessing.

Treat the question lists in each sub-skill as an ordered script to ask
sequentially — not as a checklist to present all at once.

1. Read `discovery/SKILL.md` and run Steps 1-2 with the customer, one question at a time.
2. At Step 3, apply the routing rule above and read `build/SKILL.md`.
3. Continue through `agent/SKILL.md` (Step 4) and `validate/SKILL.md` (Step 5).
4. For the actual semantic-view import or build, delegate to the `agent-studio`
   skill (its `import_tableau`, `import_powerbi`, and `creation` workflows).

## Guiding principle

**One dashboard replaced is the fastest proof point for broader adoption.** Keep
the customer anchored on a single, trusted baseline all the way through Step 5 —
resist scope creep until the first agent is validated and shipped.
