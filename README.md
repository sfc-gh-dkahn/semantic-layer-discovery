# Semantic Layer Discovery

A Cortex Code skill that turns one trusted dashboard into a validated Semantic
View and Cortex Agent, asking as few questions as it can. The dashboard's data
must be in Snowflake; the Tableau or Power BI file need not connect to it.

The skill sets the order and the checks. The installed **`agent-studio`** skill
does the import, the build, and the agent.

## Who it's for

Teams on a legacy BI tool (Tableau or Power BI) whose data already lives in
Snowflake, and who want more from their dashboards:

- **An agent beside the dashboard.** Business users ask questions in plain
  language and get answers grounded in the same metrics the dashboard shows.
- **Logic out of the BI file.** The calculations move into a Snowflake Semantic
  View, so every tool and agent uses one definition.
- **Optionally, the dashboard on Snowflake.** Rebuild it as a Streamlit app, an
  App Runtime app, or a CoWork Dashboard, with no separate BI tool needed to view it.

You don't need to own the dashboard or know its history; the skill reads what
it needs from the file.

It triggers on phrases like *semantic layer discovery, replace a dashboard with
an agent, agentic BI path.*

## The steps

| Step | What happens | File |
|---|---|---|
| 1 | Upload one dashboard's Tableau or Power BI file, plus a screenshot; the skill checks where its data lives | `01-intake/SKILL.md` |
| 2 | Read the file's metrics and formulas; confirm scope and where the Semantic View goes | `01-intake/SKILL.md` |
| 3 | Create the Semantic View, then check every required metric made it | `02-build/SKILL.md` |
| 3a | Data connected to Snowflake: convert the file's definitions | `02-build/import.md` |
| 3b | Not connected, or no file: build from Snowflake metadata | `02-build/autopilot.md` |
| 4 | Create a **Cortex Agent** on the view | `03-agent/SKILL.md` |
| 5 | Check its answers against the dashboard, then share | `04-validate/SKILL.md` |
| 6 | *(optional)* Rebuild the dashboard on Snowflake: **Streamlit app**, **App Runtime app**, or **CoWork Dashboard** (Private Preview) | `05-app/SKILL.md` |

`reference/rules.md` explains the reasons behind the rules.

Expect about 5–7 touches: the files, one scope confirmation, a published-source
file if needed, agent-studio's deploy approvals, acceptance, and the Step 6 choice.

## What to bring

- **Tableau:** the dashboard's `.twb`/`.twbx`, plus the published data source's
  `.tds`/`.tdsx` if it uses one.
- **Power BI:** a `.pbit` exported from the file that owns the model, or a
  `.pbix` that contains the model. A thin report needs its model owner's file.
- **Both:** a screenshot or results export of the page, with filters and date
  range visible.
- Packaged files with data rows aren't required; a `.twb` or `.pbit` is enough.

No model file? Screenshots from any BI tool still work; the skill builds from
metadata.

## What "done" looks like

- The agent answers the baseline's questions with **matching numbers**, or the
  run is labeled partial, reference-only, or blocked with its next step.
- Verified Queries cover those questions.
- The agent is shared in **CoWork** with named roles and an owner.
- If the customer chose one, a Streamlit app, App Runtime app, or Dashboard shows
  the baseline KPIs.

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

Restart Cortex Code so it picks up the skill. It loads when your request matches
the triggers above.

## Dependencies

- **`agent-studio`** for the Semantic View and the agent.
- For Step 6, the skill for the chosen option and surface:

  | Option | Desktop / CLI | Snowsight |
  |---|---|---|
  | Streamlit app | `developing-with-streamlit-in-snowflake` | `streamlit-in-workspaces` |
  | App Runtime app | `snowflake-apps` + `sar-actions-desktop` | `snowflake-apps` + `sar-actions-workspaces` |
  | Dashboard (Private Preview) | Check for a CoWork Dashboard skill; if none, build in Snowsight Cortex Code | `dashboard` |
