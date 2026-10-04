# Semantic Layer Discovery — Skill Guide

A Cortex Code skill that walks a customer, with as few questions as possible, from "we have
dashboards" to a **governed, agentic BI experience**: a validated Semantic View
wired to a Cortex Agent. It follows the "Quick to Evaluate, Even Quicker to
Production" path and branches on whether the supplied artifacts contain usable
model definitions and source mappings.

---

## What it does

- Requests the **owning artifacts** and a screenshot/results export for one
  baseline dashboard/page, stages the model files, and analyzes them with agent-studio.
- Resolves missing dependencies before choosing import or **Autopilot**, preserving
  usable definitions and asking only for material gaps.
- Reconciles required metric coverage, deploys the candidate view, creates a test
  **Cortex Agent**, then validates results and accepts the scope before sharing.
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
| 1 | Choose **ONE** baseline; request owning artifacts and screenshot/results evidence | `01-intake/SKILL.md` |
| 2 | Analyze, resolve dependencies, confirm scope and deployment destination | `01-intake/SKILL.md` |
| 3 | **Create the Semantic View** and reconcile required coverage | `02-build/SKILL.md` |
| 3a | Usable BI definitions → **import** selected scope | `02-build/import.md` |
| 3b | No usable model / agreed fallback → **Autopilot**, retaining known definitions | `02-build/autopilot.md` |
| 4 | Wire a test **Cortex Agent** on the candidate view | `03-agent/SKILL.md` |
| 5 | **Validate** vs baseline, add Verified Queries, accept scope and ship | `04-validate/SKILL.md` |
| 6 | **Ask** what to build — **Streamlit app**, **App Runtime app**, or **Dashboard** (Private Preview) — then build it | `05-app/SKILL.md` |

### Get the right inputs first

- **Tableau:** the chosen dashboard's `.twb`/`.twbx`; add the published source's
  `.tds`/`.tdsx` if needed. A source-only file is useful with separate baseline evidence.
- **Power BI:** prefer a `.pbit` exported from the model-owning Desktop file, or
  a model-containing `.pbix`. A thin report needs its underlying model owner's artifact.
- **Both:** a screenshot/results export with filters and date range. If already
  supplied, inspect it before asking again. Packaged files with rows are not required
  just to obtain formulas.

Import usable definitions first. Missing dependencies trigger a targeted request;
unsupported calculations trigger coverage review, not repeated file exports.
Screenshots/no usable model use the metadata path with confirmed definition evidence.

---

## How to run it (facilitator notes)

1. **Fewest useful touches.** Extract first, pre-fill the scope/destination
   confirmation, and consolidate only material gaps. Preserve delegated approvals.
2. Carry one **baseline record** through every step. Missing results need not block
   candidate construction, but they block claims of dashboard parity. Keep source
   mappings separate from where the new view is deployed.
3. Keep the customer anchored on **one** baseline dashboard through Step 5.
   Resist scope creep until the first agent is validated and shipped.
4. At Step 3, route on content readiness and hand off to the `agent-studio`
   skill for the actual import (`import_powerbi` / `import_tableau`) or build
   (`creation` / Autopilot).
5. **Identity/reference-data is a separate track.** Importing a dashboard gives
   you the model; it does NOT reconcile the same entity appearing under different
   names/IDs across systems. Flag identity gaps, but scope and quote that work
   separately (see `02-build/import.md`).

## What "done" looks like

- The agent answers the baseline dashboard's questions with **matching numbers**.
- If the customer accepts a subset or reference-query validation instead, label
  that outcome explicitly; it is not full dashboard parity. Missing required
  inputs or approvals produce a saved, blocked run, not a false success.
- Verified Queries added for those questions and known edge cases.
- Agent surfaced in **CoWork** (or an app via Cortex Code), with a
  named owner.
- Acceptance for the tested scope is recorded; formal certification, if required,
  follows the customer's process only after validation.
- If the customer opted in: a deployed **Streamlit app**, **App Runtime app**, or
  **Dashboard** (Private Preview) showing the baseline KPIs, shared with the customer's role(s).

---

## Install

**Snowsight**

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
├── SKILL.md             manifest + 6-step flow + routing rule
├── 01-intake/SKILL.md   Steps 0-2 (Cortex Sense, surface, upload + analyze)
├── 02-build/
│   ├── SKILL.md         Step 3 router
│   ├── import.md        Power BI / Tableau import path (+ identity callout)
│   └── autopilot.md     from-scratch / Autopilot path
├── 03-agent/SKILL.md    Step 4
├── 04-validate/SKILL.md Step 5
└── 05-app/SKILL.md      Step 6 (Streamlit / App Runtime / Dashboard)
```
