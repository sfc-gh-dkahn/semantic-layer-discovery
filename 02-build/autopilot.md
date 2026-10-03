# Step 3 — Autopilot / from-scratch path (customer has NEITHER BI tool)

Use this when the customer has no Power BI or Tableau to import. You build the
Semantic View fresh from Snowflake metadata, using **Autopilot** to propose the
structure, then refine it with the definitions captured in Step 2.

---

## Inputs (all from discovery)

- The **source-of-truth tables/views**: search for them first (`snowflake_object_search`,
  `snowflake_semantic_view_search`, busiest tables in query history), then
  confirm the picks and target schema in one pre-filled question.
- The top queries on those tables in query history — these become Verified
  Queries later.

## How to run it

Delegate the build to the **`agent-studio`** skill's **`creation`** workflow:
1. Point it at the source tables; let **Autopilot propose** the structure
   (relationships, candidate metrics, dimensions, descriptions).
2. Refine the proposal against Step 2:
   - Correct/confirm relationships and fact grain.
   - Encode each key metric with the formula used in query history.
   - Add non-additive metrics carefully (ratios, distinct counts, averages).
   - Add named filters for the standing filters and common drill-downs.
   - Add descriptions + synonyms so Cortex Analyst maps business language.
3. Turn those top queries into **Verified Queries (VQRs)** — this seeds
   accuracy and is validated in Step 5.

## Why questions-first matters

Anchoring the build on the ~5 real questions (rather than modeling every column)
keeps the view scoped to the baseline and gives you a concrete accuracy target.
Build for those questions first; expand only after Step 5 proves the baseline.

## Exit criteria

- Semantic View created and refined.
- Key metrics encoded with correct, owner-confirmed formulas.
- Initial VQRs drafted from the baseline questions.
- View descriptions/synonyms added; view treated as certified.

Return to `02-build/SKILL.md` "After the branch", then continue to `03-agent/SKILL.md`.
