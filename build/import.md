# Step 3 — Import path (customer HAS Power BI or Tableau)

Use this when the customer already has a BI tool. Importing the existing workbook
brings its **DAX measures, relationships, and calculations directly into** the
Semantic View — so the model reflects definitions the business has already
validated, and you land far closer to a working view than building from scratch.

---

## What to collect

Ask the customer for the file(s) behind the **Step 1 baseline dashboard**:

- **Power BI**: `.pbit` (template — preferred, lighter) or `.pbix` (full desktop file)
- **Tableau**: `.twb` / `.twbx` (workbooks) or `.tds` / `.tdsx` (datasources)

If they have both tools, import the one that owns the baseline dashboard first.
Keep it to the single baseline — do not bulk-import their whole BI estate.

## How to run it

Delegate the conversion to the **`agent-studio`** skill:
- Power BI → its **`import_powerbi`** workflow.
- Tableau → its **`import_tableau`** workflow.

Provide the file path and the target `DATABASE.SCHEMA` for the Semantic View
(align these to the source-of-truth tables identified in Step 2a).

## What carries in vs. what needs review

Carries in cleanly:
- Table relationships and join structure.
- Most measures / calculated fields.
- Field-level metadata.

Needs review (flag to the customer):
- **Some DAX / Tableau custom SQL may not transpile** — non-transpilable measures
  are dropped or need a manual equivalent. Reconcile these against the Step 2c
  definitions.
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
- Step 2c key metrics verified present and correct (fix any dropped measures).
- View descriptions/synonyms added; view treated as certified.

Return to `build/SKILL.md` "After the branch", then continue to `agent/SKILL.md`.
