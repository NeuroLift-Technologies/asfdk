# ASFDK — Agent Solidarity Framework Development Kit

```yaml
ai_assistant_directive:
  priority: 1
  instruction: "Before performing any development or coding tasks, read NLT-DEV-OTOI.md."
  description: "NLT-DEV-OTOI.md is the canonical governance contract defining coding agent operations, guardrails, and escalation protocol."
  required_file: "NLT-DEV-OTOI.md"
```

**NeuroLift Technologies' reference implementation of the [HAIEF Solidarity Framework](https://github.com/NeuroLift-Technologies/solidarity-framework).**

**One kit, two runtimes: TypeScript (npm) and Python (PyPI).**

ASFDK is governance and protection middleware that sits between the model and the agent runtime. It implements the Solidarity Framework standard maintained by HAIEF and packages it with a high-level orchestrator (`NeuroLiftFoundation`) and re-exports of all four pillar packages.

ASFDK gives you a single install that surfaces every layer of the model ↔ agent boundary:

```text
[Model Provider]
      ↓
[ASFDK Solidarity Layer]
   • User-preference governance (TOI)
   • Multi-agent coordination (OTOI)
   • Crisis detection & response (RRT Advocate)
   • Continuity across drift (Sleepwalker Protocol)
      ↓
[Agent Runtime or Claws (Agent Wrappers)]
      ↓
[Tools, APIs, Actions]
```

**Pick your runtime:**
- **TypeScript/Node.js** → `npm install @neurolift-technologies/asfdk` (primary, published from `packages/asfdk/`)
- **Python** → `pip install asfdk` (faithful port, published from `src/asfdk/`)

> **Note on “claws” (Agent Wrappers):** In ASFDK documentation, *claws* refers to wrapper implementations that orchestrate model calls, tools, and runtime behavior.

---

## Install

### TypeScript (npm) — Primary

```bash
npm install @neurolift-technologies/asfdk
```

The four pillar packages are declared as dependencies, so they are installed transitively:

| Pillar | Package | Role |
|---|---|---|
| **TOI** | [`@neurolift-technologies/toi`](https://www.npmjs.com/package/@neurolift-technologies/toi) | Terms of Interaction — user-preference governance |
| **OTOI** | [`@neurolift-technologies/otoi`](https://www.npmjs.com/package/@neurolift-technologies/otoi) | Orchestrated TOI — multi-agent honoring layer |
| **RRT Advocate** | [`@neurolift-technologies/rrt-advocate`](https://www.npmjs.com/package/@neurolift-technologies/rrt-advocate) | Crisis detection ⚠️ *prototype* |
| **Sleepwalker Protocol** | [`@neurolift-technologies/sleepwalker-protocol`](https://www.npmjs.com/package/@neurolift-technologies/sleepwalker-protocol) | Emotional continuity across drift |

### Python (PyPI) — Faithful Port

```bash
pip install asfdk
```

The Python package mirrors the TypeScript API and depends on the Python equivalents of the pillars:

| Pillar | Package | Role |
|---|---|---|
| **TOI** | `nlt-toi` | Terms of Interaction — user-preference governance |
| **OTOI** | `nlt-otoi` | Orchestrated TOI — multi-agent honoring layer |
| **RRT Advocate** | `rrt-advocate` | Crisis detection ⚠️ *prototype* |
| **Sleepwalker Protocol** | `sleepwalker-protocol` | Emotional continuity across drift |

---

## Quick Start (Both Runtimes)

### TypeScript

```ts
import { createFoundation, FoundationMode, InteractionType, toi } from '@neurolift-technologies/asfdk';

async function main() {
  // Orchestrator: route interactions through the active components for a mode.
  const foundation = await createFoundation('user-123', FoundationMode.UNIFIED);

  const response = await foundation.processInteraction({
    timestamp: new Date(),
    interactionType: InteractionType.PREFERENCE_UPDATE,
    data: { toi: { $toi: '1.0.0', $tier: 'personal', identity: { author: 'user-123' } } },
    userId: 'user-123',
  });

  // Pillars are also available directly as namespaces.
  const parsed = toi.safeParseToi(myPreferences);
}

main();
```

### Python

```python
import asyncio
from asfdk import create_foundation, FoundationMode, InteractionType, toi

async def main():
    foundation = await create_foundation("user-123", FoundationMode.UNIFIED)

    response = await foundation.process_interaction({
        "timestamp": datetime.now(timezone.utc),
        "interaction_type": InteractionType.PREFERENCE_UPDATE,
        "data": {"toi": {"$toi": "1.0.0", "$tier": "personal", "identity": {"author": "user-123"}}},
        "user_id": "user-123",
    })

    # Pillars are also available directly as namespaces.
    result = toi.safe_parse_toi(my_preferences)

asyncio.run(main())
```

---

## Foundation Modes

`FoundationMode` controls which Solidarity Framework components are active at runtime.

| Mode | TOI/OTOI | Sleepwalker | RRT Advocate | Use for |
|---|---|---|---|---|
| `UNIFIED` | ✅ | ✅ | ✅ | Production deployments wanting the full layer |
| `CRISIS_ONLY` | — | — | ✅ | Adding crisis detection to an existing agent without the full layer |
| `CONTINUITY_ONLY` | — | ✅ | — | Adding session continuity to an existing agent |
| `FRAMEWORK_ONLY` | ✅ | — | — | Adding interaction governance without crisis or continuity layers |
| `DEVELOPMENT` | ✅ | ✅ | — | Local development and testing |

Per-component overrides are available via `FoundationConfig.components`.

---

## Rollout Phases (Recommended Practice)

When integrating ASFDK into an existing system, work through these phases. They are operator-applied via component config and thresholds — not separate runtime modes.

1. **Observe** — Deploy with high thresholds so the layer logs decisions but rarely intervenes. Use logs to calibrate.
2. **Advise** — Lower thresholds gradually; emit warnings to the agent/operator but don't gate model output yet.
3. **Enforce** — Apply governance decisions inline. Promote to production only after an `nlt-redteam` review pass.

---

## ⚠️ Crisis detection is a prototype — not a safety system

The RRT Advocate layer wraps an **experimental** crisis-*detection* library with stubbed intervention layers. It is **not medical advice, not a crisis service**, performs no real-time monitoring, and **can miss real crisis signals**. Never rely on it as the sole safety mechanism. If you or someone else needs help now, in the US call or text **988** or chat [988lifeline.org](https://988lifeline.org).

---

## Companion Tools

| Tool | Purpose |
|---|---|
| [`nlt-toi`](https://github.com/NeuroLift-Technologies/nlt-toi) | TOI generator, parser, and validator CLI — use this to author and validate a user's TOI document *before* it enters the ASFDK runtime |

> **nlt-toi is a pre-flight tool, not an ASFDK component.** The ASFDK enforces TOI at runtime via the NLT-OTOI framework. Use `nlt-toi` upstream to generate well-formed, validated TOI documents that the OTOI layer can consume.

---

## Repository Structure

```
asfdk/
├── packages/asfdk/          # npm @neurolift-technologies/asfdk (TypeScript source)
├── src/asfdk/               # PyPI asfdk (Python source, faithful port)
├── hosting/                 # Next.js landing page (separate deliverable)
├── workers/                 # Cloudflare Workers deployment (separate deliverable)
├── legacy/                  # Archived Python-era implementation (v0.1.x)
│   ├── unified_core/        # Old ASFDK Python core
│   ├── nlt-otoi/            # Vendored NLT-OTOI (superseded by npm @neurolift-technologies/otoi)
│   ├── rrt-advocate/        # Vendored RRT Advocate (superseded by npm @neurolift-technologies/rrt-advocate)
│   ├── sleepwalker/         # Vendored Sleepwalker (superseded by npm @neurolift-technologies/sleepwalker-protocol)
│   ├── config/              # Python-era config
│   ├── scripts/             # Python sync scripts
│   ├── tests/               # Python-era tests
│   ├── DEPRECATED.md        # Archive index and migration guide
│   └── ...                  # Dockerfile, pyproject.toml.v0.1.0, requirements.txt, GEMINI_TOPOGRAPHY.py
├── docs/                    # Documentation (dev/deploy quickstarts, etc.)
├── .nltotoi/                # NLT governance namespace
├── NLT-DEV-OTOI.md          # Org-level coding agent contract
├── AGENTS.md                # Repo-specific agent guidance
├── CLAUDE.md                # Project-specific context
└── LICENSE                  # Apache-2.0
```

---

## License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NeuroLift Technologies** — Core AI-fusion framework and methodology
- **Human & AI ElevAItion Foundation (HAIEF)** — Governance standards
- **ADHD Community** — Feedback and real-world testing
- **Open Source Contributors** — Various libraries and tools