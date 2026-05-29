# Claude Agent Log — Governance Framing Restoration

**Date:** 2026-05-28
**Agent:** Claude Code (Opus 4.7)
**Repository:** NeuroLift-Technologies/asfdk
**Branch:** `claude/governance-docs-restore-yB5sI`
**Supersedes:** PR #5 (`governance/otoi-compliance`)

## Summary

Copilot PR #5 ran a global find/replace `.github-private` → `asfdk` across every governance doc as part of an "ORG-DEV-OTOI-1.0.0 compliance baseline." Some changes correctly localized repo-scoped artifacts, but most destroyed legitimate org-level framing references (the canonical org contract, the org-wide agent gateway, the 3-tier architecture description, canonical SOP URLs, the public security URL, and the historical audit trail). This PR starts from current `main` and applies only the correct portions.

## Kept (correct repo-local scoping)

| File | Change |
|---|---|
| `README.md` | Added `ai_assistant_directive` YAML directive + `Companion Tools` section pointing at `nlt-toi` (pre-flight tool, not an ASFDK component) |
| `nlt-otoi/README.md` | Added `nlt-toi` to Related Projects |
| `docs/unified_architecture.md` | Added `nlt-toi` pre-flight blockquote in TOI-OTOI section |
| `.nltotoi/.nltotoi/README.md` | Scoped namespace to `NeuroLift-Technologies/asfdk` |
| `.nltotoi/.nltotoi/index/governance-files.md` | Scoped index header + Scope line to this repo |
| `.nltotoi/.nltotoi/proposals/validation-roadmap.md` | Scope line to this repo |
| `.nltotoi/.nltotoi/scripts/validate-governance.sh` | `check_content` for `nltotoi.json` repo name now matches local manifest (`NeuroLift-Technologies/asfdk`) |
| `nltotoi.json` | `last_updated` bumped to `2026-05-28`. `repository.name` already correct. `purpose`, `visibility`, and `ethical_framework.public_governance` URL preserved from main (Copilot's rewrites were rejected). |
| `docs/agent-log/2026-05-21-codex-repo-specific-governance.md` | New audit log preserved from PR #5 |

## Preserved (left untouched from `main`)

- `NLT-DEV-OTOI.md` — keeps org-wide framing (Copilot rewrote it as repo-specific and pointed `Repository:` at the wrong repo — rejected)
- `AGENTS.md` — keeps org-wide gateway and public-governance pointer to `.github`
- `CLAUDE.md` — keeps the 157-line dual-audience version (external adopters + NLT-internal); Copilot would have replaced it with a generic OTOI compliance stub
- `file-structure.md` — keeps canonical 3-tier architecture references
- `SOPs/SOPs/repo-governance-setup.md` — kept; canonical-source URLs unchanged
- `ISSUE_TEMPLATE/config.yml` — security URL stays on `.github`
- `.github/workflows/sync-governance-public.yml` — sync target stays on `.github` public repo
- `docs/active-threads.md` — historical thread descriptions left intact
- `templates/agent-registration.json`, `templates/handoff-record.json` — example values still reference `.github`
- All `docs/agent-log/handoffs/*.json` and `docs/agent-log/registrations/*.json` — historical records, not rewritten

## Added

- `SOPs/repo-governance-setup.md` upgraded `v1.0.0` → `v1.1.0` from `.github-private` (adds `.claude/` provisioning and governance-auto-propagate sections)
- This audit log

## Validation

`bash .nltotoi/.nltotoi/scripts/validate-governance.sh` — see PR description for results.
