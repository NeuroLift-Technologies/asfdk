# ASFDK — Agent Solidarity Framework Development/Deployment Kit

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
2. Select a base profile (`core_only` or `voice_enabled`).
3. Implement your agent on top of ASFDK interfaces.
4. Run local validation against the Solidarity Layer test suite.
5. Submit to `nlt-redteam` review before production deployment.

---

## ASFDK-Deploy (Deployment/Integration Kit)

Use this track when you already have a claw (Agent Wrapper) implementation and want ASFDK as the model ↔ agent middleware layer.

1. Identify your existing wrapper boundary (model call ↔ agent orchestration).
2. Insert ASFDK at that boundary as a middleware layer.
3. Map wrapper inputs/outputs to ASFDK interfaces.
4. Start with the `core_only` profile.
5. Run in passive mode, then advisory mode, then active mode.
6. Validate against `nlt-redteam` before promoting to production.

---

## Deployment Profiles

**`core_only`** *(recommended default)*

- No voice dependencies
- Full Solidarity Layer functionality
- Simplest setup and broadest compatibility

**`voice_enabled`** *(optional)*

- Adds voice interface path on top of the core layer
- For teams shipping speech I/O (built on the NLT VibeVoice fork of `microsoft/VibeVoice`)
- Enable after core integration is stable

Voice is optional by design. Core functionality does not require voice components.
