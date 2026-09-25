# Step 5 — Validate, iterate, and ship

Prove the agent against the **original baseline dashboard** from Step 1, harden it
with Verified Queries, then surface it where users work. One dashboard replaced is
the fastest proof point for broader adoption.

---

## 5a. Validate against the baseline

- Take the **3-5 questions** the baseline dashboard answers (Step 2b) and ask the
  agent each one.
- Compare the agent's numbers to the dashboard's. They should match.
- For any mismatch, trace it: usually a metric definition (Step 2c), a fact-grain
  issue, or a missing filter in the Semantic View. Fix in the view, re-test.

## 5b. Add Verified Queries for edge cases

- Encode the baseline questions — and any tricky variants that tripped the agent —
  as **Verified Queries (VQRs)**. VQRs steer Cortex Analyst toward the correct SQL
  and lock in accuracy for the questions that matter most.
- Delegate VQR generation/seeding to the **`agent-studio`** skill's
  `vqr_suggestions` workflow if you want it to mine query history for candidates.

## 5c. Ship it

Surface the validated agent where the business already works:
- **Snowflake Intelligence (CoWork)** — business users chat with the agent directly.
- **Cortex Code** — scaffold a lightweight app around the agent if a custom UI is
  wanted.

## 5d. Then — and only then — expand

Once the single baseline is replaced and trusted, repeat the path with the next
dashboard. Resist widening scope before the first proof point lands.

---

## Exit criteria

- Agent answers the baseline questions with numbers matching the dashboard.
- VQRs added for the baseline questions and known edge cases.
- Agent surfaced in Snowflake Intelligence (or an app), with a named owner.
- A clear "next dashboard" candidate identified for the second iteration.

## Optional follow-ups

- Schedule this as a repeatable engagement per dashboard.
- If governance/trust is a stakeholder concern, revisit `agent/SKILL.md`
  guardrails and confirm RBAC/RLS/masking behavior with the customer's security team.
