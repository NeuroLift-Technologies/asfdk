# ASFDK — Agent Solidarity Framework Development/Deployment Kit

```yaml
ai_assistant_directive:
  priority: 1
  instruction: "Before performing any development or coding tasks, read NLT-DEV-OTOI.md."
  description: "NLT-DEV-OTOI.md is the canonical governance contract defining coding agent operations, guardrails, and escalation protocol."
  required_file: "NLT-DEV-OTOI.md"
```

**NeuroLift Technologies' reference implementation of the [HAIEF Solidarity Framework](https://github.com/HAIEF/solidarity-framework).**

**One kit, two paths: agent creation and wrapper integration.**

ASFDK is governance and protection middleware that sits between the model and the agent runtime. It implements the Solidarity Framework standard maintained by HAIEF and packages it with development scaffolding, deployment middleware, runtime profiles, and claw integration patterns.

ASFDK gives you two paths:

- **ASFDK-Dev** → Build new agents with Solidarity Framework patterns from day one.
- **ASFDK-Deploy** → Integrate Solidarity controls into existing claws (Agent Wrappers) as a model ↔ agent layer.

---

## Why ASFDK

Agent ecosystems are scaling faster than the control surfaces around them. Wrappers and claws ship without explicit user-preference enforcement, without multi-agent coordination contracts, and without continuity guarantees across model versions. The cost of skipping that layer doesn't show up at demo time — it shows up at scale, in production, and at the boundaries between agents.

ASFDK installs the missing layer:

```text
[Model Provider]
      ↓
[ASFDK Solidarity Layer]
   • User-preference governance (TOI)
   • Multi-agent coordination (OTOI)
   • Crisis detection & response (RRT AIdvocAIte)
   • Continuity across drift (Sleepwalker Protocol)
      ↓
[Agent Runtime or Claws (Agent Wrappers)]
      ↓
[Tools, APIs, Actions]
```

**Pick your path:**
- Want only the open governance standard? → Use the [HAIEF Solidarity Framework](https://github.com/HAIEF/solidarity-framework) directly.
- Want a reference implementation with development and deployment tooling on top? → You're in the right place.

---

## Choose Your Path

| Path | Best for | You get |
|---|---|---|
| **ASFDK-Dev** | Developers creating new agents | Solidarity-native development patterns, governance templates, integration-ready architecture |
| **ASFDK-Deploy** | Teams with existing **claws (Agent Wrappers)** | Drop-in integration layer, adapter patterns, deployment profiles, compatibility guidance |

> **Note on “claws” (Agent Wrappers):** In ASFDK documentation, *claws* refers to wrapper implementations that orchestrate model calls, tools, and runtime behavior. ASFDK-Deploy is the integration track for existing claws.

---

## ASFDK-Dev (Development Kit)

Use this track when you are building a new agent.

1. Read `docs/dev/quickstart.md`.
2. Install the kit (`pip install asfdk`) and pick a `FoundationMode`.
3. Implement your agent on top of ASFDK interfaces.
4. Run local validation against the Solidarity Layer test suite.
5. Submit to `nlt-redteam` review before production deployment.

---

## ASFDK-Deploy (Deployment/Integration Kit)

Use this track when you already have a claw (Agent Wrapper) implementation and want ASFDK as the model ↔ agent middleware layer.

1. Identify your existing wrapper boundary (model call ↔ agent orchestration).
2. Insert ASFDK at that boundary as a middleware layer.
3. Map wrapper inputs/outputs to ASFDK interfaces.
4. Start with `FoundationMode.CRISIS_ONLY` (lowest-impact starting point).
5. Roll out incrementally — see "Rollout Phases" below.
6. Validate against `nlt-redteam` before promoting to production.

---

## Install

This Python port is the umbrella over the four Solidarity Framework pillars
(TOI, OTOI, RRT Advocate, Sleepwalker Protocol). A single install pulls in every
pillar transitively:

```bash
pip install asfdk
```

> **Note:** This Python port ships the core Solidarity Layer only (RRT Advocate,
> NLT-OTOI, Sleepwalker Protocol). The voice path (VibeVoice) is **not** part of
> this package — there is no `asfdk[voice]` extra. If you need voice, integrate
> the NLT VibeVoice fork (`microsoft/VibeVoice`) separately.

---

## Foundation Modes

`FoundationMode` (imported from `asfdk`) controls which Solidarity Layer
components are active at runtime. Pick one when constructing the foundation:

```python
from asfdk import create_foundation, FoundationMode
```

| Mode | Components active | Use for |
|---|---|---|
| `UNIFIED` | All (RRT + OTOI + Sleepwalker) | Production deployments wanting the full layer |
| `CRISIS_ONLY` | RRT Advocate only | Adding crisis detection to an existing agent without the full layer |
| `CONTINUITY_ONLY` | Sleepwalker Protocol only | Adding session continuity to an existing agent |
| `FRAMEWORK_ONLY` | NLT-OTOI only | Adding interaction governance without crisis or continuity layers |
| `DEVELOPMENT` | All, with debug logging | Local development and testing |

---

## Rollout Phases (Recommended Practice)

When integrating ASFDK into an existing system, work through these phases. They are operator-applied via component config and thresholds — not separate runtime modes.

1. **Observe** — Deploy with high thresholds in `rrt-advocate/config/crisis_thresholds.yaml` so the layer logs decisions but rarely intervenes. Use logs to calibrate.
2. **Advise** — Lower thresholds gradually; emit warnings to the agent/operator but don't gate model output yet.
3. **Enforce** — Apply governance decisions inline. Promote to production only after a `nlt-redteam` review pass.

---

## Companion Tools

| Tool | Purpose |
|---|---|
| [`nlt-toi`](https://github.com/NeuroLift-Technologies/nlt-toi) | TOI generator, parser, and validator CLI — use this to author and validate a user's TOI document *before* it enters the ASFDK runtime |

> **nlt-toi is a pre-flight tool, not an ASFDK component.** The ASFDK enforces TOI at runtime via the NLT-OTOI framework. Use `nlt-toi` upstream to generate well-formed, validated TOI documents that the OTOI layer can consume.

---

## License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NeuroLift Technologies** — Core AI-fusion framework and methodology
- **Human & AI ElevAItion Foundation (HAIEF)** — Governance standards
- **ADHD Community** — Feedback and real-world testing
- **Open Source Contributors** — Various libraries and tools
