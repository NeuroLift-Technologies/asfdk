import {
  FoundationConfig,
  FoundationMode,
  FoundationResponse,
  HealthCheckResult,
  InteractionType,
  UserInteraction,
} from './types.js';
import * as toiOtoi from './integration/toi-otoi.js';
import * as sleepwalker from './integration/sleepwalker.js';
import * as rrt from './integration/rrt.js';

function componentsForMode(mode: FoundationMode, overrides?: FoundationConfig['components']): {
  toi: boolean;
  swp: boolean;
  rrt: boolean;
} {
  const defaults = {
    [FoundationMode.UNIFIED]: { toi: true, swp: true, rrt: true },
    [FoundationMode.CRISIS_ONLY]: { toi: false, swp: false, rrt: true },
    [FoundationMode.CONTINUITY_ONLY]: { toi: false, swp: true, rrt: false },
    [FoundationMode.FRAMEWORK_ONLY]: { toi: true, swp: false, rrt: false },
    [FoundationMode.DEVELOPMENT]: { toi: true, swp: true, rrt: false },
  };
  const base = defaults[mode] ?? { toi: false, swp: false, rrt: false };
  return {
    toi: overrides?.toi_otoi_framework ?? base.toi,
    swp: overrides?.sleepwalker_protocol ?? base.swp,
    rrt: overrides?.rrt_advocate ?? base.rrt,
  };
}

export class NeuroLiftFoundation {
  private readonly config: FoundationConfig;
  private readonly active: ReturnType<typeof componentsForMode>;
  private initialized = false;

  constructor(config: FoundationConfig) {
    this.config = config;
    this.active = componentsForMode(config.mode, config.components);
  }

  async initialize(): Promise<void> {
    this.initialized = true;
  }

  async start(): Promise<void> {
    if (!this.initialized) await this.initialize();
  }

  async processInteraction(interaction: UserInteraction): Promise<FoundationResponse> {
    const components: string[] = [];
    const content: Record<string, unknown> = {};

    if (this.active.swp && interaction.interactionType === InteractionType.EMOTIONAL_ASSESSMENT) {
      const input = String(interaction.data?.['text'] ?? '');
      const state = sleepwalker.detectEmotionalState(input);
      content.emotionalState = state;
      components.push('sleepwalker_protocol');

      if (this.active.rrt && sleepwalker.requiresRrtaHandoff(state)) {
        content.rrt = rrt.assess(input);
        components.push('rrt_advocate');
      }
    }

    if (this.active.toi && interaction.interactionType === InteractionType.PREFERENCE_UPDATE) {
      const result = await toiOtoi.validateTOI(interaction.data?.['toi']);
      content.toiValidation = result;
      components.push('toi_otoi_framework');
    }

    return {
      timestamp: new Date(),
      responseType: interaction.interactionType,
      content,
      componentsInvolved: components,
      success: true,
    };
  }

  async assessEmotionalState(
    input: string,
    _context?: Record<string, unknown>,
  ): Promise<unknown> {
    if (!this.active.swp) return null;
    return sleepwalker.assessInteraction(input);
  }

  async updatePreferences(prefs: Record<string, unknown>): Promise<void> {
    if (this.active.toi) {
      const result = await toiOtoi.validateTOI(prefs);
      if (!result.valid) {
        throw new Error('TOI validation failed: ' + JSON.stringify(result.errors));
      }
    }
  }

  getSystemStatus(): Record<string, unknown> {
    return {
      mode: this.config.mode,
      userId: this.config.userId,
      initialized: this.initialized,
      components: {
        toi_otoi_framework: this.active.toi ? toiOtoi.getStatus() : { active: false, mode: 'disabled' },
        sleepwalker_protocol: this.active.swp ? sleepwalker.getStatus() : { active: false, mode: 'disabled' },
        rrt_advocate: rrt.getStatus(),
      },
    };
  }

  async healthCheck(): Promise<HealthCheckResult> {
    return {
      healthy: true,
      timestamp: new Date(),
      components: {
        toi_otoi_framework: this.active.toi
          ? { active: true, mode: 'schema-validation' }
          : { active: false, mode: 'disabled' },
        sleepwalker_protocol: this.active.swp
          ? { active: true, mode: 'emotional-continuity' }
          : { active: false, mode: 'disabled' },
        rrt_advocate: { active: false, mode: 'stub-python-only' },
      },
    };
  }

  async shutdown(): Promise<void> {
    sleepwalker.reset();
    this.initialized = false;
  }
}
