# Agent Log — NeuroLift-Technologies/solidarity-framework

This directory contains the persistent audit trail of all AI agent sessions that have worked in this repository. It is a core component of the ORG-DEV-OTOI-1.0.2 governance framework.

---

## Directory Structure

```
docs/agent-log/
├── README.md              # This file
├── registrations/         # Agent self-registration records (one per session)
│   └── {YYYY-MM-DD}-{agent-name}-{session-id}.json
└── handoffs/              # Session handoff records (one per session)
    └── {YYYY-MM-DD}-{session-id}.json
```

---

## Registrations

Every agent session must begin with a self-registration, placed in `registrations/`. Registration is required by OTOI §3 before any work begins.

**Template:** `templates/agent-registration.json` (in repository root)

**File naming convention:**
```
{YYYY-MM-DD}-{agent-name}-{session-id}.json
```

**Example:**
```
2025-04-04-claude-a1b2c3d4.json
```

Registrations document:
- Which agent platform and version is working
- What session this is
- What repository and branch are being worked on
- What the agent's self-reported capabilities and limitations are
- That OTOI has been acknowledged

---

## Handoffs

Every agent session must end with a handoff record, placed in `handoffs/`. This is non-negotiable per OTOI §5. A session that ends without a handoff record is a governance violation.

**Template:** `templates/handoff-record.json` (in repository root)

**File naming convention:**
```
{YYYY-MM-DD}-{session-id}.json
```

**Example:**
```
2025-04-04-a1b2c3d4.json
```

Handoffs document:
- All work completed and in-progress
- Any blockers encountered
- Decisions made and their rationale
- What the next agent needs to know
- All files modified
- Test status and PR URL

---

## Retention Policy

- **Registrations:** Retained indefinitely as audit trail
- **Handoffs:** Retained indefinitely as audit trail
- **Archiving:** Periodically, old records may be archived to `docs/agent-log/archive/` by a governance maintainer

---

## Governance Reference

| Document | Location |
|----------|----------|
| OTOI Contract | `NLT-DEV-OTOI.md` |
| Agent Coordination | `AGENTS.md` |
| Onboarding SOP | `SOPs/new-agent-onboarding.md` |
| Registration Template | `templates/agent-registration.json` |
| Handoff Template | `templates/handoff-record.json` |

---

*This directory is part of the ORG-DEV-OTOI-1.0.2 governance framework for NeuroLift Technologies.*
