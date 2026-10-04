# Step 3 — Autopilot path (no usable model or agreed fallback)

Build from Snowflake metadata with **Autopilot** when no usable owning artifact
is available or the user agrees to this fallback. Preserve any recovered model
definitions; screenshots identify scope/results, not the underlying formulas.

---

## Inputs

- The **baseline record** from intake, including screenshots/results, selected
  questions, context, recovered definitions, and explicitly missing evidence.
- The **source tables**: search with the KPI and field names from the
  screenshots (`snowflake_object_search`, `snowflake_semantic_view_search`,
  busiest tables in query history). An existing semantic view on them: offer
  to reuse it.
- **Relevant reference queries**, including BI service-user history when available.
  Confirm their relationship to the baseline and definition; frequency alone
  does not make a query authoritative. See the shared Required coverage gate.

Reuse confirmed tables and deployment destination from intake. Consolidate only
new mapping/definition gaps for confirmation; do not repeat the intake questions.

## How to run it

Delegate to the **`agent-studio`** skill. "Autopilot" is the Snowsight name;
in agent-studio it is the **`creation`** workflow (`sv-generate`):
1. Pass the source tables **and** relevant, corroborated SQL (as `sqlSource`, each
   with its question), along with the baseline context and retained definitions.
   Metadata alone does not establish business logic. Then use agent-studio's
   `suggest_relationships`, `filters_and_metrics_suggestions`, and
   `generate_description` as needed, retaining their required approvals.
2. Before deployment/agent creation, apply `02-build/SKILL.md`'s **Required coverage
   gate**. Generated suggestions are candidates, not validated definitions. Then:
   - Confirm relationships and fact grain against the queries' joins.
   - Take care with non-additive metrics (ratios, distinct counts, averages).
   - Add named filters for the filters shown on screen.
   - Add descriptions + synonyms using the dashboard's labels.
3. Deploy with `upload` after authorization and confirm the object exists. Draft
   reference-query VQR candidates; Step 5 validates them before accepting them.

## Why questions-first matters

Building for the dashboard's few real questions, not every column, keeps the
view scoped and gives Step 5 a clear accuracy target. Expand only after Step 5
proves the baseline.

## Exit criteria

- Semantic View created, or existing view verified for reuse against this baseline.
- Required coverage passes for the approved scope, with explicit exclusions.
- Initial VQR candidates drafted from relevant reference queries.
- Descriptions/synonyms added; result validation is still pending. With no
  dashboard results, Step 5 can validate agreed reference questions but cannot
  claim dashboard parity.

Return to `02-build/SKILL.md` "After the branch", then continue to `03-agent/SKILL.md`.
