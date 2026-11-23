# Step 2: Build, Reuse, or Consolidate Subject-Area Semantic Views

Execute this phase **before** creating Cortex Agents or migrating dashboards. One canonical Semantic View set per Subject Area prevents duplicating definitions across sibling reports.

## 2a. Route Each Subject Area by Approved Action

Pull the next runnable Subject Areas from `<WORK_DIR>/batch_manifest.json` (`python3 <SKILL_DIR>/scripts/batch_state.py next-batch --manifest <WORK_DIR>/batch_manifest.json --phase semantic_views --limit 4`, or `--limit 1` in Snowsight). For single-dashboard mode, process the single baseline directly.

| Approved Action | What Exists | Route |
|---|---|---|
| **`reuse`** | Existing Semantic View already covers all Subject Area tables and approved metrics | Inspect via `DESCRIBE SEMANTIC VIEW <FQN>`, run coverage gate (2c), record `sv_status=completed` with existing FQN |
| **`consolidate`** | Existing Semantic View overlaps core tables and needs additional tables or metrics from incoming reports | Read `02-build/import.md` § Consolidating an Existing Semantic View, extend through `agent-studio`, run coverage gate (2c), redeploy |
| **`create_new` (Exported BI files / Connected BI)** | Staged `.pbit`, `.pbix`, `.twb`, `.twbx`, `.tds`, `.tdsx`, or Horizon Catalog BI metadata with Snowflake sources resolved | Read `02-build/import.md`, delegate to `agent-studio` (`import_powerbi`, `import_tableau`, or connected BI workflow) |
| **`create_new` (No usable file / non-Snowflake source / fallback)** | Source tables confirmed in Snowflake without an importable BI model | Read `02-build/autopilot.md`, delegate to `agent-studio` `creation` workflow |

Never create a duplicate Semantic View when the user approved `reuse` or `consolidate`.

## 2b. Delegate Mechanics to `agent-studio` (REQUIRED)

Invoke the **`agent-studio`** skill for all Semantic View creation, editing, writing, and deployment. Never hand-write Semantic View definitions around `agent-studio`.

Pass a structured context block into `agent-studio` so settled questions are not re-asked:
- Subject Area name, member reports, anchor file, and companion `.tds`/`.tdsx` stage paths
- Approved action (`reuse`, `consolidate`, or `create_new`) and existing Semantic View FQN (if any)
- Deployment FQN (`<TARGET_DB>.<TARGET_SCHEMA>.<VIEW_NAME>`) kept strictly separate from base-table FQNs
- Confirmed base-table remap (`target_database` / `target_schema`) ONLY if the user approved a physical source move
- Canonical metric resolutions for any `B006` metric drift items

## 2c. Metric-by-Metric Coverage Gate (Before Deployment)

Check the candidate Semantic View against the Subject Area's required metrics **metric by metric**, never by total counts alone:

| Status | Action |
|---|---|
| Converted or implemented, sources resolved | Review grain, joins, filters, and dependencies — queue for Step 4 validation |
| Definition found, translation unsupported (for example complex DAX, Tableau LOD, or table calculations) | Keep exact formula verbatim. Ask approval to implement it in SQL through `agent-studio`, or record it in the open-definitions list |
| Definition or dependency missing | Record `needs_input` in `batch_manifest.json` (`whats_missing` + `what_i_need`) and continue other Subject Areas. Never infer a formula from a name |

A metric whose underlying column or join was dropped is blocked even if its name survived. An empty export fails the gate.

## 2d. Deploy & Verify Persistence by Read-Back (REQUIRED)

1. Deploy explicitly via `agent-studio` (`upload` / `sv-deploy`) once authorized — an export or saved YAML is not a deployed view.
2. **Read-back verification:** Confirm every deployed Semantic View exists and exposes the expected objects:
   ```sql
   SHOW SEMANTIC VIEWS LIKE '<VIEW_NAME>' IN SCHEMA <TARGET_DB>.<TARGET_SCHEMA>;
   DESCRIBE SEMANTIC VIEW <TARGET_DB>.<TARGET_SCHEMA>.<VIEW_NAME>;
   ```
3. Update `<WORK_DIR>/batch_manifest.json` atomically:
   ```bash
   python3 <SKILL_DIR>/scripts/batch_state.py set-subject-area \
     --manifest <WORK_DIR>/batch_manifest.json \
     --id <SA_ID> --sv-status completed --semantic-view-fqn <FQN>
   ```
4. If a Subject Area fails after 3 bounded retries or hits a missing dependency, mark `sv_status=needs_input` or `sv_status=failed` with exact remediation notes and move to the next Subject Area.

## Next Step

Read `03-agent/SKILL.md` to create or consolidate one Cortex Agent per Subject Area.
