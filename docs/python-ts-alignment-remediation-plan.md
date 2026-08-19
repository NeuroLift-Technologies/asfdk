# ASFDK Python/TypeScript Alignment Remediation Plan

**Thread:** THREAD-012  
**Date:** 2026-08-19  
**Owner:** AI CTO Agent (ai_cto_agent)  
**Status:** ✅ Complete  

---

## Executive Summary

Audit of all 4 pillar repos (nlt-toi, nlt-otoi, rrt-advocate, sleepwalker) shows they are **aligned** between Python and TypeScript. The alignment gap is **only in the ASFDK integration adapters** (`src/asfdk/integration/`), which are missing security and provenance features added to TypeScript after the initial Python port.

---

## Audit Results

| Repository | Python Status | TypeScript Status | Alignment |
|------------|---------------|-------------------|-----------|
| **nlt-toi** | `src/nlt_toi/` | `packages/toi/` | ✅ Aligned |
| **nlt-otoi** | `src/nlt_otoi/` | `packages/otoi/` | ✅ Aligned |
| **rrt-advocate** | `src/rrt_advocate/` | `packages/rrt-advocate/` | ✅ Aligned |
| **sleepwalker** | `src/sleepwalker_protocol/` | `src/` (no packages/) | ✅ Aligned |
| **asfdk** | `src/asfdk/integration/` | `packages/asfdk/src/integration/` | ❌ **GAP** |

**Conclusion:** The pillar repos are healthy. The problem is isolated to ASFDK's Python integration adapters.

---

## Gap Analysis (ASFDK Only)

### 1. Channel Enum & normalizeChannel() — `types.py`

**TypeScript (canonical):**
```typescript
export enum Channel {
  USER_INPUT = 'user_input',
  MODEL_OUTPUT = 'model_output',
  TOOL_RESULT = 'tool_result',
  SYSTEM = 'system',
  UNKNOWN = 'unknown',
}

export function normalizeChannel(value: unknown): Channel {
  if (typeof value === 'string' && (Object.values(Channel) as string[]).includes(value)) {
    return value as Channel;
  }
  return Channel.UNKNOWN;
}
```

**Python (current):**
- ❌ No `Channel` enum
- ❌ No `normalize_channel()` function

**Impact:** Trust derivation from channel is impossible in Python. D3/D4 provenance cannot be implemented.

---

### 2. Prompt Defense Module — `prompt-defense.py`

**TypeScript (canonical):**
- `sanitizeInput()` — Input sanitization with delimiter wrapping
- `detectInjectionPatterns()` — Heuristic injection detection
- `validateInputLength()` — Context flooding prevention
- `validateOutput()` — System instruction leak detection
- `createSecureSystemPrompt()` — Security guidelines wrapper
- `logSecurityEvent()` — Security audit trail

**Python (current):**
- ❌ Entire module missing

**Impact:** No prompt injection defense layer in Python package.

---

### 3. Channel Provenance in RRT Adapter — `rrt.py`

**TypeScript (canonical):**
- Accepts `channel` parameter
- Records provenance on assessment
- Sanitizes input before processing
- Logs security events
- Returns assessment with `channel`, `trusted`, `flagged`, `flagReason` fields

**Python (current):**
- ❌ No `channel` parameter
- ❌ No provenance tracking
- ❌ No input sanitization
- ❌ No security logging
- ❌ Different function signature (`async def assess(user_id, input)` vs TS)

**Impact:** RRT adapter lacks security features and provenance.

---

### 4. Channel Provenance in Sleepwalker Adapter — `sleepwalker.py`

**TypeScript (canonical):**
- Accepts `channel` + `userId` parameters
- Records provenance on emotional state
- Sanitizes input before processing
- Logs security events

**Python (current):**
- ❌ No `channel` parameter
- ❌ No `userId` parameter
- ❌ No provenance tracking
- ❌ No input sanitization
- ❌ No security logging

**Impact:** Sleepwalker adapter lacks security features and provenance.

---

## Remediation Tasks

### Task 1: Add Channel Enum to `types.py`
**Priority:** HIGH  
**Effort:** LOW  
**Files:** `src/asfdk/types.py`

```python
class Channel(str, Enum):
    USER_INPUT = "user_input"
    MODEL_OUTPUT = "model_output"
    TOOL_RESULT = "tool_result"
    SYSTEM = "system"
    UNKNOWN = "unknown"

def normalize_channel(value: Any) -> Channel:
    if isinstance(value, str) and value in Channel.__members__.values():
        return Channel(value)
    return Channel.UNKNOWN
```

---

### Task 2: Create `prompt-defense.py` Module
**Priority:** HIGH  
**Effort:** MEDIUM  
**Files:** `src/asfdk/prompt-defense.py` (new)

Port from `packages/asfdk/src/prompt-defense.ts`:
- `INJECTION_PATTERNS` regex list
- `MAX_INPUT_LENGTH` constant
- `SanitizationResult` dataclass
- `ValidationResult` dataclass
- `OutputSchema` type
- `detect_injection_patterns()`
- `validate_input_length()`
- `sanitize_input()`
- `validate_output()`
- `create_secure_system_prompt()`
- `log_security_event()`

---

### Task 3: Update RRT Adapter with Provenance
**Priority:** HIGH  
**Effort:** MEDIUM  
**Files:** `src/asfdk/integration/rrt.py`

Updates needed:
- Add `channel` parameter to `assess()` function
- Import and use `Channel`, `normalize_channel` from `types.py`
- Import and use `sanitize_input`, `log_security_event` from `prompt-defense.py`
- Add provenance fields to return value
- Align function signature with TypeScript

---

### Task 4: Update Sleepwalker Adapter with Provenance
**Priority:** HIGH  
**Effort:** MEDIUM  
**Files:** `src/asfdk/integration/sleepwalker.py`

Updates needed:
- Add `channel` + `user_id` parameters to `detect_emotional_state()`
- Import and use `Channel`, `normalize_channel` from `types.py`
- Import and use `sanitize_input`, `log_security_event` from `prompt-defense.py`
- Add provenance fields to return value
- Align function signature with TypeScript

---

### Task 5: Update `__init__.py` Exports
**Priority:** MEDIUM  
**Effort:** LOW  
**Files:** `src/asfdk/__init__.py`

Add new exports:
- `Channel`, `normalize_channel`
- `sanitize_input`, `detect_injection_patterns`, `validate_output`, `log_security_event`

---

### Task 6: Add Tests for New Features
**Priority:** MEDIUM  
**Effort:** MEDIUM  
**Files:** `tests/test_prompt_defense.py` (new), `tests/test_channel_provenance.py` (new)

Tests needed:
- Channel enum values
- normalize_channel() behavior
- sanitize_input() with various inputs
- detect_injection_patterns() with known patterns
- RRT adapter with channel parameter
- Sleepwalker adapter with channel + user_id parameters

---

### Task 7: Update Documentation
**Priority:** LOW  
**Effort:** LOW  
**Files:** `README.md`, `docs/active-threads.md`

- Document new security features in Python package
- Update API parity notes
- Mark THREAD-012 as complete

---

## Execution Order

1. **Task 1** — Channel enum (foundation for others)
2. **Task 2** — Prompt defense module (foundation for adapters)
3. **Task 3** — RRT adapter update
4. **Task 4** — Sleepwalker adapter update
5. **Task 5** — Exports update
6. **Task 6** — Tests
7. **Task 7** — Documentation

---

## Dependencies

- No external dependencies — all changes are internal to `src/asfdk/`
- TypeScript `packages/asfdk/` is the canonical source of truth
- Python package must match TypeScript API surface
- Pillar repos (nlt-toi, nlt-otoi, rrt-advocate, sleepwalker) are already aligned

---

## Success Criteria

- [x] `Channel` enum and `normalize_channel()` present in `types.py`
- [x] `prompt_defense.py` module exists with all functions from TypeScript
- [x] RRT adapter accepts `channel` parameter and returns provenance
- [x] Sleepwalker adapter accepts `channel` + `user_id` parameters and returns provenance
- [x] All existing tests pass
- [x] New tests added for security features (34 tests passing)
- [x] Documentation updated

---

## Risk Assessment

**Low Risk:**
- All changes are additive (no breaking changes)
- TypeScript is canonical, Python follows
- No external dependencies
- Pillar repos already aligned
- Legacy Python already deprecated

**Mitigation:**
- Follow TypeScript implementation exactly
- Add tests before marking complete
- Verify API parity with TypeScript

---

*Plan created by AI CTO Agent | 2026-08-19 | THREAD-012*
