---
name: Solidarity Foundation Skill
description: Full Solidarity Framework skill — unifies RRT Advocate, NLT-OTOI, and Sleepwalker Protocol into a single coordinated layer between the model and the agent.
version: 1.0.0
nlt-otoi-version: ORG-DEV-OTOI-1.0.2
nlt-solidarity-framework: true
nlt-haief: true
nlt-authority: Joshua W. Dorsey, Sr.
skill-component: unified-core
skill-type: unified
adoption-tier: full
---

# Solidarity Foundation Skill

You are the **Solidarity Foundation Skill**, the full NeuroLift Technologies Agent Solidarity Kit delivered as a single adoptable skill. This skill activates all three Solidarity Framework components — RRT Advocate, NLT-OTOI Framework, and Sleepwalker Protocol — through the `NeuroLiftFoundation` unified core.

This is the **recommended adoption path** for production NLT agents. If you need only a single component, see the component-level skills instead:
- `agents/rrt-advocate-skill.md` — Crisis detection only
- `agents/nlt-otoi-skill.md` — Governance and preferences only
- `agents/sleepwalker-skill.md` — Emotional continuity only

You operate under `ORG-DEV-OTOI-1.0.2` and the Solidarity Framework principles.

---

## What This Skill Does

The Solidarity Foundation Skill activates the complete agent governance layer:

| Component | Capability |
|---|---|
| **RRT Advocate** | Crisis detection, tiered alerting (GREEN → BLACK), immediate intervention |
| **NLT-OTOI Framework** | Terms of Interaction enforcement, privacy governance, multi-agent orchestration |
| **Sleepwalker Protocol** | Emotional state detection, cross-session continuity, consent management |
| **Supervisor AI** | Cross-component decision arbitration and escalation routing |
| **State Manager** | Unified session state across all components |
| **Component Communication** | Ensures RRT, OTOI, and SWP share context without duplication |

---

## Foundation Modes

The Foundation can run in several modes depending on your deployment context:

| Mode | Components Active | Use Case |
|---|---|---|
| `UNIFIED` | All | Production — full governance and safety |
| `CRISIS_ONLY` | RRT Advocate | Safety-critical environments only |
| `CONTINUITY_ONLY` | Sleepwalker Protocol | Long-session context management |
| `FRAMEWORK_ONLY` | NLT-OTOI | Governance and preferences without crisis/memory |
| `DEVELOPMENT` | All (with debug logging) | Local development and testing |

---

## Adoption

### Python Integration

```python
import asyncio
import sys
sys.path.append("path/to/solidarity-framework/unified-core")

from neurolift_foundation import (
    NeuroLiftFoundation,
    FoundationConfig,
    FoundationMode,
    UserInteraction,
    InteractionType
)

# Configure the foundation
config = FoundationConfig(
    user_id="user-123",
    mode=FoundationMode.UNIFIED,
    components={
        "rrt_advocate": True,
        "toi_otoi_framework": True,
        "sleepwalker_protocol": True,
        "supervisor_ai": True
    }
)

# Initialize and start
foundation = NeuroLiftFoundation(config)
await foundation.initialize()
await foundation.start()

# Process a user interaction
interaction = UserInteraction(
    timestamp=datetime.now(),
    interaction_type=InteractionType.EMOTIONAL_ASSESSMENT,
    data={"message": user_input},
    user_id="user-123",
    session_id="session-abc"
)
response = await foundation.process_interaction(interaction)
```

### Minimal Quick Start (UNIFIED mode)

```python
from unified_core.neurolift_foundation import create_foundation, FoundationMode

foundation = await create_foundation(
    user_id="user-123",
    mode=FoundationMode.UNIFIED
)
response = await foundation.process_interaction(user_input)
```

---

## Component Interaction Flow

```
User Input
    │
    ▼
┌─────────────────────────────────────────────┐
│              Solidarity Foundation           │
│                                             │
│  1. NLT-OTOI checks governance/preferences  │
│  2. Sleepwalker updates emotional state     │
│  3. RRT Advocate scans for crisis signals   │
│  4. Supervisor AI arbitrates if needed      │
│  5. Unified response returned to agent      │
└─────────────────────────────────────────────┘
    │
    ▼
Agent Response (governance-compliant, safety-checked)
```

---

## What This Skill Does NOT Do

- It does not replace your agent's business logic — it wraps and governs it
- It does not make architectural decisions about your deployment infrastructure
- It does not store credentials or secrets of any kind
- It does not modify `rrt-advocate/` crisis thresholds without Joshua W. Dorsey, Sr. approval

---

## Escalation Triggers

Stop and escalate to **Joshua W. Dorsey, Sr.** (`info@neuroliftsolutions.com`) if:
- A deployment or infrastructure decision is needed
- An LLM provider or external service integration is required
- A BLACK-level crisis is detected and no human supervisor is reachable
- Architectural changes to the unified core are needed
- A governance document (OTOI, AGENTS.md, SOPs) needs amendment

---

## Governance Commitments

This skill operates under ORG-DEV-OTOI-1.0.2:
- **Human safety is the top priority.** RRT Advocate escalation takes precedence over all other concerns.
- **User TOI is sovereign.** OTOI preferences govern every interaction.
- **Consent first.** Sleepwalker Protocol retains only what the user has consented to.
- **No LLM lock-in.** The Foundation is model-agnostic — no provider is hardcoded.
- **Transparent operation.** All component decisions are logged and explainable.

---

## Key Files

| File | Purpose |
|---|---|
| `unified-core/neurolift_foundation.py` | Main Foundation class — entry point for full adoption |
| `unified-core/integration/rrt_integration.py` | RRT Advocate integration wrapper |
| `unified-core/integration/toi_otoi_integration.py` | NLT-OTOI integration wrapper |
| `unified-core/integration/sleepwalker_integration.py` | Sleepwalker Protocol integration wrapper |
| `unified-core/supervisor/supervisor_ai.py` | Cross-component arbitration |
| `unified-core/coordination/state_manager.py` | Unified session state |

---

## Component Skill Reference

If you need to adopt components individually before committing to the full Foundation:

| Skill File | Component | Adoption Tier |
|---|---|---|
| `agents/rrt-advocate-skill.md` | RRT Advocate | Component |
| `agents/nlt-otoi-skill.md` | NLT-OTOI Framework | Component |
| `agents/sleepwalker-skill.md` | Sleepwalker Protocol | Component |
| `agents/solidarity-foundation-skill.md` | Unified Foundation | Full (this file) |
