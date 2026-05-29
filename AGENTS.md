# AGENTS.md — NeuroLift Technologies Organization-Wide Internal Gateway

> **Internal use only.** This is the private governance gateway for all coding agents operating within NeuroLift Technologies repositories. For public-facing principles, see the public [`NeuroLift-Technologies/.github`](https://github.com/NeuroLift-Technologies/.github) repository.

---

## You Are Here

You are a coding agent operating within the **NeuroLift Technologies** organization. This document is your internal coordination gateway.

**Mandatory reading order:**
1. `NLT-DEV-OTOI.md` — Full org-level coding agent contract (this repo, root level)
2. Repo-level `CLAUDE.md` — Project-specific context (in the repo you are working in)
3. `docs/active-threads.md` — Current work state (in the repo you are working in)

**Final authority:** Joshua W. Dorsey, Sr. Escalate. Do not guess.

---

## Solidarity Framework Principles (Public)

The ethical foundation of all NLT work is publicly documented in the **Solidarity Framework** and **HAIEF** (Human-AI Ethical Integration Framework):

- Public governance principles: [`NeuroLift-Technologies/.github`](https://github.com/NeuroLift-Technologies/.github)
- HAIEF reference: https://elevaitionfoundation.org

The principles are public. The operational machinery is in `NeuroLift-Technologies/asfdk`.

---

## Coordination Protocol

### Session Start (Every Session)

```
1. Read NLT-DEV-OTOI.md (this repo)
2. Read repo-level CLAUDE.md (working repo)
3. Read docs/active-threads.md (working repo)
4. Self-register per OTOI Section 3
5. Confirm task scope before beginning
```

### Commit Format

All agent commits must follow:

```
[AGENT_NAME] type(scope): description
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`

### Escalation Triggers

Escalate to Joshua immediately when:
- Task scope is unclear or conflicts with existing work
- An architectural or deployment decision is required
- A blocker cannot be resolved by the agent
- An ethical concern arises
- LLM provider or external service selection is needed

Use the escalation template: `templates/escalation.md`

---

## Guardrails

These are **non-negotiable**. No exceptions without explicit Joshua approval:

| Guardrail | Details |
|---|---|
| No LLM provider lock-in | Do not hardcode or commit to a specific LLM provider |
| No architecture decisions | Database, deployment, framework choices require human sign-off |
| No production deployments | Human must explicitly approve all production actions |
| No credential storage | Never store secrets, tokens, or credentials in code or VCS |
| No external integrations | Third-party service connections require Joshua's approval |
| No OTOI self-amendment | This governance doc cannot be changed by agents |

---

## Internal File Map

All files below live in this repository (`NeuroLift-Technologies/asfdk`):

```
NLT-DEV-OTOI.md                        ← Canonical org-level agent contract
AGENTS.md                               ← This file
nltotoi.json                            ← Discovery manifest

.nltotoi/
├── README.md                           ← Namespace overview
├── index/governance-files.md          ← File registry
├── contracts/README.md                ← Contract namespace
├── proposals/validation-roadmap.md    ← Validation roadmap
└── scripts/validate-governance.sh     ← Governance validation

templates/
├── agent-registration.json            ← OTOI Section 3 registration format
├── handoff-record.json                ← OTOI Section 5 handoff format
├── escalation.md                      ← OTOI Section 4.3 escalation format
└── intent-log.md                      ← Intent logging template

ISSUE_TEMPLATE/
├── agent-escalation.md                ← GitHub escalation issue form
└── governance-proposal.md             ← OTOI amendment proposal form

PULL_REQUEST_TEMPLATE/
└── agent-contribution.md              ← Agent PR checklist

workflows/
└── validate-governance.yml            ← CI: runs validate-governance.sh

SOPs/
├── new-agent-onboarding.md            ← How to onboard a new coding agent
├── repo-governance-setup.md           ← How to add governance to a new NLT repo
└── incident-response.md               ← What to do when an agent goes off-rails
```

---

## Multi-Agent Coordination

When multiple agents may be active:

1. **Check active-threads.md first** — do not begin work already in progress
2. **Claim your thread** — update active-threads.md when starting a task
3. **Write handoff records** — never leave a session without a handoff document
4. **Do not overwrite peer work** — if conflict is detected, escalate

---

## Handoff Protocol

Before ending any significant session:

1. Update `docs/active-threads.md` in the working repo
2. Write a handoff record to `docs/agent-log/handoffs/` using `templates/handoff-record.json`
3. Document any open escalations in `docs/escalations/`
4. Summarize decisions made and decisions pending

---

## Cursor Cloud specific instructions

> **Note:** This section contains development environment operational notes for Cursor Cloud agents. It does not modify any governance rules, guardrails, or coordination protocols defined above.

### Services overview

| Service | Path | How to run | Notes |
|---|---|---|---|
| **ASFDK Python core** | `.` (repo root) | `from unified_core import create_foundation, FoundationMode` | Main product. No external services needed. |
| **Hosting (Next.js demo)** | `hosting/` | `cd hosting && npm run dev` | Static landing page at `http://localhost:3000` |
| **Workers (Cloudflare)** | `workers/` | `cd workers && npx wrangler dev` | Requires Cloudflare bindings (KV, D1, AI); optional |
| **Sleepwalker TS** | `sleepwalker/` | `cd sleepwalker && npm run build` | Dual Python/TS impl; TS side has no dev server |

### Running tests

- **Python (all components):** `python3 -m pytest --tb=short` from repo root. Requires `PYTHONPATH` to include `rrt-advocate/src` for RRT tests to load modules. Sleepwalker must be installed (`pip install -e sleepwalker/`).
- **Integration tests:** `python3 tests/integration_test.py` (custom async runner, not discovered by pytest).
- **Sleepwalker TS:** `cd sleepwalker && npm test` (Jest; test files not yet written as of 2026-05).

### Linting

- **Python:** `ruff check .` from repo root (CI uses `ruff`; 164 pre-existing warnings exist).
- **Hosting:** `cd hosting && npx next lint` (if eslint config present).

### Governance validation

- Run `bash .nltotoi/scripts/validate-governance.sh` to verify all governance files are present and valid (25 checks).
- The mandatory reading order before any work session is: `NLT-DEV-OTOI.md` then `CLAUDE.md` then `docs/active-threads.md`. See the "Session Start" section above.
- Commit format is enforced: `[AGENT_NAME] type(scope): description`. See the "Commit Format" section above.

### Known gotchas

- `rrt-advocate/tests/test_rrt_advocate.py` has 3 pre-existing failures due to test stubs not registering `CrisisAssessment` for the import `from crisis.assessors.crisis_assessor import CrisisAssessment, CrisisLevel`. This is a known bug in the test fixture, not an environment issue.
- The component source trees (`rrt-advocate/`, `nlt-otoi/`, `sleepwalker/`) use hyphenated directory names that are not valid Python package identifiers. They are wrapped by adapters under `unified_core/integration/`. To import them directly, add their `src/` paths to `PYTHONPATH`.
- `pip install -e .` only installs `unified_core`. You must also run `pip install -e sleepwalker/` to get `sleepwalker_protocol` importable for tests.
- VibeVoice (voice component) is opt-in and requires `pip install -e ".[voice]"` which pulls large deps (torch, transformers). Skip unless specifically needed.
- `~/.local/bin` must be on `PATH` for user-installed tools (`pytest`, `ruff`) to be found.

---

*Internal governance document — NeuroLift Technologies | ORG-DEV-OTOI-1.0.0*
