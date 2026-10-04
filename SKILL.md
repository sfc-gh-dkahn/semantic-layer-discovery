---
name: semantic-layer-discovery
description: "Guide a customer from one dashboard whose data is in Snowflake to a validated Semantic View and Cortex Agent with minimal repeated discovery. Use for semantic-layer discovery, building a semantic view with a customer, replacing a dashboard with an agent, or choosing Power BI/Tableau import vs. Autopilot. Requests model-owning artifacts and baseline evidence, routes on content readiness, reconciles required coverage, and validates before sharing. Delegates implementation to agent-studio and optionally builds the customer's chosen front end over the validated scope."
---

# Semantic Layer Discovery

## When to Use

Load this skill when you are helping a customer go from "we have dashboards" to a
**governed, agentic BI experience** — a validated Semantic View wired to a Cortex
Agent. The dashboard's data must be in Snowflake; the BI file need not connect
to it directly. It front-loads artifact checks, then routes on usable definitions and
source mappings rather than the BI product or file extension alone.

Triggers: *semantic layer discovery, semantic model discovery, enable a semantic
layer, walk me through semantic setup, sit with a customer on semantics, replace a
dashboard with an agent, agentic BI path, build a semantic view with a customer.*

## What this skill is

An **orchestrator**, not a re-implementation. It sequences the customer through
the six-step "Path Forward" and, for the mechanical work of creating the semantic
view (importing Power BI/Tableau or building from metadata), it hands off to the
existing **`agent-studio`** skill.

## The Path Forward — six steps (plus an optional pre-step)

```
Step 0 (optional, Cortex Sense — Public Preview Nov 2026)
  Run Cortex Sense first to surface naming conflicts, metric gaps, and coverage
  issues from Snowflake metadata, query history, dbt, Tableau, and Power BI —
  BEFORE building Semantic Views.

Step 1  Request owning artifacts + ONE dashboard baseline   -> 01-intake/SKILL.md
Step 2  Analyze, resolve dependencies, confirm scope         -> 01-intake/SKILL.md
Step 3  Build and reconcile required metric coverage         -> 02-build/SKILL.md
          Import usable definitions; recover missing dependencies first
          Build from metadata when no usable model is available
Step 4  Create a test agent on the candidate view            -> 03-agent/SKILL.md
Step 5  Validate parity, add VQRs, accept and ship             -> 04-validate/SKILL.md
Step 6  (opt-in) ASK: Streamlit app, App Runtime app, or Dashboard (PrPr) -> 05-app/SKILL.md
```

## Routing

Use the content-based decision table in `02-build/SKILL.md` after intake.
Prefer importing usable definitions; a supported extension alone does not prove
the model is present or the required calculations will convert. Recover missing
dependencies without restarting intake. Preserve partial results on fallback.

## Completion criteria

1. A **Semantic View object exists** in Snowflake (created via import or
   Autopilot, or verified for reuse in Step 3) — verifiable with
   `SHOW SEMANTIC VIEWS` / `DESCRIBE SEMANTIC VIEW`.
2. A **Cortex Agent exists** and is wired to that view (Step 4).
3. The agent has been **validated** against the agreed baseline and **surfaced**
   (CoWork or an app), with Verified Queries added (Step 5). Record whether this
   proves dashboard parity or reference-query correctness, and any accepted exclusions.
4. The customer was **asked what to build** (Streamlit app, App Runtime app,
   Dashboard (Private Preview), or not now). If they chose one, it **exists** and shows the
   baseline KPIs from the Semantic View (plus an agent chat for the two app
   options), with access granted to the customer's role(s) (Step 6). If not,
   record that it was declined.

Continue through creation when inputs and approvals allow it. If a required
definition, source, baseline, or approval is unavailable, save progress and report
the specific blocker; do not fabricate success to satisfy this definition of done.
A user-approved subset is a partial delivery, not replacement of the full dashboard.

## How to run this skill

### Interaction rule (REQUIRED) — fewest touches

Extract first; ask only for missing information that materially affects the next step.
- Use the artifact request in intake, then one pre-filled scope/destination
  confirmation. Consolidate dependency or definition gaps rather than asking piecemeal.
- If files are already supplied, inspect them before requesting replacements.
- Pass the baseline record, analyze results, and prior approvals into delegated
  skills. Reuse them where supported; do not promise that parameters bypass a
  sub-skill's mandatory checks or approvals. Do not repeat resolved questions.
- **Never guess.** Missing source SQL is not the same as a missing definition.
  Preserve exact BI formulas and context; ask before implementing unsupported logic.
- Save the baseline record and coverage status in the working project, not in
  the installed skill. Resume at the blocked step when new evidence arrives.

1. Read `01-intake/SKILL.md` and run Steps 1-2: get,
   stage, and analyze the file.
2. At Step 3, read and apply the routing rule in `02-build/SKILL.md`.
3. Continue through `03-agent/SKILL.md` (Step 4), `04-validate/SKILL.md` (Step 5), and
   `05-app/SKILL.md` (Step 6).
4. For the actual semantic-view import or build, delegate to the `agent-studio`
   skill (its `import_tableau`, `import_powerbi`, and `creation` workflows).
5. For the Step 6 build, delegate to the skill for the chosen option and the
   user's surface (Desktop/CLI vs Snowsight) — see the table in `05-app/SKILL.md`.

## Guiding principle

Complete and validate one baseline before expanding scope.
