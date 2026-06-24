import { CrisisEngine, CrisisLevel, type CrisisAssessment } from '@neurolift-technologies/rrt-advocate';

export { CrisisLevel };
export type { CrisisAssessment };

/**
 * ⚠️ PROTOTYPE — NOT A SAFETY SYSTEM.
 *
 * This adapter wraps `@neurolift-technologies/rrt-advocate`, an **experimental**
 * crisis-*detection* library with stubbed intervention layers. It is **not
 * medical advice, not a crisis service**, performs no real-time monitoring, and
 * **can miss real crisis signals**. Never rely on it as the sole safety
 * mechanism. If you or someone else needs help now, in the US call or text
 * **988** or chat https://988lifeline.org.
 */

// One engine per user — the assessor scores user safety against per-user state,
// so engines are not shared across users.
const engines = new Map<string, CrisisEngine>();

function getEngine(userId: string): CrisisEngine {
  let engine = engines.get(userId);
  if (!engine) {
    engine = new CrisisEngine(userId);
    engines.set(userId, engine);
  }
  return engine;
}

/**
 * Runs the 3-layer crisis-detection engine on a free-text input and returns a
 * {@link CrisisAssessment} (crisis level, safety score, recommended interventions).
 *
 * @param userId - The user the assessment is scored against.
 * @param input - Free-text user input to assess.
 */
export async function assess(userId: string, input: string): Promise<CrisisAssessment> {
  return getEngine(userId).assess(input);
}

/** Returns the active RRT Advocate component status. */
export function getStatus(): { active: boolean; mode: string } {
  return { active: true, mode: 'crisis-detection' };
}

/**
 * Resets per-session detector state. Pass a `userId` to reset a single user's
 * engine, or omit it to clear all cached engines.
 */
export function reset(userId?: string): void {
  if (userId === undefined) {
    engines.clear();
    return;
  }
  engines.delete(userId);
}
