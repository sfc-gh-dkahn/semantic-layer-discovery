# Step 6: Dual-Surface Batch Orchestrator, Status Card, and Resume

Use this protocol for any Bulk Estate run (2 to 100 reports) or when resuming an existing `<WORK_DIR>/batch_manifest.json`.

## 6a. Dual-Surface Concurrency Mode

Check the surface detected in `SKILL.md`:

| Surface | Batch Limit (`--limit`) | Execution Mechanism |
|---|---|---|
| **Desktop / CLI** | `3` or `4` (never exceed 4 concurrent workers) | Spawn isolated sub-agents for each item returned by `next-batch` |
| **Snowsight Workspaces** | `1` (sequential) | Execute each item in order in the active session |

Both surfaces share the exact same `<WORK_DIR>/batch_manifest.json` state machine, phase gating, and resume commands.

## 6b. Phase Order & Gating

Drive the four phases strictly in order using `<SKILL_DIR>/scripts/batch_state.py`:

1. **Phase 1 — Subject-Area Semantic Views (`--phase semantic_views`):** Build, reuse, or consolidate each Subject Area's Semantic View (`02-build/SKILL.md`).
2. **Phase 2 — Subject-Area Cortex Agents (`--phase agents`):** Create or consolidate 1 Cortex Agent per completed Subject Area (`03-agent/SKILL.md`).
3. **Phase 3 — Validation (`--phase verify`):** Validate each Subject Area against baselines and screenshots (`04-validate/SKILL.md`).
4. **Phase 4 — Dashboard Migration (`--phase dashboards`):** Reproduce every report whose Subject Area Semantic View is `completed` (`05-app/SKILL.md`).

`batch_state.py next-batch` enforces phase gating automatically: agents and dashboards stay queued until their Subject Area Semantic View reaches `completed`, and items exceeding `--max-retries 3` are skipped cleanly.

## 6c. Isolated Worker Contract (Per Report or Subject Area)

When dispatching a sub-agent (Desktop/CLI) or running a sequential turn (Snowsight), pass a self-contained worker prompt:

```text
Migrate <REPORT_FILENAME> (id: <REPORT_ID>) following <SKILL_DIR>/05-app/SKILL.md.
- Source: <STAGE_PATH_OR_CONNECTED_REF> (companions: <COMPANION_FILES>)
- Deployed Subject Area Semantic View FQN: <SEMANTIC_VIEW_FQN>
- Output path: <DASH_OUT_DIR>/<REPORT_SLUG>.dash
- Isolated scratch directory: /tmp/bulk_bi/<REPORT_SLUG>/
- Reference screenshot: <SCREENSHOT_PATH_OR_NONE>
- Batch page consent: <APPROVED_PAGE_RULE>
Rules:
1. Ground every tile and filter strictly FROM SEMANTIC_VIEW(<SEMANTIC_VIEW_FQN>).
2. Write temporary files ONLY inside /tmp/bulk_bi/<REPORT_SLUG>/.
3. If blocked by a missing companion file, unresolved table, or unmapped field, do NOT guess. Return exact whats_missing and what_i_need so the orchestrator marks status=needs_input and continues other reports.
4. Return a structured JSON summary: {status, dashboard_path, unconverted_items, whats_missing, what_i_need, error}.
```

**Single-writer manifest rule:** In parallel Desktop/CLI mode, workers return their structured summary to the coordinator, and the **coordinator alone** calls `batch_state.py set-subject-area` / `set-report` after each wave completes so concurrent workers never race on `batch_manifest.json`.

## 6d. Live Status Card After Every Wave

After each wave finishes, render and display the current progress card:

```bash
python3 <SKILL_DIR>/scripts/batch_state.py status \
  --manifest <WORK_DIR>/batch_manifest.json --format markdown
```

The user can cancel an individual item (`set-report --status canceled`) or halt remaining queued items without losing completed work.

## 6e. Non-Blocking `needs_input` Pauses & Bounded Retries

- **Isolate blockers:** When one file hits a missing `.tds`, thin Power BI report, or unmapped column, mark ONLY that item `needs_input` with `whats_missing` and `what_i_need`. Never halt healthy sibling reports.
- **Max 3 retries:** Every `set-report --status failed` or `set-subject-area --sv-status failed` increments `retry_count`. Once `retry_count >= 3`, `next-batch` excludes the item and surfaces it in the Failed Items triage queue.

## 6f. Final Batch Rollup & Resume Flow

Once no runnable items remain across all phases, generate the final triage report:

```bash
python3 <SKILL_DIR>/scripts/batch_state.py rollup \
  --manifest <WORK_DIR>/batch_manifest.json \
  --out <WORK_DIR>/batch_triage_report.md
```

Present the rollup summary directly in chat:
1. Completed Subject-Area Semantic Views (with FQNs and validation outcomes)
2. Completed Subject-Area Cortex Agents (with FQNs)
3. Completed Dashboards (with `.dash` or app paths)
4. **Needs Input Queue** (`What is missing` + `What I need` per paused item)
5. **Failed Items** (exact error after bounded retries)
6. **Open / Unconverted Definitions** table for business owners

To resume later after supplying missing files or fixing a table mapping, run:

```bash
python3 <SKILL_DIR>/scripts/batch_state.py resume \
  --manifest <WORK_DIR>/batch_manifest.json --retry-needs-input --retry-failed
```

`resume` requeues only paused/failed items and leaves all `completed` Semantic Views, Agents, and Dashboards untouched.
