import { SleepwalkerProtocol } from '@neurolift-technologies/sleepwalker-protocol';
import type { EmotionalState } from '@neurolift-technologies/sleepwalker-protocol';

export type { EmotionalState };

let instance: SleepwalkerProtocol | undefined;

function getInstance(): SleepwalkerProtocol {
  if (!instance) {
    instance = new SleepwalkerProtocol({ loggingEnabled: false });
  }
  return instance;
}

/** Classifies the emotional state expressed in a user's free-text input. */
export function detectEmotionalState(
  userInput: string,
  sessionHistory: unknown[] = [],
): EmotionalState {
  return getInstance().detectEmotionalState(userInput, sessionHistory);
}

/** Returns a full interaction assessment object for the given input. */
export function assessInteraction(userInput: string, sessionHistory: unknown[] = []): unknown {
  return getInstance().assessInteraction(userInput, sessionHistory);
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
