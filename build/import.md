# Step 3 — Import path (customer HAS Power BI or Tableau)

Use this when the customer already has a BI tool. Importing the existing workbook
brings its **DAX measures, relationships, and calculations directly into** the
Semantic View — so the model reflects definitions the business has already
validated, and you land far closer to a working view than building from scratch.

---

## Inputs (all from Step 2)

The file is already staged and analyzed: stage path, analyze result, confirmed
tabs/tables, and target `DATABASE.SCHEMA`. Don't ask for them again.

## How to run it

Delegate the conversion to the **`agent-studio`** skill:
- Power BI → its **`import_powerbi`** workflow (`pbi_export`).
- Tableau → its **`import_tableau`** workflow (`tableau_export`).

Pass every value in so agent-studio skips its own questions: stage `file_path`,
`include_worksheets` / `include_tables`, `target_database`, `target_schema`,
`generate_descriptions: true`, and for Tableau `extract_usage_context: true`
(feeds Steps 4-5), `use_custom_sql_in_definition` if `has_custom_sql`, and
`additional_files` for a published `.tdsx`. Check each table in the result
exists (`SHOW TABLES LIKE`); if not, find the match and re-export.

## What carries in vs. what needs review

Carries in cleanly:
- Table relationships and join structure.
- Most measures / calculated fields.
- Field-level metadata.

Needs review (flag to the customer):
- **Some DAX / Tableau custom SQL may not transpile** — non-transpilable measures
  are dropped or need a manual equivalent. Step 5 checks these against the
  dashboard.
- Database/schema remapping — confirm imported table references point at the real
  Snowflake objects.

## Identity / reference-data is a SEPARATE track

Importing a workbook gives you the **model** — relationships, measures,
calculations. It does **not** fix inconsistent underlying data. If the same
entity (a supplier, customer, product, or location) appears under different
names or IDs across source systems, importing the dashboard will not reconcile
them — the Semantic View will faithfully reproduce the ambiguity.

Set this expectation with the customer explicitly:
- **This step:** import the dashboard's definitions into a Semantic View.
- **A distinct effort:** master-data / reference-data / identity resolution —
  agreeing on one canonical key per entity and mapping every source to it.

Do not let the two be conflated in scope or timeline. The import can proceed
now; the identity work is its own project (often with its own business owners,
e.g. Procurement for supplier identity) and should be quoted/sequenced
separately. Flag any identity gaps you find, but keep this step focused on the
model.

## Exit criteria

- Semantic View created from the import.
- Key metrics verified present (dropped measures noted for Step 5).
- View descriptions/synonyms added; view treated as certified.

Return to `build/SKILL.md` "After the branch", then continue to `agent/SKILL.md`.
