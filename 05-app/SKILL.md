# Step 5: Reproduce Dashboards or Build Apps Over Subject-Area Semantic Views

Package each validated Subject Area's Semantic View and Cortex Agent into the customer's chosen front end: **Dashboards (`.dash`)**, **Streamlit apps**, or **App Runtime apps**. If Step 4 accepted a subset, build that subset and label its exclusions honestly.

In **Bulk Estate Mode**, the front-end choice, output directory, and batch page consent were already approved at the Batch Approval Gate in `01-intake/SKILL.md` — do not re-ask per file. Drive multi-report execution through `06-batch/SKILL.md`.

In **Single-Dashboard Mode**, if the user has not chosen a front end yet, run **5.0** below once and wait.

## 5.0 Ask What to Build (Single-Dashboard Mode Only — REQUIRED STOP)

Ask via `ask_user_question` and **wait**:

| Option | Short Description | Delegate Skill (Desktop/CLI vs Snowsight) |
|---|---|---|
| **Dashboard (`.dash`)** | KPI tiles, charts, and filters on the Semantic View in CoWork with follow-up Q&A (Private Preview) | `dashboard` (or recommend Snowsight Workspaces if unavailable on Desktop) |
| **Streamlit app** | Python app with KPI tiles and embedded Cortex Agent chat, fastest custom UI | `developing-with-streamlit-in-snowflake` / `streamlit-in-workspaces` |
| **App Runtime app** | Full web app (Next.js) with custom UI, forms, and multi-step workflows | `snowflake-apps` + `sar-actions-desktop` / `sar-actions-workspaces` |
| **Explain each one to me** | Compare the three options, then ask again | — |
| **Not now** | Skip Step 5 | — |

**STOP — Wait for choice (Single-Dashboard Mode only).**
**Resume rule:** Upon selection, build immediately without re-asking settled Semantic View or Agent FQNs.

## 5a. Bulk & Single Dashboard Reproduction (`.dash`)

For every report queued in `batch_manifest.json` (`phase = dashboards`):

1. **Confirm the Subject Area Semantic View is deployed:** Read `semantic_view_fqn` from the report's `subject_area_id` in `batch_manifest.json` and run `DESCRIBE SEMANTIC VIEW <FQN>`. Never migrate a dashboard directly against raw base tables when its Subject Area Semantic View exists.
2. **Delegate to the `dashboard` skill** (or Snowsight Workspaces `dashboard` skill if Desktop lacks one), passing:
   - The report source (staged BI file + any companion `.tds`/`.tdsx`, or Horizon Catalog reference)
   - The deployed **Subject Area Semantic View FQN** explicitly
   - The target `.dash` output path (`<DASH_OUT_DIR>/<report_slug>.dash`)
   - An isolated per-report scratch directory (`/tmp/bulk_bi/<report_slug>/`) so concurrent workers never collide
   - The batch-approved page/worksheet list and matched `screenshot_path` (if present) for layout, color, and filter fidelity
3. **Non-blocking ambiguity handling:** If a report visual references a field missing from the Semantic View or an unresolved source, record `status=needs_input` (`whats_missing` + `what_i_need`) in `batch_manifest.json` rather than guessing or silently substituting another column.

## 5b. Streamlit & App Runtime Options

- **Streamlit app:** One file (`streamlit_app.py` plus `environment.yml` if needed) containing Header, Baseline KPIs (`FROM SEMANTIC_VIEW(...)`), Ask-the-Agent chat (`st.chat_input` calling the Cortex Agent REST API), and Suggested Verified Query buttons. Use the active Streamlit-in-Snowflake session with no hard-coded credentials.
- **App Runtime app:** Same four sections in Next.js through `snowflake-apps`, server-side Snowflake calls only, no credentials in client code.

## 5c. Universal Semantic-View Grounding Rule (REQUIRED for All Front Ends)

Every tile, chart, table, filter, and dropdown list across `.dash`, Streamlit, and App Runtime builds **must query the Subject Area Semantic View**:

```sql
SELECT * FROM SEMANTIC_VIEW(
  <db>.<schema>.<semantic_view>
  METRICS <metric>, ...
  DIMENSIONS <dimension>, ...
  [WHERE <filter>]
);
```

- Query only the Semantic View — no raw base tables, helper tables, `CREATE TABLE AS`, or cached extracts. If a metric is missing, add it to the Subject Area Semantic View (Step 2) and re-validate, or record it explicitly as unconverted (`batch_state.py set-report --add-unconverted`).
- Populate filter dropdowns with query-backed SQL reading `SEMANTIC_VIEW(... DIMENSIONS ...)`.
- Route conversational chat through the Subject Area's Cortex Agent.

## 5d. Deploy, Verify, and Update Manifest

1. Deploy through the chosen skill and grant access only to named roles (never `PUBLIC`).
2. Confirm every SQL query in the generated `.dash` or app file references `FROM SEMANTIC_VIEW(...)` and verify deployment (`SHOW STREAMLITS`, `SHOW APPLICATION SERVICES`, or `.dash` validation).
3. Update `<WORK_DIR>/batch_manifest.json`:
   ```bash
   python3 <SKILL_DIR>/scripts/batch_state.py set-report \
     --manifest <WORK_DIR>/batch_manifest.json \
     --id <REPORT_ID> --status completed --dashboard-path "<OUT_PATH>"
   ```

## Next Step

In Bulk Estate Mode, return to `06-batch/SKILL.md` to render the updated status card and dispatch the next wave.
