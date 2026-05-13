# ASFDK-Dev Quickstart

Build new agents with the Solidarity Layer from day one.

This guide is for developers creating net-new agents and wanting governance/protection middleware between model and runtime by default.

---

## What You’re Building

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

- Repository cloned locally (`git clone https://github.com/NeuroLift-Technologies/solidarity-framework.git`)
- Python 3.10+ and Node.js 18+ installed
- Dependencies installed via `pip install -r requirements.txt`
- Basic understanding of your agent runtime entrypoint
- A target profile decision:
  - `core_only` (recommended)
  - `voice_enabled` (optional)

---

## Quick Start Steps

1. Choose a profile (`core_only` first, then optional `voice_enabled`).
2. Define your minimum agent contract:
   - Input envelope
   - TOI preference payload
   - Execution directive format
   - Output + audit fields
3. Insert ASFDK between model and agent logic:
   - Normalize inbound context
   - Pass context to ASFDK
   - Execute governed directives
4. Enable components:
   - TOI (always active)
   - OTOI (for multi-agent flows)
   - RRT AIdvocAIte (contextual)
   - Sleepwalker (continuity)
5. Validate locally and run nlt-redteam review before production.

---

## Next Steps

- Deployment integration track: `docs/deploy/quickstart.md`
