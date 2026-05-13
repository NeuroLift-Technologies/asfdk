# ASFDK-Deploy Quickstart

Integrate ASFDK into existing claws (Agent Wrappers) without rewriting your entire stack.

This guide is for teams that already have production or pre-production wrappers and want to add a Solidarity Layer between model and agent orchestration.

---

## What You’re Integrating

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

- Existing wrapper runtime with identifiable model↔agent boundary
- Request/response schema visibility
- Rollout strategy (staging/canary/production)
- Profile decision:
  - `core_only` (recommended initial rollout)
  - `voice_enabled` (optional)

---

## Quick Start Steps

1. Find the integration boundary:
   - model call context
   - agent orchestration/execution
2. Map wrapper I/O to ASFDK contract:
   - normalized request context
   - governed directives
   - trace metadata
3. Start with `core_only` profile.
4. Roll out in phases:
   - Passive
   - Advisory
   - Active
5. Validate each phase and promote only when stable.

---

## Next Steps

- If building new agents instead: `docs/dev/quickstart.md`
