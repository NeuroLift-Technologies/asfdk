# ASFDK-Deploy Quickstart

Integrate ASFDK into existing claws (Agent Wrappers) without rewriting your entire stack.

This guide is for teams that already have production or pre-production wrappers and want to add a Solidarity Layer between model and agent orchestration.

---

## What You're Integrating

ASFDK-Deploy inserts governance/protection middleware at your existing boundary:

```text
[Model Provider]
      ↓
[ASFDK Solidarity Layer]
      ↓
[Claws (Agent Wrappers)]
      ↓
[Tools/APIs/Actions]
```

---

## Prerequisites

- **TypeScript:** `npm install @neurolift-technologies/asfdk` (Node.js 18+)
- **Python:** `pip install asfdk` (Python 3.9+)
- Existing wrapper runtime with identifiable model↔agent boundary
- Request/response schema visibility
- Rollout strategy (staging/canary/production)
- A `FoundationMode` decision (`CRISIS_ONLY` for the lowest-impact initial rollout)

---

## Quick Start Steps

### TypeScript

```ts
import { createFoundation, FoundationMode, InteractionType } from '@neurolift-technologies/asfdk';

async function main() {
  // 1. Find the integration boundary:
  //    - model call context
  //    - agent orchestration/execution

  // 2. Start with CRISIS_ONLY for lowest-impact initial rollout
  const foundation = await createFoundation('user-123', FoundationMode.CRISIS_ONLY);

  // 3. Map wrapper I/O to ASFDK contract:
  //    - normalized request context
  //    - governed directives
  //    - trace metadata

  // 4. Process interactions at your boundary
  const response = await foundation.processInteraction({
    timestamp: new Date(),
    interactionType: InteractionType.CRISIS_ALERT,
    data: { text: "user message to assess" },
    userId: 'user-123',
  });

  // 5. Roll out in phases:
  //    - Passive (Observe): log only, high thresholds
  //    - Advisory (Advise): warn but don't gate
  //    - Active (Enforce): apply governance inline

  // 6. Validate each phase and promote only when stable.
  // 7. Validate against nlt-redteam before promoting to production.
}

main();
```

### Python

```python
import asyncio
from datetime import datetime, timezone
from asfdk import create_foundation, FoundationMode, InteractionType

async def main():
    # 1. Find the integration boundary (same as TypeScript)

    # 2. Start with CRISIS_ONLY for lowest-impact initial rollout
    foundation = await create_foundation("user-123", FoundationMode.CRISIS_ONLY)

    # 3. Map wrapper I/O to ASFDK contract (same as TypeScript)

    # 4. Process interactions at your boundary
    response = await foundation.process_interaction({
        "timestamp": datetime.now(timezone.utc),
        "interaction_type": InteractionType.CRISIS_ALERT,
        "data": {"text": "user message to assess"},
        "user_id": "user-123",
    })

    # 5. Roll out in phases (same as TypeScript)

    # 6. Validate each phase and promote only when stable.
    # 7. Validate against nlt-redteam before promoting to production.

asyncio.run(main())
```

---

## Next Steps

- If building new agents instead: `docs/dev/quickstart.md`
- Full API reference: See `packages/asfdk/README.md` (TypeScript) or `src/asfdk/__init__.py` (Python)