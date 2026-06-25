# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This file has two audiences — read the one that matches your role.

---

## 🌐 If You Are an External Adopter Integrating ASFDK

You're a developer at another organization wanting to add Solidarity Framework controls (RRT Advocate, NLT-OTOI, Sleepwalker) to your AI agent or product. The NLT-internal governance machinery you may see in this repo (`AGENTS.md`, `NLT-DEV-OTOI.md`, `SOPs/`, `.nltotoi/`, `templates/agent-*.json`, `ISSUE_TEMPLATE/agent-escalation.md`, `.github/workflows/agent-*.yml`) is **for the NLT team that maintains this kit, not for you**. Ignore it.

### What ASFDK Is

ASFDK is governance and protection middleware sitting between the model and the agent runtime. It implements the [HAIEF Solidarity Framework](https://github.com/NeuroLift-Technologies/haief) — an open standard for human-safe, emotionally-continuous AI behavior — and is the umbrella over three Solidarity Framework pillars:

- **RRT Advocate** (`rrt_advocate`) — crisis detection and response
- **NLT-OTOI** (`nlt_otoi`) — Terms of Interaction / multi-agent governance
- **Sleepwalker Protocol** (`sleepwalker_protocol`) — emotional continuity across sessions

The Python port publishes a single importable package, `asfdk` (`src/asfdk/`),
which depends on the three published pillar packages and re-exports them as
namespaces. (Voice/VibeVoice is **not** part of this Python port — there is no
`asfdk[voice]` extra.)

### Integration Surface

| Path | Role |
|---|---|
| `asfdk.create_foundation` | The main entrypoint. `await create_foundation(user_id, mode)` returns a `NeuroLiftFoundation` instance. |
| `src/asfdk/integration/` | Adapter modules wrapping each pillar for the foundation |
| `FoundationMode` enum | `UNIFIED` / `CRISIS_ONLY` / `CONTINUITY_ONLY` / `FRAMEWORK_ONLY` / `DEVELOPMENT` — picks which components run |
| `rrt-advocate/config/crisis_thresholds.yaml` | Per-domain thresholds (health, education, workplace…) for crisis detection |
| `docs/dev/quickstart.md` | If you're building a new agent and want ASFDK from day one |
| `docs/deploy/quickstart.md` | If you're integrating ASFDK into an existing agent runtime |

### Install

```bash
pip install asfdk   # umbrella; pulls in the three pillars transitively
```

Then:

```python
from asfdk import create_foundation, FoundationMode

foundation = await create_foundation(
    user_id="your_user_id",
    mode=FoundationMode.CRISIS_ONLY,  # start small
)
```

To override which components run for a mode, pass a `components` dict (or a
`FoundationComponents` instance):

```python
from asfdk import FoundationConfig

config = FoundationConfig(
    user_id="your_user_id",
    mode=FoundationMode.UNIFIED,
    components={"rrt_advocate": True, "toi_otoi_framework": True,
                "sleepwalker_protocol": True},
)
```

### Rollout Recommendation

The README describes a 3-phase rollout for integrating into an existing system: observe → advise → enforce. These are operator practices (set thresholds high, then lower; route advisory outputs to logs, then to the agent, then inline) — not separate runtime modes. Start with `FoundationMode.CRISIS_ONLY` plus high thresholds in `crisis_thresholds.yaml` and tighten progressively.

### Known Gaps (as of 2026-05)

- Only the `asfdk` package (`src/asfdk/`) ships in the wheel. It declares the three pillars (`nlt-toi`, `nlt-otoi`, `rrt-advocate`, `sleepwalker-protocol`) as published dependencies and re-exports them as namespaces (`toi`, `otoi`, `rrt`, `sleepwalker`); it does **not** vendor or bundle their source. The hyphenated trees in the repo root (`rrt-advocate/`, `nlt-otoi/`, `sleepwalker/`) are checked-in copies of the pillar repos and are excluded from the distribution.
- Web app under `hosting/` (Next.js) is a demo; not required for integration.

### Scope of Changes if You Submit a PR

External contributions are welcome. Things you may freely modify:
- Integration adapters in `src/asfdk/integration/`
- Tests in `tests/`
- Documentation in `docs/`
- Bug fixes anywhere

Things requiring discussion before changing (open an issue first):
- The `FoundationMode` enum or `create_foundation` signature (public API)
- Component interfaces in `rrt-advocate/`, `nlt-otoi/`, `sleepwalker/` (these have upstream sources)
- `crisis_thresholds.yaml` defaults (affects all adopters)
- Anything under `.nltotoi/`, `SOPs/`, `templates/agent-*.json` — these are NLT-internal and managed upstream

### Commit Format

For external contributions, use Conventional Commits (`feat:`, `fix:`, `docs:`, etc). The `[AGENT_NAME]` prefix you may see in the git history is an NLT-internal convention and doesn't apply to external PRs.

---

## 🔒 If You Are an NLT-Internal Agent Working on ASFDK

You're a coding agent operating under `ORG-DEV-OTOI-1.0.2` working on ASFDK as part of NLT's internal development. Full governance machinery applies.

### NLT Session Start (SOP-NLT-001)

1. Read `NLT-DEV-OTOI.md` — the canonical org-level coding agent contract
2. Read `AGENTS.md` — internal coordination gateway (commit format, guardrails, escalation triggers)
3. Read `docs/active-threads.md` — current work in progress
4. Self-register per OTOI Section 3 into `docs/agent-log/registrations/`

### Repository Identity (NLT-Internal)

| Field | Value |
|---|---|
| **Repository** | `NeuroLift-Technologies/asfdk` |
| **Visibility** | Currently `internal`; planned `public` |
| **Audience** | External AI developers adopting the Solidarity Framework |
| **Upstream standard** | [`NeuroLift-Technologies/haief`](https://github.com/NeuroLift-Technologies/haief) |
| **Canonical impl (internal)** | `NeuroLift-Technologies/solidarity-framework` |
| **OTOI Version** | ORG-DEV-OTOI-1.0.2 |
| **Governing SOP** | SOP-NLT-001 (`SOPs/new-agent-onboarding.md`) |

### Public-Surface vs Internal-Machinery — Critical for This Repo

Because asfdk is going public, every change you make should ask: **does this belong in the public adopter view, or is it NLT-internal noise?**

Public adopter view: `README.md`, `LICENSE`, `pyproject.toml`, `requirements.txt`, `src/asfdk/`, `packages/asfdk/` (TS source of truth), `hosting/`, `tests/`, `docs/dev/`, `docs/deploy/`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE/bug_report.md`, `ISSUE_TEMPLATE/feature_request.md`.

NLT-internal machinery (planned for removal from public asfdk; canonical home is `.github-private` or `solidarity-framework`): `AGENTS.md`, `NLT-DEV-OTOI.md`, `SOPs/`, `.nltotoi/`, `nltotoi.json`, `templates/agent-*.json`, `templates/handoff-record.json`, `templates/intent-log.md`, `templates/escalation.md`, `agents/`, `ISSUE_TEMPLATE/agent-escalation.md`, `ISSUE_TEMPLATE/governance-proposal.md`, `PULL_REQUEST_TEMPLATE/agent-contribution.md`, `.github/workflows/agent-commit-format.yml`, `agent-session-check.yml`, `agent-profile-validation.yml`, `skill-profile-validation.yml`, `sync-governance-public.yml`, `nltotoi-check.yml`, `.github/copilot-instructions.md`, `mcp-config.yaml`, `links.md`, `file-structure.md`.

### Commit Format (NLT-Internal)

```
[AGENT_NAME] type(scope): description
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`. Enforced by `.github/workflows/agent-commit-format.yml` (skipped for fork PRs).

### NLT Guardrails

(Org-wide guardrails in `AGENTS.md` and OTOI Section 4.4. These layer on top for asfdk:)

| Rule | Why |
|---|---|
| Do not promote asfdk visibility to `public` without Joshua's approval | This is a launch decision |
| Do not modify `NLT-DEV-OTOI.md` here | Canonical home is `.github-private` |
| Changes to crisis intervention logic (`rrt-advocate/src/rrt_advocate.py`) or thresholds (`crisis_thresholds.yaml`) require escalation | Affects all adopters' safety behavior |
| The `asfdk` package is the public API — changes to `FoundationMode`, `create_foundation`, `NeuroLiftFoundation` are breaking changes for adopters | Treat as a versioned API |
| The HAIEF Solidarity Framework standard is upstream; do not encode NLT-only opinions as "the standard" in code or docs | Maintain the standard/impl boundary |

### Escalation

**Primary contact:** Joshua W. Dorsey, Sr. (`info@neuroliftsolutions.com`)
**Template:** `templates/escalation.md`
**Policy:** Escalate, do not guess.

---

*This file is part of the ORG-DEV-OTOI-1.0.2 governance framework for NeuroLift Technologies.*
