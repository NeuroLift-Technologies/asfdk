import { SleepwalkerProtocol } from 'sleepwalker-protocol';
import type { EmotionalState } from 'sleepwalker-protocol';

export type { EmotionalState };

let instance: SleepwalkerProtocol | undefined;

function getInstance(): SleepwalkerProtocol {
  if (!instance) {
    instance = new SleepwalkerProtocol({ loggingEnabled: false });
  }
  return instance;
}

export function detectEmotionalState(
  userInput: string,
  sessionHistory: unknown[] = [],
): EmotionalState {
  return getInstance().detectEmotionalState(userInput, sessionHistory);
}

export function assessInteraction(userInput: string, sessionHistory: unknown[] = []): unknown {
  return getInstance().assessInteraction(userInput, sessionHistory);
}

export function requiresRrtaHandoff(state: EmotionalState): boolean {
  return getInstance().requiresRrtaHandoff(state);
}

export function getStatus(): { active: boolean; mode: string } {
  return { active: true, mode: 'emotional-continuity' };
}

export function reset(): void {
  instance = undefined;
}
