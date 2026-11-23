# Step 4: Validate, Reconcile Screenshots, Add Verified Queries, and Share

Prove each Subject Area's Semantic View and Cortex Agent against the baseline from Step 1, lock in what works with Verified Queries, hand over open definitions, then share.

## 4a. Validate Against the Baseline

1. **Use the baseline record and `batch_manifest.json`** — no new discovery. Ask questions covering every required metric in the Subject Area, including any implemented separately in SQL. Do not assume an importer carried over page or visual filter context.
2. **Compare like with like:** Apply the exact same filters, date range, refresh cutoff, and access identity as the expected results. Check detail rows, totals, and key filter variants (especially ratios, LODs, and time intelligence). Agree on rounding and tolerance up front with the owner. One matching tile is not enough.
3. **Reconcile matched fixed-filter screenshots (Bulk & Single):** When `screenshot_path` is recorded in `batch_manifest.json` (or uploaded in chat), read its visible filter state and KPI totals, query the deployed Semantic View with those exact filters, and compare side by side.
4. **Diagnose mismatches in order:** data freshness and access -> filter context -> grain and joins -> the metric definition itself. Fix only from confirmed definitions through `agent-studio`, then re-run the coverage gate and affected checks. Never tweak a formula until it matches a screenshot.
5. **Missing expected results?** Ask only for the missing screenshot or expected numbers (or pause that Subject Area while healthy Subject Areas proceed). Objects stay saved while parity waits.
6. **No dashboard baseline?** Validate an agreed reference query or result set and label it **reference validation**, not dashboard parity. A query being frequent does not make it the reference.

## 4b. Add Verified Queries

Add the passing baseline questions (and phrasing variants that tripped the agent) as **Verified Queries** on the Semantic View. They guide Cortex Analyst rather than guaranteeing every future answer. To mine query history for more candidates, use `agent-studio`'s `vqr_suggestions` workflow.

## 4c. Report One Outcome Per Subject Area & Update Manifest

| Outcome | Meaning | Manifest `verify_label` | Next |
|---|---|---|---|
| **Passed** | Every required baseline question matches expected results | `dashboard_parity` (or `reference_validation`) | Get owner acceptance |
| **Partial** | Owner accepted a smaller scope and every question in it passes | `partial` | Keep original gaps visible |
| **Blocked** | Results, definitions, permissions, or approvals are missing, or a comparison fails | `blocked` | Record exact blocker, do not share yet |

Call the scope "validated" only after owner acceptance. Do not apply formal certification tags without explicit owner authorization.

Update `<WORK_DIR>/batch_manifest.json`:

```bash
python3 <SKILL_DIR>/scripts/batch_state.py set-subject-area \
  --manifest <WORK_DIR>/batch_manifest.json \
  --id <SA_ID> --verify-status completed --verify-label <LABEL>
```

## 4d. Share Accepted Agents

After owner acceptance and the Step 3 non-admin check, share each accepted Cortex Agent with named roles (never `PUBLIC`) in **CoWork**.

## 4e. Hand Over Open Definitions

Compile every excluded, unconverted, or blocked metric across the Subject Area (and batch) into one handoff table for business owners:

| Subject Area | Report / Page | Metric | Why Open | Evidence / Formula | Ask for Owner | Owner |
|---|---|---|---|---|---|---|

This list is a note to chase later, not a blocker for passing Subject Areas.

## Next Step

Read `05-app/SKILL.md` (and `06-batch/SKILL.md` for bulk dashboard fan-out).
