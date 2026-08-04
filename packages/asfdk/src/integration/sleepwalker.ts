import { SleepwalkerProtocol } from '@neurolift-technologies/sleepwalker-protocol';
import type { EmotionalState } from '@neurolift-technologies/sleepwalker-protocol';
import { Channel, normalizeChannel } from '../types.js';

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
 */
export function detectEmotionalState(
  userInput: string,
  sessionHistory: unknown[] = [],
  channel?: Channel,
): EmotionalState {
  const resolved = normalizeChannel(channel ?? undefined);
  const state = getInstance().detectEmotionalState(userInput, sessionHistory);
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
