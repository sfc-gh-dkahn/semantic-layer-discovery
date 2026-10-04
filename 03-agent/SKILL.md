# Step 4 — Create a Cortex Agent on the candidate Semantic View

Wire a test agent to the deployed, coverage-reviewed Semantic View from Step 3.
Required metrics must be implemented for the approved scope; certification and
broader sharing wait for Step 5 result validation.

---

## What to do

1. **Point the agent at the candidate Semantic View.** Use its verified FQN and
   the approved coverage scope as grounding; test whether answers respect it.

2. **Add natural-language instructions** for:
   - **Tone** — how answers should read for this audience.
   - **Scope** — what's in/out of bounds (keep it to the baseline domain first).
   - **Business rules** — use confirmed definitions/defaults in the baseline
     record. Tableau `usage_context` or supplied screenshots can support these;
     do not assume Power BI exports contain page/slicer/visual context.
     A visible selection or repeated query `WHERE` clause is test context, not
     automatically a permanent default. If no default is confirmed, set none.
   - **Known exclusions** — name metrics outside the accepted scope and instruct
     the agent to say it cannot answer rather than approximate. Test this behavior.

3. **Verify the execution identity and governance.** Snowflake grants, row access
   policies, and masking must behave as intended in the agent's actual execution
   context. BI-specific security rules are not automatically migrated by metadata
   import. Identify any required gap and verify access with a non-admin test user
   before sharing; do not promise governance equivalence based on import alone.

## Optional: guardrails

For customer- or public-facing assistants, consider attaching **Cortex Guardrails**
so responses stay safe, neutral, and on-topic before they reach an end user.

## Delegation (REQUIRED — actually create the agent)

You **MUST** invoke the **`agent-studio`** skill to create a
real Cortex Agent object grounded on the candidate Semantic View — not describe
how one would be created. This skill sequences *when* to do it and *what* to wire
in; the agent object must actually be created and confirmed to exist before Step
5.

## Exit criteria

- A real test agent grounded on the deployed, coverage-reviewed Semantic View.
- NL instructions for tone, scope, and business rules in place.
- Confirmed that RBAC / RLS / masking behave correctly for a non-admin test user.

Proceed to `04-validate/SKILL.md` (Step 5).
