# ASFDK Repository Review — 2026-05-29

> Scope: a candid assessment of the state of `NeuroLift-Technologies/asfdk`, plus
> the concrete fixes applied alongside this review and the work intentionally
> left for a human decision. Written to be read top-to-bottom by a maintainer.

## TL;DR

ASFDK is an impressively **designed and documented** framework wrapped around a
codebase whose safety-critical core was, until this change, **largely stubbed**.
The orchestration layer is real; the crisis-detection logic it orchestrated
returned a hardcoded "all clear." The governance/documentation layer is
thorough but disproportionate to the code and bears scars of multiple AI agents
editing in tension. The build/test/deploy plumbing had several breakages.

This review ships fixes for the highest-leverage, lowest-risk problems and
flags the rest.

## What was assessed

- **Code & architecture** — `unified_core/`, `rrt-advocate/`, `sleepwalker/`,
  `nlt-otoi/`, `workers/`, `tests/`.
- **Governance & docs** — `README.md`, `AGENTS.md`, `CLAUDE.md`,
  `NLT-DEV-OTOI.md`, `SOPs/`, `.nltotoi/`, `docs/`, templates.
- **Repo hygiene & CI** — `.github/workflows/`, `Dockerfile`, `pyproject.toml`,
  `requirements.txt`, `hosting/`, tracked artifacts.

## Findings

### 1. The crisis-detection core was stubbed (highest severity)

For a system whose stated purpose is crisis support, the detection pipeline did
nothing:

- `crisis_detector.detect_crisis_indicators()` returned an empty list
  (`# Placeholder implementation … return signals`).
- `crisis_assessor.assess_crisis()` always returned `CrisisLevel.GREEN`,
  `confidence=0.0`. It could never escalate.
- `crisis_detector._load_thresholds()` ignored the YAML config and returned a
  hardcoded dict.
- The unit tests *mocked* these components, so "passing" tests proved nothing
  about real behavior — and even then 3 of them errored on import.

A hollow safety layer is arguably worse than none, because it implies a
guarantee it does not deliver.

**Status: addressed in this PR** (see "Changes applied").

### 2. Detection and the Cloudflare Worker were two disconnected halves

The only working crisis detection lived in `workers/src/rrt-advocate.ts` (an
LLM call via Cloudflare AI), completely decoupled from the Python core that the
README and `unified_core` present as the product. There is no shared contract
between them beyond the `GREEN..BLACK` level names.

**Status: partially addressed.** The Python pipeline now produces real
assessments on the same `GREEN..BLACK` contract, and a new `assess_message()`
entrypoint mirrors the Worker's interface. True cross-runtime integration
(Python core calling the Worker, or sharing one detector) remains an
**architecture decision** and is deferred — see "Deferred."

### 3. Governance/docs are disproportionate and show agent-vs-agent churn

- Roughly **15.6k lines of docs/governance vs ~2.3k lines of meaningful code.**
- Org-wide governance machinery (OTOI contract, SOPs, agent templates) is
  shipped inside a product repo; the repo's own `file-structure.md` already
  says most of it is "planned for removal."
- `docs/agent-log/2026-05-28-claude-governance-restoration.md` records a
  destructive Copilot global find/replace (PR #5) that a later Claude PR had to
  "supersede" — a multi-agent conflict left partially cleaned up.

**Status: partially addressed** (stale nested duplicates removed; the larger
public/internal split is deferred).

### 4. Build / CI / hygiene breakages

- **`Dockerfile`** ran `unified-core/…` (hyphen) — wrong path; container failed
  on startup. **Fixed.**
- **CI test job** never installed the packages, so `pytest` could not import the
  hyphen-named component trees; the suite effectively no-opped. **Fixed.**
- **Tracked build artifacts** — `*.pyc` and `rrt_advocate.egg-info/` were
  committed despite `.gitignore`. **Untracked.**
- **Nested duplicate dirs** — `SOPs/SOPs/`, `templates/templates/`,
  `ISSUE_TEMPLATE/ISSUE_TEMPLATE/` (stale shorter copies). **Removed.**
- **Loose Python deps** — `jsonschema`, `pydantic`, `torch`, `accelerate`
  unpinned. **Lower bounds added.**

## Changes applied in this PR

| Area | Change |
|---|---|
| `crisis_detector.py` | Real YAML threshold loading; deterministic, provider-agnostic lexical detector emitting `CrisisSignal`s; safe on empty input. |
| `crisis_assessor.py` | Real severity assessment (`GREEN..BLACK`) with safety-first suicidal escalation, recommended interventions, confidence and safety scores. |
| `rrt_advocate.py` | New additive `assess_message()` text entrypoint; fixed a latent missing-field bug in the safe-default assessment. |
| `unified_core/integration/rrt_integration.py` | `handle_crisis` now evaluates supplied message text via `assess_message` (backward compatible). |
| `rrt-advocate/tests/test_rrt_advocate.py` | Rewritten to test the real pipeline (benign→GREEN, stress→YELLOW/ORANGE, suicidal→RED/BLACK, empty→no signals). |
| `conftest.py` (new) | Puts `rrt-advocate/src` on `sys.path` so `pytest` runs from the repo root with no env setup. |
| `.github/workflows/reusable-ci.yml` | Installs `-e .` and `-e sleepwalker/` so the test job actually imports and runs. |
| `Dockerfile` | Corrected entrypoint path. |
| `requirements.txt`, `pyproject.toml` | Pinned lower bounds. |
| Repo hygiene | Untracked `__pycache__`/`egg-info`; removed stale nested duplicate dirs. |

Result: `pytest` goes from **3 failed / 41 passed** to **50 passed**.

### Safety note on the new detector

The new detector is a **deterministic lexical baseline**: transparent,
auditable, and provider-agnostic (it deliberately does **not** select an LLM,
per the no-LLM-lock-in guardrail in `AGENTS.md` / OTOI §4.4). It is **not** a
clinical instrument and will miss indirect or coded language. It is designed to
be replaced: any detector returning `CrisisSignal` objects (e.g. a model-backed
one like the Worker) drops in by subclassing `CrisisDetector`. Crisis-threshold
**defaults** in `crisis_thresholds.yaml` were not changed (guardrail).

## Deferred (needs a human / governance decision)

1. **`.nltotoi/.nltotoi/` reconciliation.** Unlike the other nested dirs, its
   files *diverge* from the parent `.nltotoi/` (different content/sizes), and
   `.nltotoi/` is governance "managed upstream." Picking a canonical copy is a
   governance call, not a mechanical dedupe — left untouched to avoid repeating
   the PR-#5 class of mistake.
2. **Public/internal repo split.** Moving OTOI/SOPs/agent machinery to
   `.github-private`/`solidarity-framework` as the docs themselves propose.
3. **`hosting/` Next.js version.** `"next": "latest"` resolves to Next 16 in the
   lockfile while React is pinned to 18 — a latent mismatch. Pinning + lockfile
   regen is its own change (demo app; not on the integration path).
4. **Pre-existing lint debt.** `ruff check .` is already red on `main` (~160+
   findings across existing files). New files in this PR are lint-clean; the
   backlog is a separate sweep.
5. **Intervention *deployment* is still a placeholder.** `InterventionManager`,
   `SupervisorAI` coordination, and `StateManager` persistence remain stubs.
   Detection/assessment is now real; *response* and *persistence* are the next
   substantive gaps.
6. **Cross-runtime Python↔Worker integration** (see finding #2).

## Bottom line

Strong design and documentation; the muscle is now starting to match the bones
on the detection path. The biggest remaining risks are (a) the response/
persistence layers that are still stubbed, and (b) the governance/structure
sprawl that obscures the product for external adopters.
