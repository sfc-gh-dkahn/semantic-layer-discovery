# Semantic Layer Discovery — Skill Guide

A Cortex Code skill that walks a customer, with as few questions as possible, from "we have
dashboards" to a **governed, agentic BI experience**: a certified Semantic View
wired to a Cortex Agent. It follows the "Quick to Evaluate, Even Quicker to
Production" path and branches based on whether the customer already has Power BI
or Tableau.

---

## What it does

- Has the user upload **one** baseline Tableau / Power BI file (or screenshots
  from any other BI tool), stages it with the right tool for Snowsight or
  Desktop/CLI, and **analyzes** it with agent-studio's built-in tools.
- **Branches at Step 3** on the file: Power BI/Tableau **imports** it; `none`
  builds from scratch with **Autopilot**.
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
| 0 (optional) | Run **Cortex Sense** (PuPr Nov 2026) to surface naming conflicts, metric gaps, coverage | `01-intake/SKILL.md` |
| 1 | Choose **ONE** existing dashboard/report/KPI set as the baseline; **upload its file** (or screenshots) | `01-intake/SKILL.md` |
| 2 | Map data objects, questions, and business definitions | `01-intake/SKILL.md` |
| 3 | **Create the Semantic View** — the branch point | `02-build/SKILL.md` |
| 3a | Has Power BI/Tableau → **import** the workbook | `02-build/import.md` |
| 3b | Has neither → **Autopilot** from screenshots or metadata | `02-build/autopilot.md` |
| 4 | Wire a **Cortex Agent** on the certified view | `03-agent/SKILL.md` |
| 5 | **Validate** vs baseline, add Verified Queries, ship | `04-validate/SKILL.md` |
| 6 | **Ask** what to build — **Streamlit app**, **App Runtime app**, or **Dashboard** (Private Preview) — then build it | `05-app/SKILL.md` |

### The one decision point (Step 3)

> The file from Step 1 decides; no question.

- **Power BI** (`.pbit`/`.pbix`) or **Tableau** (`.twb`/`.twbx`/`.tds`/`.tdsx`) → import path
- **Screenshots (any other BI tool) or `none`** → Autopilot / build-from-metadata path

Importing carries DAX measures, relationships, and calculations directly in, so
prefer import when a BI tool exists.

---

## How to run it (facilitator notes)

1. **Fewest touches.** Ask for the file, one pre-filled confirm, and the Step 6
   choice. The file answers the rest; ask anything else only to fix a problem.
2. A **screenshot** of the dashboard is optional, later — it helps check numbers
   in Step 5 and match layout in Step 6.
3. Keep the customer anchored on **one** baseline dashboard through Step 5.
   Resist scope creep until the first agent is validated and shipped.
4. At Step 3, route on the file and hand off to the `agent-studio`
   skill for the actual import (`import_powerbi` / `import_tableau`) or build
   (`creation` / Autopilot).
5. **Identity/reference-data is a separate track.** Importing a dashboard gives
   you the model; it does NOT reconcile the same entity appearing under different
   names/IDs across systems. Flag identity gaps, but scope and quote that work
   separately (see `02-build/import.md`).

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

**Snowsight** (it can't reach GitHub, so don't paste the repo link):

1. On your laptop, download this repo from GitHub (**Code » Download ZIP**) and
   unzip it.
2. Rename the folder to `semantic-layer-discovery` (drop the `-main` suffix).
3. In Snowsight, open a **Workspace** and its Cortex Code chat.
4. Click **+** » **Skills** » **Upload skill folder**, and pick the folder.
5. Start it with `/semantic-layer-discovery`.

**Desktop / CLI**

```
git clone https://github.com/sfc-gh-dkahn/semantic-layer-discovery ~/.snowflake/cortex/skills/semantic-layer-discovery
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
├── 01-intake/SKILL.md   Steps 0-2 (Cortex Sense, surface, upload + analyze)
├── 02-build/
│   ├── SKILL.md         Step 3 router
│   ├── import.md        Power BI / Tableau import path (+ identity callout)
│   └── autopilot.md     from-scratch / Autopilot path
├── 03-agent/SKILL.md    Step 4
├── 04-validate/SKILL.md Step 5
└── 05-app/SKILL.md      Step 6 (Streamlit / App Runtime / Dashboard)
```
