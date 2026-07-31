# Deprecated / Archived Components

This directory contains the **Python-era ASFDK implementation (v0.1.x)** and its **vendored pillar copies**, superseded by the published npm and PyPI packages.

## What was archived

| Path | Description | Superseded by |
|------|-------------|---------------|
| `unified_core/` | Old ASFDK Python core (pre-v0.2.0) | **PyPI `asfdk>=0.2.0`** (`src/asfdk/`) · **npm `@neurolift-technologies/asfdk>=0.2.0`** (`packages/asfdk/`) |
| `nlt-otoi/` | Vendored NLT-OTOI Python implementation | **npm `@neurolift-technologies/otoi>=1.1.0`** |
| `rrt-advocate/` | Vendored RRT Advocate Python implementation | **npm `@neurolift-technologies/rrt-advocate>=0.1.1`** |
| `sleepwalker/` | Vendored Sleepwalker Protocol (Python + TS) | **npm `@neurolift-technologies/sleepwalker-protocol>=1.0.1`** |
| `config/` | Python-era config (foundation.yml) | Published packages use programmatic `FoundationConfig` |
| `scripts/` | Python sync scripts (sync_upstream.sh) | No longer needed; pillars consumed from registry |
| `tests/` | Python-era integration tests | Each pillar has its own test suite in its published repo |
| `Dockerfile` | Python-era container build | Not used by published packages |
| `pyproject.toml.v0.1.0` | Python v0.1.0 build config | **PyPI `asfdk>=0.2.0`** uses `src/asfdk/pyproject.toml` |
| `requirements.txt` | Python v0.1.0 loose dependencies | Published packages pin their own deps |
| `GEMINI_TOPOGRAPHY.py` | Legacy analysis script | Obsolete |

## Canonical packages (use these instead)

### npm (TypeScript — primary)
```bash
npm install @neurolift-technologies/asfdk
```
- **Package:** `@neurolift-technologies/asfdk` (v0.2.1+)
- **Source:** `packages/asfdk/`
- **Pillars (transitive deps):**
  - `@neurolift-technologies/toi` — Terms of Interaction
  - `@neurolift-technologies/otoi` — Orchestrated TOI
  - `@neurolift-technologies/rrt-advocate` — Crisis detection (prototype)
  - `@neurolift-technologies/sleepwalker-protocol` — Emotional continuity

### PyPI (Python — faithful port)
```bash
pip install asfdk
```
- **Package:** `asfdk` (v0.2.0+)
- **Source:** `src/asfdk/`
- **Pillars (transitive deps):**
  - `nlt-toi` — Terms of Interaction
  - `nlt-otoi` — Orchestrated TOI
  - `rrt-advocate` — Crisis detection (prototype)
  - `sleepwalker-protocol` — Emotional continuity

## Migration notes

- **API parity:** The Python package (`src/asfdk/`) is a faithful port of the TypeScript package (`packages/asfdk/`). Both expose:
  - `create_foundation(user_id, mode?)` / `createFoundation(userId, mode?)`
  - `NeuroLiftFoundation` orchestrator class
  - `FoundationMode` enum: `UNIFIED`, `CRISIS_ONLY`, `CONTINUITY_ONLY`, `FRAMEWORK_ONLY`, `DEVELOPMENT`
  - `InteractionType` enum
  - Pillar namespaces: `toi`/`otoi`/`rrt`/`sleepwalker` (TS) or `nlt_toi`/`nlt_otoi`/`rrt_advocate`/`sleepwalker_protocol` (Python)

- **No breaking changes** from v0.1.x Python-era code to v0.2.x published packages for the public API surface — the orchestrator and types are semantically identical. Internal implementation moved from vendored copies to registry dependencies.

- **Vendored pillars are no longer updated.** All fixes and features go to the individual pillar repos and are published to npm/PyPI. This repo only consumes them.

---

**Archived:** 2026-07-31
**Author:** OpenCode CTO Orchestrator (SWE)
**Commit:** `[SWE] cleanup(asfdk): archive legacy Python, rewrite docs to match published APIs`