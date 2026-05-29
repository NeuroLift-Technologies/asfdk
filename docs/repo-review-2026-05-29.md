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
  hyphen-named component trees; the suite effectively no-opped. **Fix prepared
  but not applied** — the push token lacks `workflow` scope; a maintainer must
  apply the one-step change (see "Deferred" #6). Locally, `pytest` already goes
  green via the committed `conftest.py`.
- **Tracked build artifacts** — `*.pyc` and `rrt_advocate.egg-info/` were
  committed despite `.gitignore`. **Untracked.**
- **Nested duplicate dirs** — `SOPs/SOPs/`, `templates/templates/`,
  `ISSUE_TEMPLATE/ISSUE_TEMPLATE/` (stale shorter copies). **Removed.**
- **Loose Python deps** — `jsonschema`, `pydantic`, `torch`, `accelerate`
  unpinned. **Lower bounds added.**

## Changes applied in this PR

| Area | Change |
|---|---|
| `crisis_detector.py` + `keyword_layer.py`, `sentiment_layer.py`, `behavioral_layer.py` (new) | **Ported the canonical 3-layer CDE pipeline** from `NeuroLift-Technologies/rrt-advocate` (keyword + sentiment + behavioral → weighted-aggregate `CrisisIndicators`), replacing the stub. |
| `crisis_assessor.py` | Canonical assessor: aggregate→level mapping, self-harm→BLACK, safety score with penalties, intervention defaults. `CrisisLevel`/`CrisisAssessment` kept defined here for the adapter's imports. |
| `rrt_advocate.py` | Wired to the 3-layer detector; additive `assess_message(text, messages)` entrypoint (replays history into the sliding windows); fixed a latent missing-field bug in the safe-default assessment. |
| `unified_core/integration/rrt_integration.py` | `handle_crisis` evaluates supplied message text via `assess_message` (backward compatible). |
| `rrt-advocate/tests/test_rrt_advocate.py` | Rewritten for the 3-layer contract (benign→GREEN, distress→YELLOW/ORANGE, self-harm→BLACK, empty→GREEN). |
| `conftest.py` (new) | Puts `rrt-advocate/src` on `sys.path` so `pytest` runs from the repo root with no env setup. |
| `Dockerfile` | Corrected entrypoint path. |
| `requirements.txt`, `pyproject.toml` | Pinned lower bounds; added optional `sentiment` extra (`vaderSentiment`). |
| Repo hygiene | Untracked `__pycache__`/`egg-info`; removed stale nested duplicate dirs. |

Result: the RRT test suite goes from a failing run (3 erroring on import) to a
fully green run.

### Note on the detector (aligned with upstream)

An earlier revision of this PR fixed the stub with a *from-scratch single-layer*
detector. That was then **realigned to the canonical 3-layer pipeline** in the
standalone `rrt-advocate` repo (the source of truth), rather than maintaining a
parallel reinvention. The ported layers are **domain-neutral and local-first**:
transparent regex semantic fields (Layer 1), sentiment trend via VADER with a
built-in heuristic fallback (Layer 2 — VADER is an **optional** extra, not a
core dependency), and behavioral timing/complexity/looping (Layer 3). Self-harm
signals always escalate to BLACK. It remains a **transparent baseline, not a
clinical instrument** (it will miss indirect/coded language), and stays
provider-agnostic per the no-LLM-lock-in guardrail (`AGENTS.md` / OTOI §4.4).
ASFDK deliberately omits the standalone's ADHD-specific thresholds/personas;
`crisis_thresholds.yaml` defaults were not changed (guardrail).

## Deferred (needs a human / governance decision)

1. **`.nltotoi/.nltotoi/` reconciliation.** Unlike the other nested dirs, its
   files *diverge* from the parent `.nltotoi/` (different content/sizes), and
   `.nltotoi/` is governance "managed upstream." Picking a canonical copy is a
   governance call, not a mechanical dedupe — left untouched to avoid repeating
   the PR-#5 class of mistake.
2. **Public/internal repo split.** Moving OTOI/SOPs/agent machinery to
   `.github-private`/`solidarity-framework` as the docs themselves propose.
3. **Pre-existing lint debt.** `ruff check .` is already red on `main` (~160+
   findings across existing files). New files in this PR are lint-clean; the
   backlog is a separate sweep.
4. **Intervention *deployment* is still a placeholder.** `InterventionManager`,
   `SupervisorAI` coordination, and `StateManager` persistence remain stubs.
   Detection/assessment is now real; *response* and *persistence* are the next
   substantive gaps.
5. **Cross-runtime Python↔Worker integration** (see finding #2).
6. **CI lint/test never runs at all (needs `workflow` scope).** Two separate
   problems, both requiring a maintainer with `workflow` permission:

   a. **`reusable-ci.yml` has no caller.** It is a `workflow_call`-only
      reusable workflow, and nothing in `.github/workflows/` invokes it — so its
      `lint` and `test` jobs never execute on push or PR. Add a trigger or a
      caller. Simplest: a small caller workflow, e.g. `.github/workflows/ci.yml`:

      ```yaml
      name: CI
      on: [push, pull_request]
      jobs:
        ci:
          uses: ./.github/workflows/reusable-ci.yml
      ```

   b. **The `test` job doesn't install the packages.** Add this step to the
      `test` job in `reusable-ci.yml`, before "Install pytest", so CI imports the
      component packages the way local `pytest` now does:

      ```yaml
            - name: Install ASFDK packages (editable)
              # unified_core ships as a package; sleepwalker is a separate editable
              # install. rrt-advocate is made importable by the repo-root conftest.py.
              if: hashFiles('pyproject.toml') != ''
              run: |
                pip install -e .
                if [ -f sleepwalker/pyproject.toml ]; then pip install -e ./sleepwalker; fi
      ```

   Until (a) is done, the green local `pytest` (50 passed) is the only signal;
   CI does not exercise the Python suite.

## Bottom line

Strong design and documentation; the muscle is now starting to match the bones
on the detection path. The biggest remaining risks are (a) the response/
persistence layers that are still stubbed, and (b) the governance/structure
sprawl that obscures the product for external adopters.
