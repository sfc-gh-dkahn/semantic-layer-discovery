# Step 4 — Create a test agent

Wire a test agent to the Semantic View from Step 3. Sharing and certification
wait for Step 5.

---

## Do this

1. **Create the agent through `agent-studio` (REQUIRED).** It must be a real
   object grounded on the view's verified FQN, confirmed to exist before Step 5.
2. **Write its instructions:**
   - **Tone** for this audience.
   - **Scope:** the baseline domain only, for now.
   - **Business rules:** only defaults confirmed in the baseline record. Tableau
     `usage_context` or screenshots can support them; Power BI exports carry no
     page, slicer, or visual context. A visible filter or a repeated `WHERE`
     clause is test context, not a default. No confirmed default → set none.
   - **Exclusions:** name each metric outside the accepted scope and tell the
     agent to say it can't answer rather than approximate. Test that it does.
3. **Test that answers stay inside the approved scope.**
4. **Check access as a real user.** Grants, row access policies, and masking
   must work in the agent's execution context. BI tool security rules don't
   migrate with the metadata: list any that need a Snowflake policy and add it.
   Test with a non-admin user before sharing, and
   never promise the BI tool's security carries over.
5. **Optional:** for customer- or public-facing agents, add Cortex Guardrails.

## Done when

- A real test agent uses the Semantic View.
- Tone, scope, rules, and exclusions are in its instructions.
- A non-admin test user sees the right data.

Go to `04-validate/SKILL.md`.
