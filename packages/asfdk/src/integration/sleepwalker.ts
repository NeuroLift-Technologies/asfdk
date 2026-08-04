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
): EmotionalState {
  const resolved = normalizeChannel(channel ?? undefined);
  
  // Sanitize input before processing
  const sanitizationResult = sanitizeInput(userInput);
  if (!sanitizationResult.clean) {
    logSecurityEvent({
      type: sanitizationResult.riskLevel === 'HIGH' ? 'INJECTION_ATTEMPT' : 'VALIDATION_FAILURE',
      userId: 'unknown', // Will be overridden by caller context
      details: sanitizationResult.reason || 'Input sanitization failed',
      timestamp: Date.now(),
    });
    
    // Return safe default state for suspicious input
    const safeState: EmotionalState & { channel: Channel; trusted: boolean; flagged: boolean; flagReason?: string } = {
      stateType: 'neutral',
      protective: true,
      requiresCheckIn: false,
      indicators: {
        dissociation: false,
        numbing: false,
        avoidance: false,
        detachment: false,
        crisis: {
          suicidalIdeation: false,
          selfHarm: false,
          safetyConcern: false,
        },
      },
      confidence: 0,
      explicitSuicidalIdeation: false,
      selfHarmIndicators: false,
      inabilityToEnsureSafety: false,
      flagged: true,
      flagReason: sanitizationResult.reason,
      channel: resolved,
      trusted: resolved === Channel.USER_INPUT,
    };
    
    return safeState;
  }
  
  const state = getInstance().detectEmotionalState(sanitizationResult.content, sessionHistory);
  const withProvenance = state as EmotionalState & { channel: Channel; trusted: boolean };
  withProvenance.channel = resolved;
  withProvenance.trusted = resolved === Channel.USER_INPUT;
  return withProvenance;
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
