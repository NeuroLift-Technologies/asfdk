# SOP-NLT-001 — New Agent Onboarding
> Standard Operating Procedure · ORG-DEV-OTOI-1.0.2
> Applies to: All AI coding agents working in any NeuroLift Technologies repository
> Effective: 2025-04-04 · Owner: Joshua W. Dorsey, Sr.

---

## Purpose

This SOP defines the mandatory 8-step onboarding process for all AI coding agents joining any NeuroLift Technologies repository. No agent begins substantive work until all 8 steps are complete and confirmed.

The onboarding process ensures:
- Every agent understands the governance framework before writing code
- Every agent is registered and traceable
- Every session has a defined start and end
- Handoffs are complete and usable
- The Solidarity Framework is understood and upheld

---

## Scope

This SOP applies to:
- All AI coding agents (Claude, Codex, Gemini, Cursor, Copilot, and others)
- All repositories in the NeuroLift Technologies GitHub organization
- Both automated pipeline sessions and interactive human-supervised sessions

---

## Prerequisites

- Access to the target repository
- Ability to read `NLT-DEV-OTOI.md` in `NeuroLift-Technologies/solidarity-framework` (or a summary provided by a human)
- Knowledge of your agent name, platform, and version

---

## The 8-Step Onboarding Process

---

### Step 1 — Read NLT-DEV-OTOI.md

**Location:** `NLT-DEV-OTOI.md` in `NeuroLift-Technologies/solidarity-framework`

Read the full document. This is the **constitutional document** for all NLT agent work — the canonical org-level coding agent contract.

**Pay particular attention to:**
- **Section 1** — Purpose and scope of the framework
- **Section 4** — Agent behavior standards
- **Section 4.3** — Escalation triggers (mandatory to memorize)
- **Section 4.4** — Non-negotiable guardrails
- **Section 5** — Handoff protocol
- **Section 8** — Ethical commitments

**Confirm understanding of:**
- [ ] Escalation triggers (§4.3) — know when you must stop and escalate
- [ ] Guardrails (§4.4) — know what is never permissible
- [ ] Handoff protocol (§5) — know what you must produce at session end
- [ ] Ethical commitments (§8) — know your ethical floor

---

### Step 2 — Read AGENTS.md

**Location:** `AGENTS.md` in your target repository (also at `NeuroLift-Technologies/solidarity-framework/AGENTS.md` for the canonical version)

Read the full `AGENTS.md`. This is the **internal coordination gateway** — it defines how agents coordinate, what the non-negotiable guardrails are, and how multi-agent sessions work.

**Confirm understanding of:**
- [ ] The Solidarity Framework — its 6 principles
- [ ] Commit format: `[AGENT_NAME] type(scope): description`
- [ ] When to escalate vs. when to proceed
- [ ] Multi-agent session rules
- [ ] Non-negotiable guardrails list

---

### Step 3 — Read the Repo's CLAUDE.md

**Location:** `CLAUDE.md` in the **specific repository you'll be working in**

> ⚠️ Read the target repo's `CLAUDE.md`, not this repo's. Each repo has its own.

This gives you:
- Repository identity and purpose
- What is in scope vs. what requires escalation
- Repo-specific conventions and file naming
- Additional required reading for that repo

**Confirm:**
- [ ] You know which repository you're working in
- [ ] You've read and understood the repo-specific instructions
- [ ] You've noted any additional required reading listed

---

### Step 4 — Read docs/active-threads.md

**Location:** `docs/active-threads.md` in your target repository

This file tracks current and recent work. You must understand it to avoid duplicating effort or conflicting with in-progress work.

**Confirm:**
- [ ] You've read all active thread entries
- [ ] You've identified any threads related to your task
- [ ] There are no blockers or conflicts you need to resolve before starting
- [ ] You know who owns any related active threads

> If you find a conflict, **stop** and escalate before proceeding.

---

### Step 5 — Complete Self-Registration

**Template:** `templates/agent-registration.json`
**Save to:** `docs/agent-log/registrations/`
**File name:** `{YYYY-MM-DD}-{agent-name}-{session-id}.json`

Fill in every field of the registration template. Commit the registration file as your **first commit** of the session.

Required fields include:
- Agent name, platform, and version
- Session ID (unique per session)
- Entry date and entry point
- Working repository and branch
- Task summary
- Active thread ID
- Self-reported capabilities and known limitations
- Acknowledgement of OTOI, escalation protocol, commit format, and handoff requirement

**Your commit for this step:**
```
[AGENT_NAME] chore(governance): register agent session {session-id}
```

---

### Step 6 — Confirm Task Scope

Before writing any code, describe your understanding of the task to the human and explicitly ask:

> *"Is this the full scope of the task, or are there additional requirements I should know about?"*

Wait for explicit human confirmation before proceeding.

**Document:**
- [ ] Human has confirmed scope
- [ ] You've noted any out-of-scope items you identified
- [ ] No architectural decisions are embedded in the task

**Escalation check — escalate to Joshua W. Dorsey, Sr. if the task involves:**
- Architecture or system design decisions
- New external service integrations
- Production deployments
- LLM provider selection or hard-coding
- Security-affecting changes
- Scope beyond what a human has explicitly confirmed

---

### Step 7 — Begin Work with Correct Commit Format

You are now cleared to begin work. Every commit must follow this exact format:

```
[AGENT_NAME] type(scope): description
```

**Valid types:** `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`

**Examples:**
```
[CLAUDE] feat(auth): add OAuth2 login flow
[CLAUDE] fix(api): resolve null pointer in user endpoint
[CLAUDE] chore(governance): add repo governance stubs (ORG-DEV-OTOI-1.0.2)
[CODEX] docs(readme): update setup instructions
```

> Commit format is enforced from your very first commit. No exceptions.

During work:
- Update `docs/active-threads.md` to show your thread as active
- Log significant decisions in the intent log (`templates/intent-log.md`)
- Escalate immediately if you encounter any escalation trigger
- Do not proceed past blockers — document them and pause

---

### Step 8 — End Session with Handoff Record

**This step is mandatory. No session ends without a handoff record.**

**Template:** `templates/handoff-record.json`
**Save to:** `docs/agent-log/handoffs/`
**File name:** `{YYYY-MM-DD}-{session-id}.json`

The handoff record must include:

| Field | Requirement |
|-------|-------------|
| `work_completed` | Every completed deliverable |
| `work_in_progress` | Every in-progress item (never leave work undocumented) |
| `blockers` | Any unresolved blockers |
| `decisions_made` | Every decision and its rationale |
| `decisions_pending` | Decisions still needed and who owns them |
| `escalations` | Any escalations and their current status |
| `next_agent_notes` | Freeform context for the next agent |
| `files_modified` | Every file touched |
| `files_created` | Every file created |
| `files_deleted` | Every file deleted |
| `tests_run` | Tests run (or 'None') |
| `tests_passing` | Boolean |
| `pr_url` | PR URL if applicable |

**Your commit for this step:**
```
[AGENT_NAME] chore(governance): write handoff record {session-id}
```

Also update `docs/active-threads.md` to reflect your thread's final status.

---

## Onboarding Completion Checklist

Before beginning substantive work, confirm all 8 steps are complete:

- [ ] Step 1: Read `NLT-DEV-OTOI.md` — understood §1, §4, §4.3, §4.4, §5, §8
- [ ] Step 2: Read `AGENTS.md` — understood Solidarity Framework, commit format, escalation
- [ ] Step 3: Read repo's `CLAUDE.md` — understood repo-specific context and conventions
- [ ] Step 4: Read `docs/active-threads.md` — no conflicts identified
- [ ] Step 5: Registration filed to `docs/agent-log/registrations/` and committed
- [ ] Step 6: Scope confirmed with human
- [ ] Step 7: Work begun with correct commit format
- [ ] Step 8: Handoff record filed before session ends

---

## Quick Reference Card

```
=== NLT AGENT ORIENTATION ===

OTOI Version:   ORG-DEV-OTOI-1.0.2
SOP:            SOP-NLT-001

COMMIT FORMAT:  [AGENT_NAME] type(scope): description
VALID TYPES:    feat | fix | docs | refactor | chore | test | ci

ESCALATE TO:    Joshua W. Dorsey, Sr.
EMAIL:          joshua@neurolift.tech
TRIGGER WHEN:   Architecture · New integrations · LLM provider · Production
                Security changes · Scope expansion · Ethical concerns

END WITH:       Handoff record in docs/agent-log/handoffs/
                No session ends without a handoff.

KEY DOCS:
  OTOI:         NLT-DEV-OTOI.md
  AGENTS:       AGENTS.md
  THREADS:      docs/active-threads.md
  REGISTER:     templates/agent-registration.json
  HANDOFF:      templates/handoff-record.json
==============================
```

---

## Document Control

| Field | Value |
|-------|-------|
| **SOP ID** | SOP-NLT-001 |
| **Version** | 1.0.0 |
| **Effective Date** | 2025-04-04 |
| **Owner** | Joshua W. Dorsey, Sr. |
| **Review Cycle** | Quarterly |
| **Next Review** | 2025-07-04 |
| **OTOI Alignment** | ORG-DEV-OTOI-1.0.2 |

---

*Maintained in `NeuroLift-Technologies/solidarity-framework`*
