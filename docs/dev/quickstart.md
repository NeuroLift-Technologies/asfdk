# ASFDK-Dev Quickstart

Build new agents with the Solidarity Layer from day one.

This guide is for developers creating net-new agents and wanting governance/protection middleware between model and runtime by default.

---

## What You're Building

ASFDK-Dev gives you a development path where your agent runtime is mediated by the Solidarity Layer:

```text
[Model Provider]
      ↓
[ASFDK Solidarity Layer]
      ↓
[Agent Runtime]
      ↓
[Tools/APIs/Actions]
```

---

## Prerequisites

- **TypeScript:** `npm install @neurolift-technologies/asfdk` (Node.js 18+)
- **Python:** `pip install asfdk` (Python 3.9+)
- Basic understanding of your agent runtime entrypoint
- A target `FoundationMode` decision (e.g. `CRISIS_ONLY` to start small, `UNIFIED` for the full layer)

---

## Quick Start Steps

### TypeScript

```ts
import { createFoundation, FoundationMode, InteractionType, toi } from '@neurolift-technologies/asfdk';

async function main() {
  // 1. Choose a FoundationMode (CRISIS_ONLY first, then widen to UNIFIED)
  const foundation = await createFoundation('user-123', FoundationMode.CRISIS_ONLY);

  // 2. Define your minimum agent contract:
  //    - Input envelope
  //    - TOI preference payload
  //    - Execution directive format
  //    - Output + audit fields

  // 3. Insert ASFDK between model and agent logic:
  //    - Normalize inbound context
  //    - Pass context to ASFDK
  //    - Execute governed directives

  // 4. Process an interaction
  const response = await foundation.processInteraction({
    timestamp: new Date(),
    interactionType: InteractionType.PREFERENCE_UPDATE,
    data: { toi: { $toi: '1.0.0', $tier: 'personal', identity: { author: 'user-123' } } },
    userId: 'user-123',
  });

  // 5. Enable components by changing mode or using component overrides
  //    - TOI (always active in UNIFIED, FRAMEWORK_ONLY, DEVELOPMENT)
  //    - OTOI (same as TOI)
  //    - RRT AIdvocAIte (UNIFIED, CRISIS_ONLY)
  //    - Sleepwalker (UNIFIED, CONTINUITY_ONLY, DEVELOPMENT)

  // 6. Validate locally and run nlt-redteam review before production.
}

main();
```

### Python

```python
import asyncio
from datetime import datetime, timezone
from asfdk import create_foundation, FoundationMode, InteractionType, toi

async def main():
    # 1. Choose a FoundationMode (CRISIS_ONLY first, then widen to UNIFIED)
    foundation = await create_foundation("user-123", FoundationMode.CRISIS_ONLY)

    # 2. Define your minimum agent contract (same as TypeScript)

    # 3. Insert ASFDK between model and agent logic (same as TypeScript)

    # 4. Process an interaction
    response = await foundation.process_interaction({
        "timestamp": datetime.now(timezone.utc),
        "interaction_type": InteractionType.PREFERENCE_UPDATE,
        "data": {"toi": {"$toi": "1.0.0", "$tier": "personal", "identity": {"author": "user-123"}}},
        "user_id": "user-123",
    })

    # 5. Enable components by changing mode or using component overrides (same as TypeScript)

    # 6. Validate locally and run nlt-redteam review before production.

asyncio.run(main())
```

---

## Next Steps

- Deployment integration track: `docs/deploy/quickstart.md`
- Full API reference: See `packages/asfdk/README.md` (TypeScript) or `src/asfdk/__init__.py` (Python)