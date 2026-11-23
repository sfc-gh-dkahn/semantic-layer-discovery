# Step 2 — Import & Consolidation Path

Use this guide when building or consolidating a Subject Area Semantic View from Power BI files (`.pbit`, `.pbix`), Tableau files (`.twb`, `.twbx`, `.tds`, `.tdsx`), or Horizon Catalog connected BI metadata.

## Consolidating an Existing Semantic View (`approved_action = consolidate`)

When Step 1 confirmed an existing Semantic View overlaps the incoming Subject Area:

1. Inspect the existing view (`DESCRIBE SEMANTIC VIEW <FQN>`) and load it through `agent-studio` rather than overwriting it blindly.
2. Export the incoming anchor BI model via `agent-studio` (`pbi_export` / `tableau_export`) to identify only the delta: missing base tables, missing relationships, missing dimensions/measures, and synonyms from imported BI labels.
3. Merge the approved delta into the existing Semantic View through `agent-studio`'s edit workflow:
   - **Never break existing metric definitions** used by live dashboards or agents.
   - Where incoming reports conflict with an existing metric (`B006` drift), apply the canonical definition approved at the Batch Approval Gate and log any retired alias.
4. Run the coverage gate (`02-build/SKILL.md` 2c), save (`sv-write`), deploy (`upload` / `sv-deploy`), and confirm via `DESCRIBE SEMANTIC VIEW`.

## Horizon Catalog Connected BI Import (Optional Estate Path)

When Power BI or Tableau metadata is already cataloged in Snowflake Horizon Catalog, delegate to `agent-studio` to import the cataloged semantic model directly rather than exporting files manually, then run the same coverage gate, deploy, and `DESCRIBE SEMANTIC VIEW` read-back check.

## File-Based Subject-Area Import (Power BI & Tableau)

When a Subject Area groups multiple exported reports sharing Snowflake base tables:

1. **Import the anchor model first** (the report with the richest table and measure set from `batch_plan.json`).
2. Delegate to **`agent-studio`**:
   - **Power BI (`.pbit`, `.pbix`):** `import_powerbi` (`pbi_export`) with staged `file_path`, `semantic_model_name`, and exact `include_tables` / `include_measures` names from `pbi_analyze`.
   - **Tableau (`.twb`, `.twbx`, `.tds`, `.tdsx`):** `import_tableau` (`tableau_export`) with staged `file_path`, `semantic_model_name`, `include_worksheets`, `extract_usage_context: true`, and `additional_files` + `published_datasource_stub_name` for paired `.tds`/`.tdsx` files. Confirm custom SQL handling if `has_custom_sql`.
   - **Source-only Tableau (`.tds`, `.tdsx`):** omit worksheet filters, use `include_all_columns: true` if needed, then trim to approved scope while keeping join keys.
3. **Fold in sibling reports:** Compare remaining reports in the same Subject Area against the anchor view's `DESCRIBE SEMANTIC VIEW` output. Add only missing tables, joins, and approved canonical metrics through `agent-studio`'s edit workflow so one Subject Area produces one governed Semantic View instead of N overlapping views.
4. **Never pass large YAML payloads inline as bash arguments.** Write exported `yaml_content` to `/tmp/bulk_bi/<sa_id>/model.sv.yaml` first and pass it safely to `sv-write` with `--source-object <TARGET_DB>.<TARGET_SCHEMA>.<VIEW_NAME>`.
5. **Keep deployment destination and base-table remap separate.** Leave `target_database` / `target_schema` unset unless the user confirmed physical tables moved to a different Snowflake schema (`reference/rules.md`).
6. **Verify references and deploy.** Confirm every base table and required column exists in Snowflake, ask before rebuilding unsupported logic or running custom-view DDL, deploy explicitly via `upload` / `sv-deploy`, and confirm via `SHOW SEMANTIC VIEWS` and `DESCRIBE SEMANTIC VIEW`.

## Scope Boundaries

- **Entity resolution is a separate track.** If the same customer, supplier, or product appears under different IDs across sources, flag it and scope that reconciliation separately.
- **BI security rules do not migrate automatically.** Power BI RLS roles and Tableau user filters must be translated explicitly into Snowflake Row Access Policies or Masking Policies before sharing.

Return to `02-build/SKILL.md` 2c to complete the coverage gate and read-back verification.
