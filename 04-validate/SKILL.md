# Step 5 — Validate, accept, share

Prove the agent against the baseline from Step 1, lock in what works with
Verified Queries, then share it.

---

## 5a. Validate against the baseline

1. **Use the baseline record**; no new discovery. Ask questions that cover
   every required metric, including ones implemented separately in SQL. Don't
   assume the importer brought over page or visual context; use the record's.
2. **Compare like with like:** the same filters, date range, refresh cutoff, and
   access identity as the expected results. Check detail rows, totals, and key
   filter variants (especially ratios, LOD, and time calculations). Agree on
   rounding and tolerance up front. One matching tile is not enough.
3. **Diagnose mismatches in order:** data freshness and access → filter context
   → grain and joins → the metric itself. Fix only from supported definitions,
   through agent-studio, then re-run the coverage gate and the affected result checks. Never tweak a formula
   until it matches a screenshot.
4. **Missing expected results?** Ask for only that. Objects stay saved; parity
   waits.
5. **No dashboard?** Validate an agreed reference query or result set and label
   it **reference validation**, not dashboard replacement. A query being popular
   doesn't make it the reference.

## 5b. Add Verified Queries

Add the baseline questions, and any variants that tripped the agent, as
Verified Queries once their SQL and results pass. They guide Cortex Analyst;
they don't guarantee future answers. To mine query history for more,
use agent-studio's `vqr_suggestions` workflow.

## 5c. Report one outcome

| Outcome | Meaning | Next |
|---|---|---|
| Passed | Every required baseline question passes | Get the customer's acceptance |
| Partial | The customer accepted a smaller scope and every question in it passes | Keep the original gaps; label the delivery partial |
| Blocked | Results, definitions, permissions, or approvals are missing, or a comparison fails | Record the next action; don't share or start Step 6 |

Call the scope "validated" only after acceptance. If the customer needs formal
certification, follow their process with their authorization; don't apply a
certification tag yourself.

## 5d. Share it

After acceptance and the Step 4 non-admin check, share the agent with named
roles (never PUBLIC) in **CoWork**. Step 6 offers an app or dashboard.

## 5e. Hand over the open definitions

If any metric is open (excluded, blocked, or undefined), give the user this
list for its owners, from the Gaps and 3c coverage table. Also give it when a
run stops.

| Metric | Page | Why open | Evidence | Ask | Owner |
|---|---|---|---|---|---|
| Dashboard name | Baseline page | Not in model, didn't convert, no source, or excluded | Exact formula or "none" | One standalone question | Name or "unknown" |

It's a note to chase later, not a blocker: don't wait for answers. When they
arrive, add those metrics from 3c.

## Done when

- The agent answers every accepted question with matching results. The record
  states dashboard parity or reference validation, and any partial scope.
- Verified Queries are added.
- The agent is shared; a named owner accepts the tested scope and knows its
  gaps. Pick the next dashboard only after this; it doesn't block delivery.

Go to `05-app/SKILL.md`.
