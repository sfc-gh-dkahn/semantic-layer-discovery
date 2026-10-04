# Step 3 — Import path

Import the BI file's definitions instead of rebuilding them. Converted measures
and relationships are a head start, not proof of parity.

---

## Inputs (from Steps 1-2)

The baseline record, stage paths (including any Tableau sidecar), analyze
results, confirmed scope, deployment FQN, and any confirmed source remap. Pass
existing answers and approvals into agent-studio.

## Run it

1. **Delegate to `agent-studio`:** Power BI → `import_powerbi` (`pbi_export`);
   Tableau → `import_tableau` (`tableau_export`). Re-read the installed tool
   reference first. Its required analysis and approval steps still run.
2. **Set the export inputs:**

| Export inputs | How to set them |
|---|---|
| Both tools | Staged `file_path`, required `semantic_model_name`; scope filters using exact analyzed names |
| Tableau | `include_worksheets` for selected worksheets, `extract_usage_context: true`; confirm custom SQL handling if `has_custom_sql`. Published source: `additional_files` and, when needed, `published_datasource_stub_name` (intake 2b). `usage_context` may include unselected worksheets; use only the selected ones as evidence |
| Source-only Tableau | No worksheet filter. Use `include_all_columns: true` if needed to keep source definitions; then trim to baseline scope and keep join keys |
| Power BI | `include_tables` and, when narrowing measures, `include_measures`; keep dependent tables and measures. There is no sidecar or page-filter parameter |
| Descriptions | With `generate_descriptions: true`, give Tableau a `model_name`; Power BI has a default. Descriptions don't add coverage |

3. **Leave `target_database` / `target_schema` unset.** They rewrite every
   base-table reference, not where the view deploys. Set them only for a
   confirmed move of all sources to one schema. For mixed schemas, keep the FQNs
   or map tables one by one with agent-studio's edit workflow. No remap brings
   back a source dropped at parse time.
4. **Read the result.** Parse the stringified `result`; check `success`,
   `errors`, and `warnings` against the failure table in intake 2a. Export
   returns `yaml_content`, not a Snowflake object.
5. **Run the coverage gate** (`02-build/SKILL.md` 3c) on each named metric and
   its dependencies.
   - Power BI: also check `unsupported_measure_count`, `m_query_warnings`, and
     `validation_warnings`. Zero unsupported measures doesn't prove coverage.
   - Tableau may skip LOD and table calculations even when their definitions exist.
   - Add `usage_context` evidence to the baseline record, but don't change the
     confirmed scope without asking.
6. **Save and check references** in agent-studio's order: Tableau checks them
   before `sv-write`, Power BI after saving. Pass the deployment FQN as
   `--source-object`.
   - Confirm the source objects and required columns exist, including approved
     remaps. Empty or skipped validation proves nothing.
   - Ask before rebuilding unsupported logic or running custom-view DDL. Re-run
     the gate after fixes.
7. **Deploy** with `upload` / `sv-deploy` once the user authorizes it (reuse an
   earlier authorization). Confirm the object exists.

Keep YAML edits inside agent-studio. A blocked metric or a declined approval
pauses that work; never move on to the agent quietly.

If the same entity has different names or IDs across sources, flag it and scope
the fix separately; importing metadata doesn't reconcile them.

## Done when

- The Semantic View exists, the gate passes for the approved scope, and
  exclusions are recorded.
- Descriptions and synonyms are added. Result validation waits for Step 5.

Return to `02-build/SKILL.md` 3d.
