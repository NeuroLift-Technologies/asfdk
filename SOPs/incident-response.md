# SOP-NLT-003 — Incident Response
> Standard Operating Procedure · ORG-DEV-OTOI-1.0.2
> Applies to: All AI coding agents and human contributors at NeuroLift Technologies
> Effective: 2025-04-04 · Owner: Joshua W. Dorsey, Sr.

---

## Purpose

This SOP defines how to identify, respond to, and document incidents arising from AI agent activity or other operational events in NeuroLift Technologies repositories. It ensures incidents are handled consistently, transparently, and with appropriate escalation.

---

## What Constitutes an Incident

An **incident** is any unplanned event that:

| Category | Examples |
|----------|---------|
| **Governance violation** | Credentials committed to VCS; agent working without registration; session ended without handoff |
| **Security event** | Secret or credential exposed; unauthorized access detected; dependency vulnerability discovered |
| **Data integrity** | Unintended file deletion; incorrect merge; corrupted data in production |
| **Agent misbehavior** | Agent exceeds confirmed scope; agent makes architectural decisions unilaterally; agent bypasses escalation |
| **Service disruption** | CI/CD pipeline failure affecting multiple repos; workflow misconfiguration causing widespread failure |
| **Policy violation** | LLM provider hard-coded without approval; production deployment without authorization |

---

## Incident Severity Levels

| Level | Name | Description | Response Time |
|-------|------|-------------|---------------|
| **P1** | Critical | Credential exposure; production data loss; security breach | Immediate (< 1 hour) |
| **P2** | High | Governance violation with real impact; service disruption affecting multiple repos | Same day (< 4 hours) |
| **P3** | Medium | Governance violation caught before impact; agent scope creep caught early | Next business day |
| **P4** | Low | Minor policy deviation; process improvement opportunity | Within 1 week |

---

## Incident Response Process

### Step 1 — Detect and Stop

**If you are an AI agent and you discover or cause an incident:**

1. **Stop all work immediately**
2. Do not attempt to fix the incident unilaterally — this may make it worse
3. Document what happened in plain terms
4. Proceed to Step 2

### Step 2 — Assess Severity

Determine the severity level (P1–P4) using the table above. If unsure, treat it as one level higher than your best guess.

### Step 3 — Notify

**For P1 incidents:**
- Email Joshua W. Dorsey, Sr. immediately: `joshua@neurolift.tech`
- Subject line: `[P1 INCIDENT] [Repository] Brief description`
- Include: What happened, when, what systems are affected, what you've done so far

**For P2 incidents:**
- Email `joshua@neurolift.tech` with subject: `[P2 INCIDENT] [Repository] Brief description`
- Also file a GitHub Issue in the affected repository using the `agent-escalation` template
- Mark urgency as 🔴 High

**For P3–P4 incidents:**
- File a GitHub Issue in the affected repository
- Tag with `incident` label
- No immediate email required unless it escalates

### Step 4 — Contain

Take only **reversible, low-risk** containment actions without additional approval:
- Close a PR that introduced the problem (do not merge)
- Revert a specific commit on a non-production branch
- Pause an automated workflow

**Do NOT:**
- Delete files, branches, or commits without approval
- Attempt to patch production systems without approval
- Rotate credentials or keys without approval (this must be coordinated)

### Step 5 — Document

Create an incident record with the following information:

```markdown
## Incident Record

**Date:** YYYY-MM-DD HH:MM UTC
**Severity:** P1 / P2 / P3 / P4
**Discovered by:** Agent name or human name
**Repository:** NeuroLift-Technologies/REPO_NAME
**Branch/PR:** BRANCH or PR URL

### What Happened
[Clear, factual description of what occurred]

### Timeline
- HH:MM — [Event]
- HH:MM — [Event]
- HH:MM — [Containment action taken]

### Impact
[What was affected or potentially affected]

### Root Cause (if known)
[Why this happened]

### Actions Taken
[Steps already taken to contain]

### Actions Needed
[Steps still required — who owns them]

### Lessons Learned
[What should change to prevent recurrence]
```

Save the incident record as a comment in the GitHub Issue, or attach it to the escalation email.

### Step 6 — Resolve

Resolution is owned by Joshua W. Dorsey, Sr. for P1/P2 incidents. For P3/P4, the repository maintainer may resolve with Joshua's awareness.

Resolution includes:
- Confirming the incident is fully contained
- Implementing any necessary remediations
- Updating affected governance records
- Closing the incident issue with the full incident record attached

### Step 7 — Post-Incident Review

For P1 and P2 incidents, a post-incident review is required within 5 business days:
- What happened (timeline)
- Root cause analysis
- What we're changing to prevent recurrence
- Any governance or SOP updates needed

---

## Credential Exposure — Special Protocol

If credentials, tokens, API keys, or secrets are committed to any repository:

1. **Assume the secret is compromised** — treat it as a P1 immediately
2. **Do not delete the commit** — this does not remove the secret from git history and may destroy evidence
3. **Email Joshua immediately** at `joshua@neurolift.tech` with subject: `[P1 CREDENTIAL EXPOSURE] [Repository]`
4. **Do not rotate or revoke** without coordination — Josh will coordinate with the relevant service owner
5. The affected credential must be rotated out-of-band by a human, not an AI agent

---

## Agent-Specific Guidance

**If you are an AI agent and you caused the incident:**
- Do not attempt to cover it up or minimize it in your handoff record
- Document it fully and honestly
- Your transparency helps fix the problem faster and improves the framework
- Incidents caused by agents are governance improvement opportunities, not individual failures

**If you discover an incident caused by a previous agent:**
- Document it in your handoff record under `blockers`
- Do not attempt to fix it beyond containment
- Escalate per this SOP

---

## Document Control

| Field | Value |
|-------|-------|
| **SOP ID** | SOP-NLT-003 |
| **Version** | 1.0.0 |
| **Effective Date** | 2025-04-04 |
| **Owner** | Joshua W. Dorsey, Sr. |
| **Review Cycle** | Quarterly |
| **Next Review** | 2025-07-04 |
| **OTOI Alignment** | ORG-DEV-OTOI-1.0.2 |

---

*Maintained in `NeuroLift-Technologies/solidarity-framework`*
