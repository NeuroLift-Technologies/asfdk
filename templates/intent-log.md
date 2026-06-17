# Intent Log
> ORG-DEV-OTOI-1.0.2 · Agent Intent Transparency Record
> Use this template to document your planned actions before executing them for significant or irreversible changes.

---

## Intent Log Metadata

| Field | Value |
|-------|-------|
| **Date** | YYYY-MM-DD |
| **Agent Name** | AGENT_NAME |
| **Session ID** | SESSION_ID |
| **Repository** | NeuroLift-Technologies/REPO_NAME |
| **Branch** | BRANCH_NAME |
| **Active Thread ID** | THREAD_ID |

---

## Task Summary

> Restate the confirmed task in one or two sentences. This is your understanding — not the original prompt verbatim.

REPLACE_WITH_TASK_SUMMARY

---

## Planned Actions

> List every significant action you plan to take, in order. Be specific about files, commands, and decisions.

| # | Action | Files/Commands Affected | Reversible? |
|---|--------|------------------------|-------------|
| 1 | DESCRIBE_ACTION_1 | FILE_OR_COMMAND | Yes / No |
| 2 | DESCRIBE_ACTION_2 | FILE_OR_COMMAND | Yes / No |
| 3 | DESCRIBE_ACTION_3 | FILE_OR_COMMAND | Yes / No |

---

## Assumptions

> List any assumptions you are making about the codebase, requirements, or environment.

1. ASSUMPTION_1
2. ASSUMPTION_2

---

## Out of Scope (Explicitly Excluded)

> List anything you noticed that you are intentionally NOT doing, and why.

- EXCLUDED_ITEM_1 — REASON
- EXCLUDED_ITEM_2 — REASON

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| RISK_1 | Low / Medium / High | Low / Medium / High | MITIGATION |
| RISK_2 | Low / Medium / High | Low / Medium / High | MITIGATION |

---

## Escalation Check

Before proceeding, I confirm:

- [ ] This task does NOT require an architectural decision
- [ ] This task does NOT introduce new external service dependencies
- [ ] This task does NOT select or hard-code an LLM provider
- [ ] This task does NOT touch production systems
- [ ] This task does NOT expand beyond confirmed scope
- [ ] No escalation is required — proceeding

**OR**

- [ ] Escalation is required — see `templates/escalation.md` for this session

---

## Execution Notes

> Fill this section in as you execute. Note anything that deviated from the plan.

REPLACE_WITH_EXECUTION_NOTES

---

*This intent log is part of the ORG-DEV-OTOI-1.0.2 governance framework for NeuroLift Technologies.*
