---
name: semantic-layer-discovery
description: "Guide a customer from one dashboard whose data is in Snowflake to a validated Semantic View and Cortex Agent with minimal repeated discovery. Use for semantic-layer discovery, building a semantic view with a customer, replacing a dashboard with an agent, or choosing Power BI/Tableau import vs. Autopilot. Requests model-owning artifacts and baseline evidence, routes on content readiness, reconciles required coverage, and validates before sharing. Delegates implementation to agent-studio and optionally builds the customer's chosen front end over the validated scope."
---

# Semantic Layer Discovery

## When to Use

Use this skill to take a customer from "we have dashboards" to a validated
Semantic View wired to a Cortex Agent. The dashboard's data must be in
Snowflake; the BI file need not connect to it directly.

Triggers: *semantic layer discovery, semantic model discovery, enable a semantic
layer, walk me through semantic setup, sit with a customer on semantics, replace a
dashboard with an agent, agentic BI path, build a semantic view with a customer.*

## What this skill does

It sets the order and the inputs. The **`agent-studio`** skill does the work:
its `import_tableau`, `import_powerbi`, and `creation` workflows build the
Semantic View, and it creates the agent.

## The six steps (plus an optional Step 0)

| Step | What happens | File |
|---|---|---|
| 0 (optional) | Run **Cortex Sense** (PuPr Nov 2026) to surface naming conflicts, metric gaps, and coverage issues | `01-intake/SKILL.md` |
| 1 | Get the dashboard's files and a baseline; check where the data lives; stage | `01-intake/SKILL.md` |
| 2 | Analyze, fix missing pieces, confirm scope and destination | `01-intake/SKILL.md` |
| 3 | Build the Semantic View (import or Autopilot), then check coverage | `02-build/SKILL.md` |
| 4 | Create a test agent on it | `03-agent/SKILL.md` |
| 5 | Validate against the baseline, add Verified Queries, accept, share | `04-validate/SKILL.md` |
| 6 | Ask what to build (Streamlit, App Runtime, Dashboard, or not now), then build it | `05-app/SKILL.md` |

Read each file when you reach its step. Edge cases and the reasons behind the
rules are in `reference/rules.md`; read it when a step points there.

## How to work

1. **Read before you ask.** Inspect any supplied files first. Ask only for what
   changes the next step.
2. **Ask in batches.** One request for files, one pre-filled confirmation of
   scope and destination. Group any later gaps into one question.
3. **Carry answers forward.** Pass the baseline record, analyze results, and
   approvals into agent-studio. Its own required checks and approvals still
   run; never claim a parameter skips them. Never re-ask a settled question.
4. **Never guess.** Keep exact BI formulas and their context. Ask before
   building logic the importer could not convert. Missing SQL is not a missing
   definition.
5. **Save progress in the working project**, not the skill folder: the baseline
   record and coverage table. When new evidence arrives, resume at the blocked step.
6. **Route on content, not file type.** A supported extension doesn't prove the
   model is there or that its calculations will convert. Use the router in
   `02-build/SKILL.md`. Recover a missing piece without restarting intake; keep
   finished work.
7. **One baseline first.** Finish and validate it before taking on more.

A typical run asks the user 5–7 times: files, scope, a published-source file if
needed, agent-studio's deploy approvals, acceptance, and the Step 6 choice.

## Done means

1. A Semantic View exists (imported, built, or approved for reuse), confirmed
   with `SHOW SEMANTIC VIEWS` / `DESCRIBE SEMANTIC VIEW`.
2. A Cortex Agent exists and uses that view.
3. The agent passed validation against the agreed baseline, has Verified
   Queries, and is shared with named roles. The record says whether this is
   dashboard parity or reference validation, and lists any exclusions.
4. The customer chose a Step 6 option and it exists, shows the baseline KPIs
   from the Semantic View (plus agent chat for the apps), and has access
   granted; or the record shows they declined.

If a definition, source, baseline, or approval is missing, save progress and
report the exact blocker. Never report success you don't have. An approved
subset is a partial delivery, not a dashboard replacement.
