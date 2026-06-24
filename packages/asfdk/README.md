# @neurolift-technologies/asfdk

**Agent Solidarity Framework Development Kit — TypeScript.**

ASFDK is the TypeScript umbrella over the four Solidarity Framework pillars. It
ships a high-level orchestrator (`NeuroLiftFoundation`) and re-exports each pillar
package so a single install gives you every layer of the model ↔ agent boundary:

| Pillar | Package | Role |
|---|---|---|
| **TOI** | [`@neurolift-technologies/toi`](https://www.npmjs.com/package/@neurolift-technologies/toi) | Terms of Interaction — user-preference governance |
| **OTOI** | [`@neurolift-technologies/otoi`](https://www.npmjs.com/package/@neurolift-technologies/otoi) | Orchestrated TOI — multi-agent honoring layer |
| **RRT Advocate** | [`@neurolift-technologies/rrt-advocate`](https://www.npmjs.com/package/@neurolift-technologies/rrt-advocate) | Crisis detection ⚠️ *prototype* |
| **Sleepwalker Protocol** | [`@neurolift-technologies/sleepwalker-protocol`](https://www.npmjs.com/package/@neurolift-technologies/sleepwalker-protocol) | Emotional continuity across drift |

## Install

```sh
npm install @neurolift-technologies/asfdk
```

The four pillar packages are declared as dependencies, so they are installed
transitively — you do not need to install them separately.

## Usage

```ts
import { createFoundation, FoundationMode, InteractionType, toi } from '@neurolift-technologies/asfdk';

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
```

### Foundation modes

| Mode | TOI/OTOI | Sleepwalker | RRT Advocate |
|---|---|---|---|
| `UNIFIED` | ✅ | ✅ | ✅ |
| `CRISIS_ONLY` | — | — | ✅ |
| `CONTINUITY_ONLY` | — | ✅ | — |
| `FRAMEWORK_ONLY` | ✅ | — | — |
| `DEVELOPMENT` | ✅ | ✅ | — |

Per-component overrides are available via `FoundationConfig.components`.

## ⚠️ Crisis detection is a prototype — not a safety system

The RRT Advocate layer wraps an **experimental** crisis-*detection* library with
stubbed intervention layers. It is **not medical advice, not a crisis service**,
performs no real-time monitoring, and **can miss real crisis signals**. Never
rely on it as the sole safety mechanism. If you or someone else needs help now,
in the US call or text **988** or chat [988lifeline.org](https://988lifeline.org).

## License

MIT — © NeuroLift Technologies. Part of the
[Solidarity Framework](https://github.com/NeuroLift-Technologies/solidarity-framework)
and governed by the NLT-DEV-OTOI contract.
