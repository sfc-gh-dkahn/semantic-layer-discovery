# Agentic BI Migration

A Cortex Code skill that migrates a business BI estate — or a single trusted dashboard — into governed Snowflake **Semantic Views**, **Cortex Agents**, and **Dashboards** split cleanly by subject matter, without duplicating semantic models.

Formerly `semantic-layer-discovery`, this release adds full bulk estate orchestration alongside the original single-dashboard guided flow.

## What makes this different

- **Horizon Catalog connectors encouraged first (optional).** Connecting Power BI or Tableau through Snowflake Horizon Catalog brings in BI inventory and lineage without exporting dozens of files by hand. When no connector is set up, drop exported files (`.pbit`, `.pbix`, `.twb`, `.twbx`, `.tds`, `.tdsx`) into a local folder, Snowflake stage, or Workspace directory — including `.pbix` directly.
- **Zero duplicated Semantic Views.** Before creating anything, deterministic preflight clusters incoming reports by shared Snowflake base tables into **Subject Areas**, surfaces cross-report metric drift, and maps **existing Semantic Views and Cortex Agents** so you can choose to **consolidate/extend**, **reuse as-is**, or **create new**.
- **One Semantic View layer and one Cortex Agent per Subject Area.** Every migrated dashboard queries its Subject Area's deployed Semantic View (`FROM SEMANTIC_VIEW(...)`), keeping business logic out of individual reports.
- **Resumable, fault-isolated bulk execution.** Tracks every Subject Area and report in an atomic, SHA-256-keyed `batch_manifest.json`. A single blocked file pauses with `needs_input` (`What's missing` / `What I need`) while the rest of the batch finishes. Re-runs skip completed items automatically.
- **Dual-surface aware.** Supports 3 to 4 bounded parallel workers on Cortex Code Desktop/CLI and switches cleanly to a sequential manifest loop in Snowsight Workspaces.

## Lifecycle

| Step | What happens | File |
|---|---|---|
| **0** | Encourage Horizon Catalog BI connector (optional), scan existing Semantic Views and Agents, optional query-history review | `00-assess/SKILL.md` |
| **1** | Discover and preflight files or connected inventory (`scripts/preflight_batch.py`), cluster by base tables into Subject Areas, run one **Batch Approval Gate** (or single-dashboard intake) | `01-intake/SKILL.md` |
| **2** | Reuse, consolidate, or build **1 canonical Semantic View set per Subject Area** via `agent-studio`, run coverage gate, deploy, verify by read-back | `02-build/SKILL.md` |
| **3** | Consolidate or create **1 Cortex Agent per Subject Area** via `agent-studio`, check non-admin access | `03-agent/SKILL.md` |
| **4** | Validate against baseline and reference screenshots, add Verified Queries, accept, share, hand over open definitions | `04-validate/SKILL.md` |
| **5** | Reproduce dashboards (`.dash`, Streamlit, or App Runtime) wired strictly `FROM SEMANTIC_VIEW(...)` | `05-app/SKILL.md` |
| **6** | Orchestrate bounded parallel (Desktop) or sequential (Snowsight) workers, render status card, roll up triage queue, resume/retry | `06-batch/SKILL.md` |

## What to bring

- **Best for large estates:** A Snowflake Horizon Catalog metadata connection to Power BI or Tableau.
- **Bulk or single exported files:**
  - **Power BI:** `.pbit` (preferred, readable JSON model) or model-containing `.pbix`. Thin reports need their model-owning file.
  - **Tableau:** `.twb` or `.twbx` workbooks, plus companion `.tds` or `.tdsx` files for any published data sources in the same folder.
  - **Reference screenshots (optional, recommended):** Fixed-filter screenshots matching report names improve layout fidelity and numerical reconciliation.
- **No BI files or other BI tools:** Screenshots, text/model exports, or Snowflake table names still work through the Autopilot metadata path.

## Quickstart

**Bulk estate migration (folder or stage):**

> `/agentic-bi-migration` Migrate all Power BI and Tableau dashboards in `./exports/finance_bi` into subject-area Semantic Views, Cortex Agents, and dashboards.

**Single dashboard (original flow):**

> `/agentic-bi-migration` Start with one baseline dashboard: `./exports/executive_revenue.pbit` and its screenshot.

**Resume a paused batch:**

> `/agentic-bi-migration` Resume the batch in `./bi_migration_run/batch_manifest.json`.

## Install

**Cortex Code Desktop / CLI**

```bash
git clone https://github.com/sfc-gh-dkahn/semantic-layer-discovery ~/.snowflake/cortex/skills/agentic-bi-migration
```

Restart Cortex Code and run `/agentic-bi-migration`.

**Cortex Code in Snowsight**

1. Download this repo from GitHub (**Code -> Download ZIP**) and unzip it.
2. Rename the unzipped folder to `agentic-bi-migration`.
3. Open a Snowsight **Workspace** and its Cortex Code chat.
4. Click **+** -> **Skills** -> **Upload skill folder** and select `agentic-bi-migration`.
5. Run `/agentic-bi-migration`.

## Dependencies

- **Python 3.11+** (stdlib only — zero `pip install` needed for `scripts/preflight_batch.py` and `scripts/batch_state.py`).
- Bundled Cortex Code skills delegated by this orchestrator:
  - **`agent-studio`** — Semantic View import (`import_powerbi`, `import_tableau`), Autopilot (`creation`), deploy (`upload` / `sv-deploy`), Verified Queries (`vqr_suggestions`), and Cortex Agent creation.
  - **`dashboard`** (or **`developing-with-streamlit-in-snowflake` / `streamlit-in-workspaces`** or **`snowflake-apps`**) — for Step 5 front ends over validated Semantic Views.

## File map

```text
agentic-bi-migration/
├── README.md                              public guide
├── SKILL.md                               thin <200-line dual-mode router
├── .skillignore                           excludes tests/ and evals/ from runtime bundle
├── 00-assess/SKILL.md                     Horizon connector guidance and existing SV/Agent scan
├── 01-intake/SKILL.md                     bulk preflight + Batch Approval Gate + single-dashboard intake
├── 02-build/
│   ├── SKILL.md                           subject-area Semantic View router + coverage gate
│   ├── import.md                          Power BI / Tableau / connected BI import + consolidation
│   └── autopilot.md                       metadata-driven Autopilot build
├── 03-agent/SKILL.md                      subject-area Cortex Agent consolidation/creation + governance check
├── 04-validate/SKILL.md                   baseline validation, screenshot reconciliation, VQRs, open definitions
├── 05-app/SKILL.md                        bulk + single Dashboard, Streamlit, and App Runtime delivery
├── 06-batch/SKILL.md                      dual-surface worker loop, status card, pause/resume protocol
├── reference/
│   ├── rules.md                           staging, remap, untrusted-input, and bulk gotchas
│   └── horizon-catalog-connections.md     Horizon Catalog BI connector overview and inventory schema
├── scripts/
│   ├── preflight_batch.py                 stdlib Python 3.11+ untrusted-safe preflight, clustering, consolidation match
│   └── batch_state.py                     stdlib Python 3.11+ atomic SHA-256 manifest, status card, resume/rollup
├── tests/test_batch_scripts.py            offline stdlib unit tests
└── evals/evals.json                       behavioral trigger and routing evals
```

## Running tests locally

```bash
python3 -m unittest discover -s tests -v
```
