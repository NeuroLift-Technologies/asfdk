# Active Threads — NeuroLift-Technologies/solidarity-framework
> OTOI §4.1 Step 4 · Read before starting any work to avoid conflicts
> Last updated: 2026-05-04

---

## How to Use This File

This file tracks all **current and recently completed** work threads in this repository. Before starting any task, you must:

1. Read this file in its entirety
2. Identify any active threads related to your task
3. Check for potential conflicts with in-progress work
4. Register your new thread in the **Active Threads** section below
5. Move completed threads to **Completed Threads** when done

**Update this file as part of your first commit when starting a thread, and as part of your handoff record when closing one.**

---

## Active Threads

<!-- Add new threads here. One entry per thread. -->

<!-- No active threads. -->

---

## Completed Threads

<!-- Move threads here when closed. Retain for 30 days after completion. -->

### THREAD-001 — Governance File Bootstrap
| Field | Value |
|-------|-------|
| **Thread ID** | THREAD-001 |
| **Status** | ✅ Complete |
| **Started** | 2025-04-04 |
| **Completed** | 2026-05-02 |
| **Owner** | GitHub Copilot (@copilot) — session c9d4 |
| **Branch** | `copilot/work-on-active-threads-again` |
| **Task** | Create the `sync-governance-public.yml` workflow to bootstrap governance files from solidarity-framework into the `NeuroLift-Technologies/.github` public repo |
| **Scope** | `.github/workflows/sync-governance-public.yml` — all other governance files (CLAUDE.md, AGENTS.md, docs/, templates/, SOPs/, ISSUE_TEMPLATE/agent-escalation.md, ISSUE_TEMPLATE/governance-proposal.md, .nltotoi/) already existed from prior threads |
| **Blockers** | None — workflow created. Requires `GOVERNANCE_SYNC_TOKEN` secret (PAT with `contents: write` on NeuroLift-Technologies/.github) to be configured by Joshua W. Dorsey, Sr. before the workflow can push to the target repo |
| **Related PR** | `copilot/work-on-active-threads-again` |
| **Notes** | Resumed and completed by session c9d4 per explicit user instruction. The `sync-governance-public.yml` workflow syncs AGENTS.md, NLT-DEV-OTOI.md, SOPs/, templates/, ISSUE_TEMPLATE/agent-escalation.md, ISSUE_TEMPLATE/governance-proposal.md, PULL_REQUEST_TEMPLATE/agent-contribution.md, and .nltotoi/ to NeuroLift-Technologies/.github on every push to main/master that touches those files, plus supports workflow_dispatch with a dry-run option. A human must add the GOVERNANCE_SYNC_TOKEN secret once before the first run. |

### THREAD-004 — Solidarity Framework Skills
| Field | Value |
|-------|-------|
| **Thread ID** | THREAD-004 |
| **Status** | ✅ Complete |
| **Started** | 2026-04-28 |
| **Completed** | 2026-05-02 |
| **Owner** | GitHub Copilot (@copilot) |
| **Branch** | `copilot/create-skills-for-solidarity-framework` |
| **Task** | Create standalone skill files for each Solidarity Framework component (RRT Advocate, NLT-OTOI, Sleepwalker Protocol, Unified Foundation) to enable modular adoption |
| **Scope** | `agents/rrt-advocate-skill.md`, `agents/nlt-otoi-skill.md`, `agents/sleepwalker-skill.md`, `agents/solidarity-foundation-skill.md`, `docs/active-threads.md`, `docs/agent-log/registrations/`, `docs/agent-log/handoffs/` |
| **Blockers** | None |
| **Related PR** | Branch `copilot/create-skills-for-solidarity-framework` |
| **Notes** | All four skill files verified present and complete as of 2026-05-02. Closed by GitHub Copilot session c9d2. |

### THREAD-003 — Governance Enforcement for Remote Agents
| Field | Value |
|-------|-------|
| **Thread ID** | THREAD-003 |
| **Status** | ✅ Complete |
| **Started** | 2026-04-28 |
| **Completed** | 2026-05-02 |
| **Owner** | GitHub Copilot (@copilot) |
| **Branch** | `copilot/update-deployment-instructions` |
| **Task** | Investigate root cause of VS Code Copilot Agents - Insiders not following governance; implement fixes to enforce OTOI §4.1 session start protocol for all remote agents |
| **Scope** | `.github/copilot-instructions.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/workflows/validate-governance.yml`, `docs/active-threads.md` |
| **Blockers** | None |
| **Related PR** | Branch `copilot/update-deployment-instructions` |
| **Notes** | Root cause: `.github/copilot-instructions.md` contained no OTOI governance protocol — only generic coding standards. VS Code Copilot reads this file at session start; without governance instructions there, it had no awareness of SOP-NLT-001. Three fixes: (1) copilot-instructions.md updated with full OTOI session start protocol, commit format, guardrails, escalation triggers, and handoff requirement; (2) PULL_REQUEST_TEMPLATE.md updated with governance checklist; (3) validate-governance.yml updated with agent-commit-format CI job. All three files verified complete 2026-05-02 by GitHub Copilot session c9d2. |

### THREAD-002 — Governance File Repository Scoping
| Field | Value |
|-------|-------|
| **Thread ID** | THREAD-002 |
| **Status** | ✅ Complete |
| **Started** | 2026-04-28 |
| **Owner** | GitHub Copilot (@copilot) |
| **Branch** | `copilot/update-deployment-instructions` |
| **Task** | Update all governance files pulled in from .github-private to replace generic/template references with solidarity-framework–specific values (repo name, paths, URLs) |
| **Scope** | `AGENTS.md`, `NLT-DEV-OTOI.md`, `SOPs/new-agent-onboarding.md`, `SOPs/repo-governance-setup.md`, `SOPs/incident-response.md`, `SOPs/SOPs/new-agent-onboarding.md`, `SOPs/SOPs/repo-governance-setup.md`, `SOPs/SOPs/incident-response.md`, `agents/nlt-governance-steward.md`, `.nltotoi/index/governance-files.md`, `.nltotoi/.nltotoi/README.md`, `.nltotoi/.nltotoi/index/governance-files.md`, `.nltotoi/.nltotoi/proposals/validation-roadmap.md`, `nltotoi.json`, `docs/agent-log/README.md`, `docs/escalations/README.md`, `ISSUE_TEMPLATE/governance-proposal.md`, `rrt-advocate/CLAUDE.md`, `file-structure.md`, `agents/swe-agent.md` (new) |
| **Blockers** | None |
| **Related PR** | Branch `copilot/update-deployment-instructions` |
| **Notes** | Governance session artifacts (registration, this thread entry, handoff record) were filed retroactively per §2.1 transparency requirement. Work commits: `8b594e6`, `92618ca`. No architectural decisions were made; all changes were scoping/naming corrections only. |

### THREAD-ASK-remove-aimybox — Remove Aimybox / voice interface layer
| Field | Value |
|-------|-------|
| **Thread ID** | THREAD-ASK-remove-aimybox |
| **Status** | ✅ Complete |
| **Completed** | 2026-04-24 |
| **Owner** | CURSOR |
| **Branch** | `cursor/review-fix-refresh-and-build-repo-5f72` |
| **Summary** | Removed voice integration module and all Aimybox/voice routing from unified core; RRT-to-TOI-OTOI path uses `rrt_to_framework` + `ingest_rrt_crisis_context`; documentation and config updated; `tests/integration_test.py` 4/4. |

### THREAD-ASK-align-solidarity-kit — Align PR with Agent Solidarity Kit (main)
| Field | Value |
|-------|-------|
| **Thread ID** | THREAD-ASK-align-solidarity-kit |
| **Status** | ✅ Complete |
| **Completed** | 2026-04-21 |
| **Owner** | CURSOR |
| **Branch** | `cursor/review-fix-refresh-and-build-repo-5f72` |
| **Summary** | Documentation and messaging aligned to Agent Solidarity Kit; unified core package renamed to `core_coordination` to avoid `coordination` namespace clash with `rrt-advocate`; (superseded) earlier voice stub removed in THREAD-ASK-remove-aimybox. |

---

## Thread Registry Format

When adding a new thread, copy this template:

```markdown
### THREAD-XXX — [Short Title]
| Field | Value |
|-------|-------|
| **Thread ID** | THREAD-XXX |
| **Status** | 🟡 In Progress / 🔴 Blocked / ✅ Complete |
| **Started** | YYYY-MM-DD |
| **Owner** | [Agent name or human] |
| **Branch** | `branch-name` |
| **Task** | [One-sentence description] |
| **Scope** | [Files or areas affected] |
| **Blockers** | [None, or description] |
| **Related PR** | [PR URL or TBD] |
| **Notes** | [Any relevant context for future agents] |
```

---

## Conflict Avoidance Rules

- **One agent per thread** — if you need to hand off a thread, write a handoff record first
- **Do not modify files owned by another active thread** without explicit coordination
- **If you see a conflict**, stop and escalate via the `agent-escalation` issue template
- **Stale threads** (no update in 7+ days) should be escalated to Joshua W. Dorsey, Sr. for disposition

---

*This file is part of the ORG-DEV-OTOI-1.0.0 governance framework for NeuroLift Technologies.*
