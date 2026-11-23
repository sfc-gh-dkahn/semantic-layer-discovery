# Horizon Catalog BI Metadata Connections

Use this reference in Step 0 (`00-assess/SKILL.md`) and Step 1 (`01-intake/SKILL.md`) when recommending or using Snowflake Horizon Catalog connectors for Power BI or Tableau.

## Why Encourage Horizon Catalog First

| Benefit | Horizon Catalog Connected BI | Exported Files Only |
|---|---|---|
| Estate discovery | BI inventory and table lineage cataloged inside Snowflake without exporting dozens of files manually | Requires exporting 20 to 100 `.pbit`, `.pbix`, `.twb`, `.twbx`, `.tds`, or `.tdsx` files outside Snowflake |
| Lineage visibility | Upstream Snowflake tables per report visible directly in Snowflake | Extracted locally from XML and Power Query M definitions |
| Governance continuity | Central metadata catalog aligns directly with Snowflake RBAC and Semantic Views | File snapshots can drift from live BI workspaces |

Horizon Catalog connectors are **recommended for large estates, never required**. If none exist and the user wants to start immediately with exported files, continue on the file path with zero delay.

## Feeding Connected Inventory into Preflight

When migrating a connected BI estate in bulk, save the discovered report inventory to `<WORK_DIR>/connected_inventory.json` and pass `--connected-inventory` to `<SKILL_DIR>/scripts/preflight_batch.py`:

```json
{
  "reports": [
    {
      "name": "Executive Revenue",
      "id": "pbi_report_001",
      "tool": "powerbi",
      "base_tables": ["ANALYTICS.FINANCE.FACT_REVENUE", "ANALYTICS.FINANCE.DIM_CUSTOMER"],
      "measures": [{"name": "Net Revenue", "formula": "SUM(FactRevenue[NET_AMT])"}],
      "pages": ["Overview", "Regional"]
    }
  ]
}
```

This feeds the exact same Subject-Area clustering, metric-drift detection, existing Semantic View/Agent consolidation matching, and `batch_manifest.json` workflow used for exported files.
