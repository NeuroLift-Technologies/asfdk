import { CrisisEngine, CrisisLevel, type CrisisAssessment } from '@neurolift-technologies/rrt-advocate';
import { Channel, normalizeChannel } from '../types.js';
import { sanitizeInput, logSecurityEvent } from '../prompt-defense.js';

export { CrisisLevel, Channel, normalizeChannel };
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
 * Security: Input is sanitized to prevent prompt injection attacks before assessment.
 *
 * Channel provenance (D4): the resolved channel and its derived `trusted` flag
 * are recorded additively on the returned assessment. The assessment object is
 * fresh per call, so provenance never bleeds between responses.
 *
 * Observe-phase caveat: the per-user engine is shared across channels, so an
 * untrusted assessment may still mutate engine state here. Per-channel engines
 * are deferred to Enforce; `resetSession` is the documented re-baseline hook
 * Enforce will call when an untrusted assessment is discarded.
 *
 * @param userId - The user the assessment is scored against.
 * @param input - Free-text user input to assess.
 * @param channel - Optional channel the interaction arrived on; absent → `unknown`.
 */
export async function assess(
  userId: string,
  input: string,
  channel?: Channel,
): Promise<CrisisAssessment> {
  const resolved = normalizeChannel(channel ?? undefined);
  
  // Sanitize input before processing
  const sanitizationResult = sanitizeInput(input);
  if (!sanitizationResult.clean) {
    logSecurityEvent({
      type: sanitizationResult.riskLevel === 'HIGH' ? 'INJECTION_ATTEMPT' : 'VALIDATION_FAILURE',
      userId,
      details: sanitizationResult.reason || 'Input sanitization failed in RRT assessment',
      timestamp: Date.now(),
    });
    
    // Return safe default assessment for suspicious input
    const safeAssessment: CrisisAssessment & { channel: Channel; trusted: boolean; flagged: boolean; flagReason?: string } = {
      timestamp: new Date(),
      crisisLevel: CrisisLevel.GREEN,
      primaryIndicators: [],
      secondaryIndicators: [],
      confidenceScore: 0,
      estimatedDuration: null,
      recommendedInterventions: [],
      escalationThreshold: 0,
      userSafetyScore: 1.0,
      contextFactors: {},
      flagged: true,
      flagReason: sanitizationResult.reason,
      channel: resolved,
      trusted: resolved === Channel.USER_INPUT,
    };
    
    return safeAssessment;
  }
  
  const assessment = await getEngine(userId).assess(sanitizationResult.content);
  const withProvenance = assessment as CrisisAssessment & { channel: Channel; trusted: boolean };
  withProvenance.channel = resolved;
  withProvenance.trusted = resolved === Channel.USER_INPUT;
  return withProvenance;
}

/**
 * Re-baselines a single user's crisis-detection engine (delegates to
 * {@link CrisisEngine.resetSession}). Enforce-phase hook: call after discarding
 * an untrusted assessment so engine state cannot carry it forward.
 */
export function resetSession(userId: string): void {
  getEngine(userId).resetSession();
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
