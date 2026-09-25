# Steps 1-2: Discovery

This covers the first two steps of the Path Forward: pick a single baseline, then
map the data objects, questions, and business definitions behind it.

---

## Step 1 — Choose ONE existing dashboard, report, or KPI set

Start with something the business **already uses and trusts**. A single,
well-understood dashboard is the best first candidate — you prove the agentic
approach against a known baseline, so success is unambiguous.

Ask the customer (use the ask_user_question tool):
- Which dashboard/report do stakeholders rely on most today?
- Who are its primary consumers, and what decisions do they make from it?
- Is it considered a source of truth? (If it's disputed, that's a *reason* to
  pick it — the semantic layer can settle the definition.)

**Do not** let the customer pick "all of analytics." One dashboard. Write down its
name; it becomes the validation baseline in Step 5.

### Ask for a screenshot of the dashboard

After the customer names the baseline, **ask them to share a screenshot** (or a
few) of that dashboard — use the ask_user_question tool to request it:

> Can you paste a screenshot of that dashboard? Seeing the actual charts, metrics,
> and filters helps me map it accurately in the next step.

Why this matters:
- You are multimodal — a screenshot lets you **read the real metric names, chart
  types, filters, and layout** directly, instead of relying only on description.
- It jump-starts Step 2: many of the metrics, dimensions, and filters you need to
  capture are visible on the dashboard face.
- It anchors Step 5 validation — you know exactly which numbers the agent must
  reproduce.

How to use the screenshot:
- Read the visible **metrics/KPIs** (these become measures in Step 2b/2c).
- Note **groupings and filters** shown (regions, dates, segments → dimensions).
- Identify **chart titles / questions** the dashboard answers (→ Step 2b).
- Treat what you infer as a **draft** — confirm each item with the customer in
  Step 2 rather than assuming. If no screenshot is available, proceed with the
  Step 2 questions as normal (the screenshot is helpful, not required).

---

## Step 2 — Map data objects, questions, and business definitions

For the chosen dashboard, capture three things. These become the raw material for
the Semantic View (Step 3) and the Verified Queries (Step 5).

### 2a. Data objects
- Which **tables and views** feed this dashboard?
- What are the **join keys**, and what is the **grain** of each fact table?
  (Grain mistakes cause inflated/double-counted numbers — pin this down.)
- Any slowly-changing dimensions (valid_from/valid_to) or role-playing dims
  (e.g., order date vs. ship date)?

### 2b. Questions & interactions
- What are the **top 3-5 questions** the dashboard answers?
- What **filters** and **drill-down paths** do users apply (time, region,
  segment, product hierarchy)?
- What **date convention** — fiscal vs. calendar? Default ranges?

### 2c. Business definitions (the part people disagree on)
Capture each key metric's **exact** definition, in the customer's words:
- *"What does an active customer mean?"*
- *"How is revenue defined?"* (gross? net of returns? recognized vs. booked?)
- Which metrics have **multiple definitions** across departments — and which is
  canonical? Note who owns the canonical definition.
- Any standing filters that always apply (e.g., exclude cancelled orders).

### The five discovery buckets (question bank)
Use these to make sure Step 2 is complete:
1. **Scope** — top 3-5 business questions; consumers; source-of-truth tables.
2. **Metrics** — measures + precise formulas; non-additive metrics (ratios,
   distinct counts, averages); conflicting definitions to canonicalize.
3. **Dimensions & filters** — grouping fields, fiscal/calendar dates, named filters.
4. **Relationships** — tables, join keys, fact grain, SCD2 / role-playing dims.
5. **Governance & trust** — SME sign-off, access control (RLS/masking), trusted sources.

---

## Optional Step 0 — Cortex Sense (Public Preview, November 2026)

If available, run **Cortex Sense** *before* Step 2 finishes. It auto-builds
semantic context from Snowflake metadata, query history, dbt, Tableau, and Power
BI, and surfaces **naming conflicts, metric gaps, and coverage issues** — which
makes the Step 2 mapping faster and more accurate. Mark it clearly as coming soon;
do not block the workflow on it.

---

## Exit criteria for discovery

Before moving to Step 3, you should have:
- One named baseline dashboard.
- Its tables, joins, and fact grain.
- The 3-5 questions it answers.
- Precise, owner-confirmed definitions for its key metrics.

Then proceed to `build/SKILL.md` and apply the routing rule.
