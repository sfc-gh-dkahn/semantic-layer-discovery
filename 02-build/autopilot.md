# Step 2 — Autopilot Path (Build from Snowflake Metadata)

Use this when a Subject Area or baseline dashboard has no usable model file, when required tables are not connected to Snowflake inside the BI file, when migrating from another BI tool, or when the user prefers a fresh metadata build. Keep all verbatim `CALC`/`MEASURE` formulas extracted during intake.

## Inputs

- Confirmed Snowflake base-table FQNs for the Subject Area or baseline
- Kept verbatim formulas (`CALC`/`MEASURE` from preflight or intake)
- Confirmed deployment `DATABASE.SCHEMA.VIEW_NAME`
- Any corroborated reference queries from the owner or BI service user's query history (confirming each query matches the baseline definition)

## Run It

1. Delegate to **`agent-studio`**'s `creation` workflow (`sv-generate`, called Autopilot in Snowsight). Pass the confirmed tables, corroborated SQL as `sqlSource`, the baseline context, and kept definitions.
2. Use `agent-studio` helpers as needed (`suggest_relationships`, `filters_and_metrics_suggestions`, `generate_description`) — treat suggestions as drafts and verify relationships, fact grain, ratios, distinct counts, and averages.
3. Add named filters for standing business filters and add synonyms matching the original BI field labels.
4. Run the metric-by-metric coverage gate (`02-build/SKILL.md` 2c), deploy explicitly via `upload` / `sv-deploy`, and confirm persistence by read-back (`SHOW SEMANTIC VIEWS` and `DESCRIBE SEMANTIC VIEW`).
5. Draft initial Verified Query candidates from the real business questions or corroborated reference queries for Step 4 validation.

Return to `02-build/SKILL.md` 2d to record completion in `batch_manifest.json`.
