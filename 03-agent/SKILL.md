# Step 3: Subject-Area Cortex Agents

Create or consolidate **one Cortex Agent per Subject Area**, grounded strictly on that Subject Area's deployed Semantic View(s). Sharing and certification wait for Step 4 validation.

## 3a. Check Existing Subject-Area Agent First

Pull runnable Subject Areas with `python3 <SKILL_DIR>/scripts/batch_state.py next-batch --manifest <WORK_DIR>/batch_manifest.json --phase agents --limit 4` (or `--limit 1` in Snowsight).

| Approved Action | What to Do |
|---|---|
| **`reuse` (existing Agent already attaches the Semantic View)** | Verify with `DESCRIBE AGENT <FQN>`, run tool and non-admin checks (3c), and record `agent_status=completed` with the existing FQN |
| **`consolidate` (existing Agent covers this Subject Area)** | Delegate to `agent-studio` to attach the consolidated/new Semantic View FQN and append Subject-Area rules without breaking existing instructions |
| **`create_new`** | Delegate to `agent-studio` to build a new Cortex Agent for this Subject Area |

Never create a duplicate Cortex Agent for a Subject Area when the user approved consolidating into an existing one.

## 3b. Delegate to `agent-studio` & Write Instructions (REQUIRED)

Create or update a real Cortex Agent object grounded on the Subject Area's verified Semantic View FQN(s), and configure its instructions:

1. **Tone:** Match the Subject Area's business audience.
2. **Scope:** Pin the agent explicitly to this Subject Area's approved domain.
3. **Business rules:** Encode only standing defaults confirmed in the baseline record or intake approval. A visible filter on a screenshot is test context, not an automatic default — if no default was confirmed, set none.
4. **Exclusions:** Name each metric outside the accepted scope and instruct the agent to say it cannot answer rather than approximating. Test that it does.
5. **Optional:** For customer- or broad-audience agents, add **Cortex Guardrails**.

## 3c. Verify Persistence, Every Tool, and Non-Admin Access (REQUIRED)

1. **Read-back persistence:** Confirm the deployed agent exists:
   ```sql
   SHOW AGENTS LIKE '<AGENT_NAME>' IN SCHEMA <TARGET_DB>.<TARGET_SCHEMA>;
   DESCRIBE AGENT <TARGET_DB>.<TARGET_SCHEMA>.<AGENT_NAME>;
   ```
2. **Test every attached tool separately:** If a Subject Area agent attaches multiple Semantic Views or tools, test each one individually so no tool goes unverified.
3. **Check access as a non-admin user:** Grants, Row Access Policies, and Masking Policies must work in the agent's execution context before sharing. BI tool security rules do not migrate automatically — list any that require Snowflake policies and never imply source BI security carried over.

## 3d. Update Manifest

```bash
python3 <SKILL_DIR>/scripts/batch_state.py set-subject-area \
  --manifest <WORK_DIR>/batch_manifest.json \
  --id <SA_ID> --agent-status completed --agent-fqn <AGENT_FQN>
```

If an agent fails after 3 bounded retries or lacks grants, record `agent_status=needs_input` or `agent_status=failed` with the exact blocker and continue other Subject Areas.

## Next Step

Read `04-validate/SKILL.md` to validate each Subject Area against its baseline and reference screenshots.
