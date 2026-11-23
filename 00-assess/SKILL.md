# Step 0: Estate Assessment, Horizon Connectors, and Existing-Asset Scan

Run this before bulk intake. None of the read-only inventory steps below require confirmation. If a role lacks privileges on a metadata command, state that in one line and continue — never stall a migration on Step 0.

## 0a. Encourage Horizon Catalog BI Connectors First (Recommended, Optional)

For multi-dashboard migrations, **setting up a Snowflake Horizon Catalog metadata connection to Power BI or Tableau is the recommended starting point**:

- **Why recommend it up front:** Unlike file-based bulk imports that require exporting 20 to 100 `.pbit`, `.twbx`, and `.tds` files outside Snowflake, connecting Power BI or Tableau through Horizon Catalog brings BI catalog inventory and table lineage directly into Snowflake.
- **Offer both paths clearly without blocking:**
  1. Connect Power BI or Tableau via Snowflake Horizon Catalog first (see `reference/horizon-catalog-connections.md`).
  2. Proceed immediately with exported files (`.pbit`, `.pbix`, `.twb`, `.twbx`, `.tds`, `.tdsx`) in a local folder, Snowflake stage, or Workspace directory.

Never block the migration if the user prefers exported files.

## 0b. Scan Existing Semantic Views and Cortex Agents (REQUIRED in Bulk Mode)

Before creating any new Semantic View or Cortex Agent, inventory what already exists in the target account or databases so `<SKILL_DIR>/scripts/preflight_batch.py` can detect table overlap and propose consolidation instead of duplicates.

Run read-only discovery:

```sql
SHOW SEMANTIC VIEWS IN ACCOUNT;
SHOW AGENTS IN ACCOUNT;
```

If `IN ACCOUNT` is too broad or restricted, scope to the target database(s) or schema(s) named by the user (`SHOW SEMANTIC VIEWS IN DATABASE <DB>`).

For each relevant existing Semantic View, run `DESCRIBE SEMANTIC VIEW <FQN>` to capture its physical `base_tables` (`DATABASE.SCHEMA.TABLE`). For each existing Cortex Agent, run `DESCRIBE AGENT <FQN>` to capture its attached Semantic View FQNs.

Save the inventory to `<WORK_DIR>/existing_assets.json` (in the user's working project, never inside `<SKILL_DIR>`):

```json
{
  "semantic_views": [
    {
      "fqn": "ANALYTICS.FINANCE.FINANCE_CORE_SV",
      "base_tables": ["ANALYTICS.FINANCE.FACT_REVENUE", "ANALYTICS.FINANCE.DIM_CUSTOMER"]
    }
  ],
  "agents": [
    {
      "fqn": "ANALYTICS.FINANCE.FINANCE_AGENT",
      "semantic_views": ["ANALYTICS.FINANCE.FINANCE_CORE_SV"]
    }
  ]
}
```

Pass `--existing-assets <WORK_DIR>/existing_assets.json` to `<SKILL_DIR>/scripts/preflight_batch.py` in Step 1.

## 0c. Optional Cortex Sense Pre-Pass

If **Cortex Sense** (Public Preview, November 2026) is available in the account, run it before finalizing Subject Areas to surface naming conflicts, metric gaps, and table coverage issues across Snowflake metadata, query history, dbt, Tableau, and Power BI. Do not block the workflow if unavailable.

## Next Step

Read `01-intake/SKILL.md` and pass the Horizon connection status and `<WORK_DIR>/existing_assets.json` forward without re-asking settled questions.
