# Step 3 — Import path (usable BI definitions)

Import usable model definitions rather than rebuilding them. Supported measures,
relationships, and metadata provide a head start, not a guarantee of parity.

---

## Inputs (all from Steps 1-2)

Reuse the baseline record, stage paths (including any Tableau sidecar), analyze
results, confirmed scope, deployment FQN, and separately confirmed source remap.
Pass existing answers and approvals into the delegated workflow.

## How to run it

Delegate the conversion to the **`agent-studio`** skill:
- Power BI → its **`import_powerbi`** workflow (`pbi_export`).
- Tableau → its **`import_tableau`** workflow (`tableau_export`).

Re-read the installed tool reference before exporting. Reuse intake evidence
where the workflow allows it, but retain mandatory analysis/approval gates.

| Export inputs | How to populate |
|---|---|
| Both tools | Staged `file_path`, required `semantic_model_name`; approved scope filters using exact analyzed names |
| Tableau | `include_worksheets` for selected worksheets, `extract_usage_context: true`; confirm custom SQL handling if `has_custom_sql`. Published source: `additional_files` and, when needed, `published_datasource_stub_name` (intake 2b). `usage_context` may still include worksheets outside `include_worksheets`; use only the selected sheets' entries as baseline evidence |
| Source-only Tableau | No worksheet filter. Deliberately use `include_all_columns: true` if needed to retain source definitions; then review against baseline scope and preserve join keys |
| Power BI | `include_tables` and, when narrowing measures, `include_measures`; keep dependent tables/measures. There is no published-source sidecar or page filter parameter |
| Descriptions | If `generate_descriptions: true`, supply an available `model_name` for Tableau; Power BI has a documented default. Enrichment is not a substitute for coverage |

**Destination is not remapping.** Omit `target_database` / `target_schema` by
default: they overwrite **every base-table reference**, not the semantic view's
deployment location. Only set them for a confirmed uniform source relocation.
For mixed schemas, preserve the FQNs or use agent-studio's edit workflow for
confirmed per-table mappings. A remap cannot recover an M source dropped at parse time.

## Export, reconcile, then deploy

1. Parse the stringified `result`; inspect `success`, `errors`, and `warnings`.
   Export returns `yaml_content`, not a Snowflake object.
2. Apply `02-build/SKILL.md`'s **Required coverage gate** to named baseline metrics
   and dependencies. For Power BI, check export's `unsupported_measure_count`,
   `m_query_warnings`, and `validation_warnings`; zero unsupported measures alone
   does not prove coverage. When tables were dropped (`NO_SNOWFLAKE_REFERENCE`),
   measures that depend on them are "source unavailable", not unsupported. Tableau may skip LOD/table calculations even when their
   source definitions exist. Update the baseline from `usage_context` only where
   it adds evidence, without silently changing the confirmed scope.
3. Follow the delegated save/reference-check sequence: Tableau verifies references
   before `sv-write`; Power BI verifies them after saving. For that save, use the
   **deployment FQN** for `--source-object`, not as an export remap. Verify source objects
   and required columns, including any approved remaps. Empty/skipped validation
   is not proof of correctness. Ask before recreating unsupported logic or running
   custom-view DDL. Reconcile coverage again after fixes.
4. Follow `upload` / `sv-deploy` after explicit deployment
   authorization, reusing it if already given. Verify the actual object exists.

Keep YAML operations inside agent-studio. A blocked metric or declined approval
pauses the affected work; do not silently proceed to agent creation.

If identity inconsistencies affect the baseline, flag them and scope remediation
separately; metadata import does not reconcile entities.

## Exit criteria

- Semantic View created from the import.
- Required coverage passes for the approved scope; exclusions remain explicit.
- View descriptions/synonyms added; result validation is still pending.

Return to `02-build/SKILL.md` "After the branch", then continue to `03-agent/SKILL.md`.
