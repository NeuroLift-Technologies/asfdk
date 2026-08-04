import { SleepwalkerProtocol } from '@neurolift-technologies/sleepwalker-protocol';
import type { EmotionalState } from '@neurolift-technologies/sleepwalker-protocol';
import { Channel, normalizeChannel } from '../types.js';
import { sanitizeInput, logSecurityEvent } from '../prompt-defense.js';

export { Channel, normalizeChannel };
export type { EmotionalState };

let instance: SleepwalkerProtocol | undefined;

function getInstance(): SleepwalkerProtocol {
  if (!instance) {
    instance = new SleepwalkerProtocol({ loggingEnabled: false });
  }
  return instance;
}

/**
 * Classifies the emotional state expressed in a user's free-text input.
 * The resolved channel and its derived `trusted` flag are recorded additively
 * on the returned state (absent channel → `unknown`).
 * 
 * Security: Input is sanitized to prevent prompt injection attacks.
 */
export function detectEmotionalState(
  userInput: string,
  sessionHistory: unknown[] = [],
  channel?: Channel,
  userId: string = 'unknown',
): EmotionalState & { channel: Channel; trusted: boolean; flagged?: boolean; flagReason?: string } {
  const resolved = normalizeChannel(channel ?? undefined);

  // Sanitize input before processing; a flagged result is logged but still
  // assessed defensively so a genuine signal is never silently suppressed by
  // an injection heuristic (fail-open on detection).
  const sanitizationResult = sanitizeInput(userInput);
  const flagged = !sanitizationResult.clean;
  if (flagged) {
    logSecurityEvent({
      type: sanitizationResult.riskLevel === 'HIGH' ? 'INJECTION_ATTEMPT' : 'VALIDATION_FAILURE',
      userId,
      details: sanitizationResult.reason || 'Input sanitization flagged in Sleepwalker assessment',
      timestamp: Date.now(),
    });
  }

  const state = getInstance().detectEmotionalState(sanitizationResult.content, sessionHistory) as EmotionalState & {
    channel: Channel;
    trusted: boolean;
    flagged?: boolean;
    flagReason?: string;
  };
  state.channel = resolved;
  state.trusted = resolved === Channel.USER_INPUT;
  if (flagged) {
    state.flagged = true;
    state.flagReason = sanitizationResult.reason;
  }
  return state;
}

/**
 * Returns a full interaction assessment object for the given input.
 * The resolved channel and its derived `trusted` flag are recorded additively
 * on the returned assessment (absent channel → `unknown`).
 */
export function assessInteraction(
  userInput: string,
  sessionHistory: unknown[] = [],
  channel?: Channel,
): unknown {
  const resolved = normalizeChannel(channel ?? undefined);
  const result = getInstance().assessInteraction(
    userInput,
    sessionHistory,
  ) as Record<string, unknown>;
  result.channel = resolved;
  result.trusted = resolved === Channel.USER_INPUT;
  return result;
}

/** Returns `true` when the assessed emotional state warrants an RRT Advocate handoff. */
export function requiresRrtaHandoff(state: EmotionalState): boolean {
  return getInstance().requiresRrtaHandoff(state);
}

/** Returns the active Sleepwalker Protocol component status. */
export function getStatus(): { active: boolean; mode: string } {
  return { active: true, mode: 'emotional-continuity' };
}

/** Resets the singleton instance; called during {@link NeuroLiftFoundation.shutdown}. */
export function reset(): void {
  instance = undefined;
}
