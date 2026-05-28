# CLAUDE.md — NeuroLift-Technologies/asfdk
> OTOI Compliance File · ORG-DEV-OTOI-1.0.0 · Step 3 of Agent Onboarding (SOP-NLT-001)

---

## Repository Identity

| Field              | Value                                                     |
|--------------------|-----------------------------------------------------------|
| **Repository**     | `NeuroLift-Technologies/asfdk`                            |
| **Visibility**     | Private                                                    |
| **Purpose**        | Agent Solidarity Framework Development Kit (ASFDK) — Unified agent development platform: ASFDK core layer, coding-agent operations hub, and Cloudflare agent development resources |
| **OTOI Version**   | ORG-DEV-OTOI-1.0.0                                        |
| **Governing SOP**  | SOP-NLT-001 (`SOPs/new-agent-onboarding.md`)              |
| **Components**     | RRT Advocate, NLT-OTOI, Sleepwalker Protocol, VibeVoice, Agent Ops Hub, Cloudflare Dev Resources |

---

## Purpose of This Repository

The **asfdk** repository is the **Agent Solidarity Framework Development Kit (ASFDK)** — the unified agent development platform for NeuroLift Technologies. It serves three interconnected purposes:

### 1. ASFDK Core Layer (layer between the model and the agent)
- **RRT Advocate** (`rrt-advocate/`) — Crisis intervention and immediate safety protocols
- **NLT-OTOI Framework** (`nlt-otoi/`) — Interaction governance and orchestration
- **Sleepwalker Protocol** (`sleepwalker/`) — Emotional continuity across sessions
- **VibeVoice** — Open-source frontier voice AI (ASR + TTS) — see [`NeuroLift-Technologies/VibeVoice`](https://github.com/NeuroLift-Technologies/VibeVoice)
- **Unified Core** (`unified-core/`) — Integration layer connecting all components

### 2. Coding-Agent Operations Hub
- **Agent & Skill Profiles** (`agents/`) — Org-wide custom agent and skill definitions
- **Governance SOPs** (`SOPs/`) — Standard operating procedures for agent onboarding, repo setup, and incident response
- **Templates** (`templates/`) — OTOI-compliant registration and handoff artifacts
- **CI Workflows** (`.github/workflows/`) — Automated governance validation and enforcement

### 3. Cloudflare Agent Development Platform
- **Agent Reference Links** (`links.md`) — Curated Cloudflare Workers, Agents SDK, and MCP resources
- **MCP Server Configuration** (`mcp-config.yaml`) — Ready-to-use GitHub and Cloudflare MCP configs
- **Hosting** (`hosting/`) — Web application layer for agent-facing interfaces

All agents developed by NeuroLift Technologies **must** use this kit as the layer between the AI model and the agent.

---

## What Agents May and May Not Do Here

### ✅ In Scope (proceed after task confirmation)
- Update integration code in `unified-core/`
- Add tests for any component
- Update documentation in `docs/`
- Update governance tracking files in `docs/active-threads.md`
- Add agent registration and handoff records to `docs/agent-log/`
- Minor documentation improvements (typos, clarity, formatting)
- Bug fixes within existing component integrations

### 🔴 Out of Scope — Escalate to Joshua W. Dorsey, Sr.
- Modifying the governance framework itself (OTOI, AGENTS.md, SOPs)
- Adding or removing core components (rrt-advocate, nlt-otoi, sleepwalker)
- Introducing new external service integrations or LLM provider dependencies
- Architectural decisions about component interaction patterns
- Changes to crisis intervention logic (`rrt-advocate/src/rrt_advocate.py`)
- Changes to crisis thresholds (`rrt-advocate/config/crisis_thresholds.yaml`)
- Production deployment decisions
- Changes to the Solidarity Framework principles

---

## Additional Required Reading (Step 3 checklist)

Before beginning work, confirm you have read:

- [ ] `NLT-DEV-OTOI.md` — repo-local governance contract (read first)
- [ ] `AGENTS.md` — coordination gateway and guardrails
- [ ] `SOPs/new-agent-onboarding.md` — onboarding process SOP-NLT-001
- [ ] `docs/active-threads.md` — current work in progress

---

## Repo-Specific Conventions

### File Naming
- Governance templates: `templates/{type}.json` or `templates/{type}.md`
- Agent registrations: `docs/agent-log/registrations/{YYYY-MM-DD}-{agent-name}-{session-id}.json`
- Handoff records: `docs/agent-log/handoffs/{YYYY-MM-DD}-{session-id}.json`

### Commit Format (mandatory)
```
[AGENT_NAME] type(scope): description
```
Valid types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`

Examples for this repo:
```
[CLAUDE] feat(unified-core): add sleepwalker protocol integration
[COPILOT] fix(rrt-advocate): correct crisis threshold handling
[CODEX] docs(asfdk): update architecture diagram
```

### Technology Stack
- **Python 3.10+** — Primary language for all components
- **TypeScript** — Sleepwalker Protocol TypeScript implementation
- **AsyncIO** — Async processing framework
- **PyYAML** — Configuration management
- **pytest** — Testing framework

### Key Files
- `unified-core/neurolift_foundation.py` — Main foundation class
- `unified-core/integration/` — Component integration modules
- `rrt-advocate/src/rrt_advocate.py` — Crisis intervention engine
- `nlt-otoi/src/fusion/` — OTOI framework core
- `sleepwalker/sleepwalker_protocol/` — SWP Python implementation

---

## Escalation

**Primary escalation contact:** Joshua W. Dorsey, Sr.
**Email:** `info@neuroliftsolutions.com`
**Use the escalation template:** `templates/escalation.md`
**Or file a GitHub Issue:** Use the `agent-escalation` issue template

When in doubt, escalate. It is always better to pause than to guess.

---

*This file is part of the ORG-DEV-OTOI-1.0.0 governance framework for NeuroLift Technologies.*
