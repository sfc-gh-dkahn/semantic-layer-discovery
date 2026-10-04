# Step 5 — Validate, iterate, and ship

Prove the agent against the **original baseline dashboard** from Step 1, harden it
with Verified Queries, then surface it where users work. One dashboard replaced is
the fastest proof point for broader adoption.

---

## 5a. Validate against the baseline

- Use the confirmed **baseline record**, not a fresh discovery round. Ask the
  agent the agreed questions covering every required metric, including separately
  implemented formulas. Do not assume the importer supplied all visual context.
- Compare with the recorded expected results under the same filters, date range,
  refresh cutoff, and access identity. Check relevant detail grain and totals,
  plus important filter variants (especially ratios, LOD, and time calculations).
  Agree any rounding/tolerance explicitly; one matching tile is not sufficient.
- Diagnose mismatches in this order: data freshness/access, filter context, grain
  and joins, then the metric implementation. Fix only from supported definitions
  and evidence through agent-studio; re-run affected coverage and result checks.
  Never tune a formula merely until a screenshot matches.
- If expected results are missing, request only that evidence. Candidate objects
  can remain saved, but parity is blocked. With no dashboard, validate an agreed
  reference query/result set; label this **reference validation**, not dashboard
  replacement. Query-history popularity alone cannot establish the reference.

## 5b. Add Verified Queries for edge cases

- Encode the baseline questions — and any tricky variants that tripped the agent —
  as **Verified Queries (VQRs)** only after their SQL/results pass validation.
  VQRs guide Cortex Analyst; they do not guarantee every future answer is correct.
- Delegate VQR generation/seeding to the **`agent-studio`** skill's
  `vqr_suggestions` workflow if you want it to mine query history for candidates.

## 5c. Accept the validated scope, then ship

Report one outcome with the evidence and remaining exclusions:

| Outcome | Action |
|---|---|
| Passed | All required baseline questions pass; confirm customer acceptance |
| Partial | Customer explicitly accepted a reduced scope and every question in that subset passes; retain the original gaps and label the delivery as partial |
| Blocked | Required results, definitions, permissions, or approvals are missing, or a required comparison fails; record the next action and stop before sharing/Step 6 |

Only after acceptance describe the tested scope as validated. If formal
certification is required, follow the customer's certification process and obtain
authorization; this workflow does not apply a certification tag automatically.

Surface the accepted agent for named recipient roles (never default to PUBLIC),
after the non-admin access check from Step 4 passes:
- **CoWork** — business users chat with the agent directly.
- **Streamlit app, App Runtime app, or Dashboard (Private Preview)** — offered next in **Step 6**
  (`05-app/SKILL.md`); the customer picks one first.

## 5d. Then — and only then — expand

Once the single baseline is replaced and trusted, repeat the path with the next
dashboard. Resist widening scope before the first proof point lands.

---

## Exit criteria

- Agent answers all questions in the accepted scope with matching results;
  validation type (dashboard parity or reference) and any partial scope are explicit.
- VQRs added for the baseline questions and known edge cases.
- Agent surfaced in CoWork (or an app), with a named owner.
- A named owner accepts the tested scope and knows the remaining gaps. Identify
  a next dashboard only after this proof point; it is not a delivery blocker.
- Then proceed to **Step 6** (`05-app/SKILL.md`), which asks the customer what to
  build (or to skip) before building anything.

## Optional follow-ups

- Schedule this as a repeatable engagement per dashboard.
- If governance/trust is a stakeholder concern, revisit `03-agent/SKILL.md`
  guardrails and confirm RBAC/RLS/masking behavior with the customer's security team.
