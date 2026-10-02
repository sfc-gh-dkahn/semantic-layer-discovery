# Semantic Layer Discovery — Skill Guide

A Cortex Code skill that walks a customer, one question at a time, from "we have
dashboards" to a **governed, agentic BI experience**: a certified Semantic View
wired to a Cortex Agent. It follows the "Quick to Evaluate, Even Quicker to
Production" path and branches based on whether the customer already has Power BI
or Tableau.

---

## What it does

- Runs **discovery** against a single, trusted baseline dashboard.
- **Branches at Step 3**: if the customer has Power BI/Tableau it **imports** the
  workbook; if not, it builds from scratch with **Autopilot**.
- Wires a **Cortex Agent** to the certified view and **validates** it against the
  original dashboard, then ships it.
- **Builds a front end** over the validated view and agent — the customer picks a
  Streamlit app, App Runtime app, or Dashboard in CoWork (PrPr).
- Delegates the heavy lifting (import/build) to the installed **`agent-studio`**
  skill — this skill orchestrates *when* and *what*, not the mechanics.

## Who it's for

Sales engineers, solution architects, and data teams sitting with a customer to
stand up their first agentic BI use case — or anyone modernizing a trusted
dashboard into a conversational, governed agent.

## When it triggers

Phrases like: *semantic layer discovery, walk me through building a semantic
view with a customer, replace a dashboard with an agent, agentic BI path,
enable a semantic layer.*

---

## The six-step path

| Step | What happens | File |
|---|---|---|
| 0 (optional) | Run **Cortex Sense** (PuPr Nov 2026) to surface naming conflicts, metric gaps, coverage | `discovery/SKILL.md` |
| 1 | Choose **ONE** existing dashboard/report/KPI set as the baseline; **ask for a screenshot** of it | `discovery/SKILL.md` |
| 2 | Map data objects, questions, and business definitions | `discovery/SKILL.md` |
| 3 | **Create the Semantic View** — the branch point | `build/SKILL.md` |
| 3a | Has Power BI/Tableau → **import** the workbook | `build/import.md` |
| 3b | Has neither → **Autopilot** from metadata | `build/autopilot.md` |
| 4 | Wire a **Cortex Agent** on the certified view | `agent/SKILL.md` |
| 5 | **Validate** vs baseline, add Verified Queries, ship | `validate/SKILL.md` |
| 6 | **Ask** what to build — **Streamlit app**, **App Runtime app**, or **Dashboard** (Private Preview) — then build it | `app/SKILL.md` |

### The one decision point (Step 3)

> "Do you already have Power BI or Tableau?"

- **Power BI** (`.pbit`/`.pbix`) or **Tableau** (`.twb`/`.twbx`/`.tds`/`.tdsx`) → import path
- **Both** → import the tool that owns the baseline dashboard first
- **Neither** → Autopilot / build-from-metadata path

Importing carries DAX measures, relationships, and calculations directly in, so
prefer import when a BI tool exists.

---

## How to run it (facilitator notes)

1. Ask **one question at a time** and wait for the answer — this is a live
   conversation, not a form. Reflect each answer before moving on.
2. In Step 1, **request a screenshot** of the baseline dashboard — you're
   multimodal, so reading the real metrics/filters/layout accelerates the Step 2
   mapping (helpful, not required).
3. Keep the customer anchored on **one** baseline dashboard through Step 5.
   Resist scope creep until the first agent is validated and shipped.
4. At Step 3, apply the routing question and hand off to the `agent-studio`
   skill for the actual import (`import_powerbi` / `import_tableau`) or build
   (`creation` / Autopilot).
5. **Identity/reference-data is a separate track.** Importing a dashboard gives
   you the model; it does NOT reconcile the same entity appearing under different
   names/IDs across systems. Flag identity gaps, but scope and quote that work
   separately (see `build/import.md`).

## What "done" looks like

- The agent answers the baseline dashboard's questions with **matching numbers**.
- Verified Queries added for those questions and known edge cases.
- Agent surfaced in **CoWork** (or an app via Cortex Code), with a
  named owner.
- A "next dashboard" candidate identified for iteration 2.
- If the customer opted in: a deployed **Streamlit app**, **App Runtime app**, or
  **Dashboard** (Private Preview) showing the baseline KPIs, shared with the customer's role(s).

---

## Install

Unzip into your personal skills directory:

```
~/.snowflake/cortex/skills/semantic-layer-discovery/
```

Restart Cortex Code so the skill is picked up. It loads automatically when your
request matches the triggers above.

## Dependencies

- The installed **`agent-studio`** skill (for import/build mechanics).
- For Step 4, the **`agent-studio`** skill (agent creation).
- For Step 6, the skill for the chosen option and surface:

  | Option | Desktop / CLI | Snowsight |
  |---|---|---|
  | Streamlit app | `developing-with-streamlit-in-snowflake` | `streamlit-in-workspaces` |
  | App Runtime app | `snowflake-apps` + `sar-actions-desktop` | `snowflake-apps` + `sar-actions-workspaces` |
  | Dashboard (Private Preview) | Check for a CoWork Dashboard skill; if none, build in Snowsight Cortex Code | `dashboard` |

- No bundled scripts — the front end is generated per customer at run time.

## File map

```
semantic-layer-discovery/
├── README.md            this guide
├── SKILL.md             manifest + 5-step flow + routing rule
├── discovery/SKILL.md   Steps 1-2
├── build/
│   ├── SKILL.md         Step 3 router
│   ├── import.md        Power BI / Tableau import path (+ identity callout)
│   └── autopilot.md     from-scratch / Autopilot path
├── agent/SKILL.md       Step 4
├── validate/SKILL.md    Step 5
└── app/SKILL.md         Step 6 (Streamlit / App Runtime / Dashboard)
```
