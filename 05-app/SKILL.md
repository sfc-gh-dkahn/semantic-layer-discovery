# Step 6 — Build the front end

Package the validated Semantic View and agent into something the customer can
open and share: a **Streamlit app**, an **App Runtime app**, or a **Dashboard**
(Private Preview). Run this only after Step 5 passes. If Step 5 accepted a
subset, build that subset and label its exclusions; don't present it as the
full dashboard.

This file says *what* each option contains. Delegate the build to the skill
for the option and the user's surface:

| Option | Cortex Code Desktop / CLI | Snowsight (Cortex Code in Workspaces) |
|---|---|---|
| **Streamlit app** | `developing-with-streamlit-in-snowflake` | `streamlit-in-workspaces` |
| **App Runtime app** | `snowflake-apps` + `sar-actions-desktop` | `snowflake-apps` + `sar-actions-workspaces` |
| **Dashboard** (Private Preview) | A CoWork Dashboard skill if one exists; otherwise recommend building in Snowsight Cortex Code (6b-3) | `dashboard` (Snowsight Workspaces) |

Tell the surface from your skills list (`sar-actions-desktop` vs
`sar-actions-workspaces`). If you can't, ask.

---

## 6.0 Ask what to build (REQUIRED stop)

Before any Step 6 work, ask with ask_user_question and **wait**:

> Your Semantic View and Cortex Agent are validated. What would you like to build
> on top of them?

| Option | Short description to show |
|---|---|
| **Streamlit app** | Python app with KPI tiles and an agent chat. Fastest to build. |
| **App Runtime app** | Full web app (Next.js) with a custom UI, forms, and multi-step workflows. |
| **Dashboard** | KPI tiles, charts, and filters on the view, stored as one `.dash` file. Built in Snowsight, viewed in CoWork, where users can ask follow-up questions on any tile. Private Preview. |
| **Explain each one to me** | Compare the three, then ask again. |
| **Not now** | Skip Step 6. |

- **Explain each one to me:** show the comparison below, then ask again without
  this option.
- **Not now:** build nothing. Note in the wrap-up that Step 6 can run later.
- **A build option:** go to 6a.

| | Streamlit app | App Runtime app | Dashboard (Private Preview) |
|---|---|---|---|
| **Best for** | Analysts and business users who want KPIs plus a chat | Teams that need a branded, custom app for wider use | Business users who want curated numbers and to ask "why?" about them |
| **Agent chat** | Yes | Yes | Yes |
| **Code** | Python, one file | TypeScript / Next.js project | One `.dash` file; each tile is a SQL query |
| **Effort** | Low | Higher | Lowest |
| **Where it runs** | Streamlit in Snowflake | Snowflake App Runtime (SPCS) | Built in Snowsight Workspaces; viewed in CoWork |

## 6a. Gather inputs (reuse; ask only for gaps)

1. Semantic View FQN (Step 3).
2. Cortex Agent FQN (Step 4); apps only.
3. Deployment `database.schema` and warehouse.
4. Roles to grant (never PUBLIC).

## 6b. What each option contains

### 6b-1. Streamlit app

One file (`streamlit_app.py`, plus `environment.yml` if needed):

| Section | What it shows | Source |
|---|---|---|
| **Header** | Baseline dashboard name, agent name, owner | Steps 1, 4, 5 |
| **Baseline KPIs** | The 3-5 baseline metrics as `st.metric` tiles + 1-2 charts, mirroring the baseline dashboard (use the screenshot if provided) | `SELECT * FROM SEMANTIC_VIEW(<sv> METRICS ... DIMENSIONS ...)` |
| **Ask the agent** | `st.chat_input` / `st.chat_message` chat that calls the Cortex Agent and shows its text, generated SQL (in an expander), and result tables | Cortex Agent REST API (`/api/v2/databases/<db>/schemas/<schema>/agents/<agent>:run`) |
| **Suggested questions** | Buttons for the baseline questions / Verified Queries that pre-fill the chat | Step 5 |

Use the active Streamlit-in-Snowflake session; no hard-coded credentials.

### 6b-2. App Runtime app

The same four sections as a Next.js app. Let `snowflake-apps` choose the layout
and the server-side Snowflake calls. KPIs come from `SEMANTIC_VIEW(...)`, chat
from the Cortex Agent REST API. No credentials in client-side code.

### 6b-3. Dashboard (Private Preview)

The same baseline KPIs as a `.dash` file in Snowsight Workspaces, deployed to
CoWork, where users ask the agent about it: scorecard tiles for the KPIs, 1-2
chart tiles, and filters for the baseline dimensions (wired into tile SQL with
`{{ filter('name') }}`). Confirm the account is enrolled in the Private Preview
first. On Desktop / CLI, use a CoWork Dashboard skill if one exists; otherwise
recommend building it in Snowsight Cortex Code. See
[Dashboards in Snowflake Cowork](https://docs.snowflake.com/en/LIMITEDACCESS/cowork-dashboards).

### Rules for all three

**Every query reads the Semantic View (REQUIRED):** every tile, chart, filter,
and drop-down list.

```sql
SELECT * FROM SEMANTIC_VIEW(
  <db>.<schema>.<semantic_view>
  METRICS <metric>, ...
  DIMENSIONS <dimension>, ...
  [WHERE <filter>]
);
```

- Query only the view: no base tables, other views, helper tables,
  `CREATE TABLE AS`, or cached extracts. If a number can't come from the view,
  add it to the view (Step 3) and re-validate.
- Filter value lists come from `SEMANTIC_VIEW(... DIMENSIONS ...)`. In
  Dashboards, use a **query**-backed filter with that SQL, not a column-backed
  one. The CoWork docs suggest a pre-aggregated or Dynamic Table for slow
  filters; don't. Raise the slowness with the customer instead.
- Chat goes through the agent, which uses the same view.

This keeps security, metric definitions, and numbers identical to what Step 5
validated.

## 6c. Deploy and verify

1. Deploy through the chosen skill. Dashboards go to CoWork for the 6a roles,
   never PUBLIC.
2. Grant the 6a roles access.
3. Check the source: every SQL statement in the app files or `.dash` file uses
   `FROM SEMANTIC_VIEW(...)`. Fix any that don't.
4. Open it: KPI numbers match Step 5, and (apps) one suggested question gets a
   correct agent answer.
5. Give the customer the URL and the source files.

## Done when

(Only if the customer chose a build option.)

- It exists and loads: `SHOW STREAMLITS`, `SHOW APPLICATION SERVICES`, or the
  dashboard opens in CoWork for a recipient role.
- Every query uses `FROM SEMANTIC_VIEW(...)`.
- KPI numbers match Step 5.
- Apps: the chat answers a baseline question through the agent.
- The named roles have access; the customer has the source.
