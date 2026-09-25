# Step 4 — Create a Cortex Agent on the certified Semantic View

Wire a Cortex Agent to the certified Semantic View from Step 3. This is what turns
a data model into an **agentic BI experience** the business can talk to.

---

## What to do

1. **Point the agent at the certified Semantic View.** The view is the agent's
   grounding — it answers only from governed definitions, not guesses.

2. **Add natural-language instructions** for:
   - **Tone** — how answers should read for this audience.
   - **Scope** — what's in/out of bounds (keep it to the baseline domain first).
   - **Business rules** — standing assumptions, default date ranges, canonical
     metric choices from Step 2c.

3. **Governance travels with every answer.** The agent automatically inherits:
   - **RBAC** — users see only what their role permits.
   - **Row-level security** — row access policies still apply.
   - **Masking** — masked columns stay masked in answers.

   You do not re-implement governance at the agent layer; it flows from the
   underlying Snowflake objects. Call this out to the customer — it's a key
   trust/compliance selling point.

## Optional: guardrails

For customer- or public-facing assistants, consider attaching **Cortex Guardrails**
so responses stay safe, neutral, and on-topic before they reach an end user.

## Delegation

For agent creation/versioning mechanics, use the **`agent-studio`** skill. This
skill just sequences *when* to do it and *what* to wire in.

## Exit criteria

- A Cortex Agent grounded on the certified Semantic View.
- NL instructions for tone, scope, and business rules in place.
- Confirmed that RBAC / RLS / masking behave correctly for a non-admin test user.

Proceed to `validate/SKILL.md` (Step 5).
