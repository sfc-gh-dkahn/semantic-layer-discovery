# Step 6 — Build the front end

Package the validated Semantic View + Cortex Agent into a front end the customer
can open and share — not just objects in a schema. The customer picks one of
three: a **Streamlit app**, an **App Runtime app**, or a **Dashboard** (Private Preview). This runs
**after Step 5 validation passes**; never build on an unvalidated agent.

This file defines *what* each option must contain. Delegate the mechanics to the
skill for the option and the surface the user is in:

| Option | Cortex Code Desktop / CLI | Snowsight (Cortex Code in Workspaces) |
|---|---|---|
| **Streamlit app** | `developing-with-streamlit-in-snowflake` | `streamlit-in-workspaces` |
| **App Runtime app** | `snowflake-apps` + `sar-actions-desktop` | `snowflake-apps` + `sar-actions-workspaces` |
| **Dashboard** (Private Preview) | Check for a CoWork Dashboard skill; if none exists, recommend building in Snowsight Cortex Code (see 6b-3) | `dashboard` (Snowsight Workspaces) |

Detect the surface by checking your available skills list (e.g.
`sar-actions-desktop` vs `sar-actions-workspaces`). If you can't tell, ask the
user which surface they are in.

---

## 6.0 Ask what to build (REQUIRED stopping point)

Before doing ANY Step 6 work, ask the customer with the ask_user_question tool
and **wait for the answer**:

> Your Semantic View and Cortex Agent are validated. What would you like to build
> on top of them?

| Option | Short description to show |
|---|---|
| **Streamlit app** | Python app with KPI tiles and an agent chat. Fastest to build. |
| **App Runtime app** | Full web app (Next.js) with a custom UI, forms, and multi-step workflows. |
| **Dashboard** | KPI tiles, charts, and filters on the view, stored as one `.dash` file. Built in Snowsight, viewed in CoWork, where users can ask follow-up questions on any tile. Private Preview. |
| **Explain each one to me** | Compare the three, then ask again. |
| **Not now** | Skip Step 6. |

- **Explain each one to me** -> give the comparison below, then ask the same
  question again (without this option).
- **Not now** -> skip Step 6 entirely. Do not scaffold or deploy anything. Note
  in the wrap-up that Step 6 can be re-run later.
- Any build option -> continue to 6a.

### The comparison (for "Explain each one to me")

| | Streamlit app | App Runtime app | Dashboard (Private Preview) |
|---|---|---|---|
| **Best for** | Analysts and business users who want KPIs plus a chat | Teams that need a branded, custom app for wider use | Business users who want curated numbers and to ask "why?" about them |
| **Agent chat** | Yes | Yes | Yes |
| **Code** | Python, one file | TypeScript / Next.js project | One `.dash` file; each tile is a SQL query |
| **Effort** | Low | Higher | Lowest |
| **Where it runs** | Streamlit in Snowflake | Snowflake App Runtime (SPCS) | Built in Snowsight Workspaces; viewed in CoWork |

## 6a. Confirm inputs (one question at a time)

Reuse what you already have from Steps 1-5; only ask for what's missing:

1. Fully qualified **Semantic View** name (from Step 3).
2. Fully qualified **Cortex Agent** name (from Step 4) — Streamlit and App
   Runtime only.
3. **Database.schema** and **warehouse** to deploy into.
4. **Role(s)** that should get access (never default to PUBLIC).

## 6b. Required contents

### 6b-1. Streamlit app

Build a single-file app (`streamlit_app.py` + `environment.yml` if needed):

| Section | What it shows | Source |
|---|---|---|
| **Header** | Baseline dashboard name, agent name, owner | Steps 1, 4, 5 |
| **Baseline KPIs** | The 3-5 baseline metrics as `st.metric` tiles + 1-2 charts, mirroring the Step 1 dashboard (use the screenshot if provided) | `SELECT * FROM SEMANTIC_VIEW(<sv> METRICS ... DIMENSIONS ...)` |
| **Ask the agent** | `st.chat_input` / `st.chat_message` chat that calls the Cortex Agent and renders its text, generated SQL (in an expander), and result tables | Cortex Agent REST API (`/api/v2/databases/<db>/schemas/<schema>/agents/<agent>:run`) |
| **Suggested questions** | Buttons for the baseline questions / VQRs from Step 5 that pre-fill the chat | Step 5 VQRs |

No hard-coded credentials; use the active SiS session.

### 6b-2. App Runtime app

Same sections as the Streamlit app — header, baseline KPIs, agent chat,
suggested questions — built as a Next.js app. Let `snowflake-apps` choose the
project layout and server-side Snowflake calls; KPIs still come from
`SEMANTIC_VIEW(...)` and the chat from the Cortex Agent REST API. No credentials
in client-side code.

### 6b-3. Dashboard (Private Preview)

Same baseline KPIs as the Streamlit app, built as a `.dash` file in Snowsight
Workspaces and deployed to CoWork, where users ask the agent about it. Scorecard
tiles for the KPIs, 1-2 chart tiles, and filters for the baseline dimensions
(wired into tile SQL with `{{ filter('name') }}`). Confirm the account is
enrolled in the Private Preview first. On Desktop / CLI, use a CoWork Dashboard
skill if one exists; otherwise recommend building it in Snowsight Cortex Code.
See [Dashboards in Snowflake Cowork](https://docs.snowflake.com/en/LIMITEDACCESS/cowork-dashboards).

### Rules (all options)

**Every query queries the Semantic View directly (REQUIRED).** This holds for
all three options and every tile, chart, filter, and drop-down list:

```sql
SELECT * FROM SEMANTIC_VIEW(
  <db>.<schema>.<semantic_view>
  METRICS <metric>, ...
  DIMENSIONS <dimension>, ...
  [WHERE <filter>]
);
```

- **Never** query base tables, other views, or copies of the data — no
  helper tables, no `CREATE TABLE AS`, no cached extracts. If a number can't be
  built from the view's metrics and dimensions, add it to the Semantic View
  (Step 3) and re-validate; don't work around it in the front end.
- Filter value lists (e.g. regions in a drop-down) also come from
  `SEMANTIC_VIEW(... DIMENSIONS ...)`. For Dashboards, use a **query**-backed
  filter with that SQL rather than a column-backed one. The CoWork docs suggest
  backing slow filters with a pre-aggregated or Dynamic Table; don't do that
  here. If a filter is too slow, raise it with the customer instead.
- Agent chat goes through the Cortex Agent, which is grounded on the same view.
- This keeps governance (RBAC/RLS/masking) and metric definitions identical to
  Step 4, and KPI numbers identical to what was validated in Step 5.

## 6c. Deploy and verify

1. Deploy via the skill chosen above. Dashboards deploy to CoWork for the
   role(s) from 6a, never PUBLIC.
2. Grant access to the role(s) from 6a.
3. Check the source: every SQL statement in the app files or `.dash` file uses
   `FROM SEMANTIC_VIEW(...)`. Fix any that don't before handing it over.
4. Open it and verify: KPI numbers match Step 5, and (Streamlit / App Runtime) at
   least one suggested question returns a correct agent answer.
5. Give the customer the URL and the source (app files or `.dash` file).

---

## Exit criteria

(Only if the customer chose a build option in 6.0.)

- The object exists and loads without errors: `SHOW STREAMLITS` (Streamlit),
  `SHOW APPLICATION SERVICES` (App Runtime), or the dashboard is deployed and
  opens in CoWork for a recipient role.
- Every query in the source uses `FROM SEMANTIC_VIEW(...)` — no base tables.
- KPI numbers match the baseline dashboard / Step 5 validated numbers.
- Streamlit / App Runtime: the chat answers a baseline question via the agent.
- Access granted to the named role(s); source handed to the customer.
