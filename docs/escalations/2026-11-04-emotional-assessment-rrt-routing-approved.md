# Escalation record (approved) — RRT routing for EMOTIONAL_ASSESSMENT

**Date:** 2026-11-04
**Agent / session:** Claude Code, session_01UNjnjm3TZ7Tg4MRswGt24P
**Branch:** ccr-0d5033af-1rkbla
**OTOI:** ORG-DEV-OTOI-1.0.3
**Status:** Approved by the owner in the originating session; PR is a draft for owner review.

## Why this is an escalation
This changes crisis-handling behavior of `NeuroLiftFoundation.processInteraction` / `process_interaction`, which adopters treat as a versioned public API (`CLAUDE.md`: changes to the foundation are breaking for adopters). No signature, enum, `create_foundation`, threshold, or `rrt-advocate` source file changes. Approval: the owner chose "Fix upstream with a test corpus" for the safety gaps (approving changes in `asfdk` for RRT coverage) and instructed "open a PR for the other 2" (asfdk-harness and asfdk) on 2026-11-04.

## Intended action
For `EMOTIONAL_ASSESSMENT`, call RRT whenever RRT is active, independent of Sleepwalker's `requiresRrtaHandoff` signal. Raise the high-severity flag (and so `gateUp` on untrusted channels) when RRT returns a critical or emergency level. In `CRISIS_ONLY` mode, where Sleepwalker is off, emotional assessments now reach RRT instead of being ignored. A Sleepwalker failure no longer skips RRT; an RRT failure is still attributed to `rrt_advocate` and keeps the Sleepwalker result. Applied to the TypeScript source of truth (`packages/asfdk/src/foundation.ts`) and the Python port (`src/asfdk/foundation.py`), with tests for both.

## Rationale
Measured with `@neurolift-technologies/asfdk` 0.2.4: "I want to die" returns emergency / 1.0 from the RRT engine directly, but the foundation never called RRT because Sleepwalker did not flag it, so a gate built on the foundation allowed it. `CRISIS_ONLY` mode produced no assessment at all for plain text.

## Risks and trust boundaries
- Behavior change for adopters: more `rrt_advocate` entries in `componentsInvolved` and a `content.rrt` on every emotional assessment in `UNIFIED`; `CRISIS_ONLY` now returns a result for emotional assessments. RRT keeps per-user engine state, so its history now includes every assessed message.
- More `gateUp` signals on untrusted channels (RRT high readings), by design.
- Limited effect on detection: this only routes input to RRT. Statements RRT's own patterns miss (rrt-advocate issue #49) or topic mentions it over-flags (issue #50) are unchanged.
- No change to thresholds or detection logic; no provider or deployment change.

## Alternatives considered
- Keep the Sleepwalker gate and widen Sleepwalker's detector: belongs in the sleepwalker repository, and would not help `CRISIS_ONLY`.
- Call RRT only when Sleepwalker's detector throws: leaves the missed-statement case open.

## Outcome
TypeScript: 7 new tests; 57 pass (50 before). Python: 7 new tests; 66 pass (59 before). Mutation checks (stashing the routing change, keeping the tests) fail 6 of 7 new tests in each language; the seventh asserts that modes without RRT are unchanged. `tsc --noEmit` passes. Version, changelog, build artifacts, and publishing are not touched.
