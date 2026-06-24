/**
 * `@neurolift-technologies/asfdk` — the Agent Solidarity Framework Development Kit.
 *
 * ASFDK is the TypeScript umbrella over the four Solidarity Framework pillars.
 * The {@link NeuroLiftFoundation} orchestrator is the high-level entry point; the
 * four pillar packages are also re-exported as namespaces so a single install
 * surfaces every layer:
 *
 * - `toi`         → `@neurolift-technologies/toi` (Terms of Interaction — user preferences)
 * - `otoi`        → `@neurolift-technologies/otoi` (Orchestrated TOI — multi-agent honoring)
 * - `rrt`         → `@neurolift-technologies/rrt-advocate` (crisis detection — ⚠️ prototype)
 * - `sleepwalker` → `@neurolift-technologies/sleepwalker-protocol` (emotional continuity)
 *
 * @example
 * ```ts
 * import { createFoundation, FoundationMode, toi } from '@neurolift-technologies/asfdk';
 *
 * const foundation = await createFoundation('user-123', FoundationMode.UNIFIED);
 * const result = toi.safeParseToi(myPreferences);
 * ```
 */

// High-level orchestrator (primary API).
export { FoundationMode, InteractionType } from './types.js';
export type { FoundationConfig, FoundationResponse, UserInteraction, HealthCheckResult } from './types.js';
export { NeuroLiftFoundation } from './foundation.js';
export { createFoundation } from './create-foundation.js';

// The four Solidarity Framework pillars, re-exported as namespaces.
export * as toi from '@neurolift-technologies/toi';
export * as otoi from '@neurolift-technologies/otoi';
export * as rrt from '@neurolift-technologies/rrt-advocate';
export * as sleepwalker from '@neurolift-technologies/sleepwalker-protocol';
