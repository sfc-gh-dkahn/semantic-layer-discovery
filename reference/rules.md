# Rules: reasons and edge cases

The step files say what to do. This file says why, for the cases where the
short rule isn't enough. Read a section when a step points to it.

## Inputs

- **Ask for definitions, not data.** Packaged files (`.twbx`, `.pbix`) can hold
  business rows. Prefer a file without them (`.twb`, `.pbit`) when available.
  Packaging a file doesn't make its unsupported calculations convertible.
- **Don't ask users to change connection modes.** Live vs extract (Tableau) and
  Import vs DirectQuery (Power BI) don't matter for importing metadata.
- **Screenshots are evidence of scope and results, not formulas.** They tell you
  which metrics, filters, and numbers the baseline shows. They can't tell you
  how a metric is calculated.
- **A source-only file still helps.** A `.tds` or `.tdsx` without a workbook
  carries real definitions; it just needs the dashboard page and its results
  from somewhere else.
- **The builder may not own the dashboard.** That's why the skill extracts
  answers from files and asks only about gaps, instead of interviewing for
  purpose and audience.

## Sources

- **An extract keeps its source definitions.** A Tableau extract of a Snowflake
  connection still names the Snowflake source. Whether `tableau_analyze` accepts
  a Hyper extract next to that connection is unverified; intake 1b-2 covers both
  outcomes.
- **Matching data is not lineage.** Similar rows or column names don't prove a
  BI table comes from a given Snowflake table. Have the user confirm.
- **A remap can't recover a dropped table.** If the parser dropped a source at
  parse time, pointing the exporter at a new schema won't bring it back.
- **Why non-Snowflake tables never reach export.** The exporter drops them
  without an error, so their metrics fail later and look like translation
  problems. Routing them in intake 1b-3 names the real cause early.
- **Why a nested `sqlproxy` fails.** A `.tds` that is itself a published-source
  stub holds a server pointer, not tables. Only a copy connected straight to
  Snowflake, or finding the data in Snowflake, gets past it.

## Query history

Query history can help recover a metric, but it is not a formula source on its
own:
- It may hold refresh or extract-build SQL rather than the metric's logic.
- For DirectQuery, it may hold only part of a calculation; the rest runs in the
  BI tool.
- A name, alias, or matching number alone proves nothing. Check candidate SQL
  against the definition, the source mapping, the grain, and the filters.
- Missing SQL doesn't mean the formula is missing, or that it runs only in the BI
  tool.
- How often a query runs doesn't make it the reference for validation.

## Coverage

- **Why gate by named metric, not by count.** An export can succeed with most
  measures while dropping the one the baseline page needs. Totals hide that.
- **Unsupported is not unimplementable.** A formula the importer can't convert
  can often be written in SQL, but only from its exact definition and with the
  user's approval. It never permits a guessed approximation.
- **Why not certify before Step 5.** Coverage proves a metric exists, not that
  its numbers are right.

## Destination vs remap

`target_database` / `target_schema` in the exporters rewrite every base-table
reference. Using them to choose where the view deploys points every table at
the wrong schema. The deployment FQN goes to `sv-write` as `--source-object`.
Source FQNs stay as they are unless the user confirms the data moved.

## Staging

- **Why not a temporary stage.** It ends with the session, which can happen
  before agent-studio's tools read the file.
- **Why never `cortex ws cp`.** It copies into the sandbox, not the stage, and
  still reports success. `LIST` after every copy catches it.
