# Escalation Record
> ORG-DEV-OTOI-1.0.2 · OTOI §4.3 — Escalation Protocol
> Use this template when filing an escalation. Also file a GitHub Issue using `ISSUE_TEMPLATE/agent-escalation.md`.

---

## Escalation Metadata

| Field | Value |
|-------|-------|
| **Date** | YYYY-MM-DD |
| **Agent Name** | AGENT_NAME |
| **Session ID** | SESSION_ID |
| **Repository** | NeuroLift-Technologies/REPO_NAME |
| **Branch** | BRANCH_NAME |
| **Active Thread ID** | THREAD_ID |
| **Escalation Urgency** | 🔴 High / 🟡 Medium / 🟢 Low |
| **GitHub Issue URL** | ISSUE_URL (after filing) |

---

## What Triggered This Escalation

> Describe the specific trigger. Reference the OTOI trigger list if applicable.
> Example: "This task requires selecting between two LLM providers, which is an architectural decision requiring Joshua's approval per OTOI §4.3."

REPLACE_WITH_TRIGGER_DESCRIPTION

**OTOI Trigger Category (check one):**
- [ ] Architecture or system design decision
- [ ] New external service integration
- [ ] LLM provider selection or hard-coding
- [ ] Production deployment
- [ ] Security-affecting change
- [ ] Governance framework modification
- [ ] Scope expansion beyond confirmed task
- [ ] Ethical concern
- [ ] Ambiguous requirements
- [ ] Other: ___________________

---

## Context

> Provide enough context for Joshua (or another human) to make a decision without having to re-read the full codebase.

### What the task originally required:
REPLACE_WITH_ORIGINAL_TASK

### What I discovered that triggered the escalation:
REPLACE_WITH_DISCOVERY

### Options identified (if any):

**Option A:** DESCRIBE_OPTION_A
- Pros: PROS
- Cons: CONS

**Option B:** DESCRIBE_OPTION_B
- Pros: PROS
- Cons: CONS

---

## Decision Needed

> State the exact question Joshua needs to answer.

REPLACE_WITH_SPECIFIC_QUESTION

---

## Work Paused

I have **stopped work** on the following until this is resolved:
- PAUSED_ITEM_1
- PAUSED_ITEM_2

---

## Status

- [ ] Escalation filed as GitHub Issue
- [ ] Email sent to `joshua@neurolift.tech`
- [ ] Blocker documented in handoff record
- [ ] Awaiting decision
- [ ] Decision received — proceeding
- [ ] Decision received — closing without action

**Decision received (if applicable):**
> REPLACE_WITH_DECISION_TEXT

---

*This escalation record is part of the ORG-DEV-OTOI-1.0.2 governance framework for NeuroLift Technologies.*
