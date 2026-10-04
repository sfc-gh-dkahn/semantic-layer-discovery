# Step 3 — Autopilot path (build from metadata)

Use this when there is no usable model file, when required tables aren't
connected to Snowflake in the file, or when the user agrees to this fallback.
Keep any definitions recovered from the file; screenshots show scope and
results, not formulas.

---

## Inputs

- **The baseline record:** screenshots/results, questions, context, recovered
  definitions, and what's missing.
- **Source tables:** the ones confirmed in intake, or search with the KPI and
  field names (`snowflake_object_search`, `snowflake_semantic_view_search`, the
  busiest tables in query history). If a Semantic View already covers them,
  offer to reuse it.
- **Reference queries,** including the BI service user's history. Confirm each
  one matches the baseline and its definition; how often a query runs doesn't
  make it right.

Reuse the confirmed tables and destination. Ask only about new gaps, in one batch.

## Run it

1. **Delegate to `agent-studio`'s `creation` workflow** (`sv-generate`;
   "Autopilot" is the Snowsight name). Pass the tables, corroborated SQL as
   `sqlSource` (each with its question), the baseline context, and kept
   definitions. Metadata alone doesn't give you business logic.
2. **Use its helpers as needed:** `suggest_relationships`,
   `filters_and_metrics_suggestions`, `generate_description`. Keep their approvals.
3. **Run the coverage gate** (`02-build/SKILL.md` 3c) before deploying. Treat
   suggestions as drafts:
   - Check relationships and fact grain against the reference queries' joins.
   - Take care with ratios, distinct counts, and averages.
   - Add named filters for the filters shown on screen.
   - Write descriptions and synonyms from the dashboard's labels.
4. **Deploy** with `upload` after authorization and confirm the object exists.
5. **Draft Verified Query candidates** from the reference queries. Step 5
   validates them.

Build for the dashboard's few real questions, not every column. Expand after
Step 5 proves the baseline.

## Done when

- The Semantic View exists, or reuse is verified against this baseline.
- The gate passes for the approved scope; exclusions are recorded.
- Verified Query candidates and descriptions are drafted.
- With no dashboard results, Step 5 can do reference validation only, not
  claim dashboard parity.

Return to `02-build/SKILL.md` 3d.
