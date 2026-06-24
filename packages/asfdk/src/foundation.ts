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

/**
 * Central orchestrator for the Solidarity Framework.
 *
 * Routes user interactions to the active Solidarity Framework components
 * (TOI-OTOI, Sleepwalker Protocol, RRT Advocate) according to the
 * configured {@link FoundationMode}.
 *
 * Obtain an instance via {@link createFoundation} rather than constructing directly.
 */
export class NeuroLiftFoundation {
  private readonly config: FoundationConfig;
  private readonly active: ReturnType<typeof componentsForMode>;
  private initialized = false;

  constructor(config: FoundationConfig) {
    this.config = config;
    this.active = componentsForMode(config.mode, config.components);
  }

  /** Marks the foundation as initialized. Called automatically by {@link createFoundation}. */
  async initialize(): Promise<void> {
    this.initialized = true;
  }

  /** Alias for {@link initialize}; ensures the foundation is ready before use. */
  async start(): Promise<void> {
    if (!this.initialized) await this.initialize();
  }

  /**
   * Routes a {@link UserInteraction} to the appropriate active components and
   * returns a {@link FoundationResponse} with aggregated content.
   *
   * - `EMOTIONAL_ASSESSMENT` → Sleepwalker Protocol (+ RRT handoff if crisis indicated)
   * - `PREFERENCE_UPDATE` → TOI-OTOI schema validation
   * - `CRISIS_ALERT` / `EMERGENCY_ESCALATION` → RRT Advocate crisis detection
   * - All other types → empty `componentsInvolved` array with `success: true`
   */
  async processInteraction(interaction: UserInteraction): Promise<FoundationResponse> {
    const components: string[] = [];
    const content: Record<string, unknown> = {};

    if (this.active.swp && interaction.interactionType === InteractionType.EMOTIONAL_ASSESSMENT) {
      try {
        const input = String(interaction.data?.['text'] ?? '');
        const state = sleepwalker.detectEmotionalState(input);
        content.emotionalState = state;

        if (this.active.rrt && sleepwalker.requiresRrtaHandoff(state)) {
          content.rrt = await rrt.assess(this.config.userId, input);
          components.push('rrt_advocate');
        }
      } catch (err) {
        content.error = { component: 'sleepwalker_protocol', message: String(err) };
      }
      components.push('sleepwalker_protocol');
    }

    if (this.active.toi && interaction.interactionType === InteractionType.PREFERENCE_UPDATE) {
      content.toiValidation = toiOtoi.validateTOI(interaction.data?.['toi']);
      components.push('toi_otoi_framework');
    }

    if (
      this.active.rrt &&
      (interaction.interactionType === InteractionType.CRISIS_ALERT ||
        interaction.interactionType === InteractionType.EMERGENCY_ESCALATION)
    ) {
      const input = String(interaction.data?.['text'] ?? '');
      content.rrt = await rrt.assess(this.config.userId, input);
      components.push('rrt_advocate');
    }

    return {
      timestamp: new Date(),
      responseType: interaction.interactionType,
      content,
      componentsInvolved: components,
      success: true,
    };
  }

  /**
   * Assesses the emotional state of a free-text input via the Sleepwalker Protocol.
   * Returns `null` when Sleepwalker is not active for the current mode.
   *
   * @param input - Free-text user input to assess.
   * @param _context - Reserved for future context enrichment; currently unused.
   */
  async assessEmotionalState(
    input: string,
    _context?: Record<string, unknown>,
  ): Promise<unknown> {
    if (!this.active.swp) return null;
    return sleepwalker.assessInteraction(input);
  }

  /**
   * Validates a preference object against the TOI schema and throws if invalid.
   * No-op when TOI-OTOI is not active for the current mode.
   *
   * @throws {Error} If the preference object fails TOI schema validation.
   */
  async updatePreferences(prefs: Record<string, unknown>): Promise<void> {
    if (this.active.toi) {
      const result = toiOtoi.validateTOI(prefs);
      if (!result.valid) {
        throw new Error('TOI validation failed: ' + JSON.stringify(result.errors));
      }
    }
  }

  /** Returns the current mode, userId, initialization state, and per-component status. */
  getSystemStatus(): Record<string, unknown> {
    return {
      mode: this.config.mode,
      userId: this.config.userId,
      initialized: this.initialized,
      components: {
        toi_otoi_framework: this.active.toi ? toiOtoi.getStatus() : { active: false, mode: 'disabled' },
        sleepwalker_protocol: this.active.swp ? sleepwalker.getStatus() : { active: false, mode: 'disabled' },
        rrt_advocate: this.active.rrt ? rrt.getStatus() : { active: false, mode: 'disabled' },
      },
    };
  }

  /**
   * Returns a structured health report for all components, reflecting which are
   * active for the current {@link FoundationMode}.
   */
  async healthCheck(): Promise<HealthCheckResult> {
    return {
      healthy: true,
      timestamp: new Date(),
      components: {
        toi_otoi_framework: this.active.toi
          ? { active: true, mode: 'toi-otoi-validation' }
          : { active: false, mode: 'disabled' },
        sleepwalker_protocol: this.active.swp
          ? { active: true, mode: 'emotional-continuity' }
          : { active: false, mode: 'disabled' },
        rrt_advocate: this.active.rrt
          ? { active: true, mode: 'crisis-detection' }
          : { active: false, mode: 'disabled' },
      },
    };
  }

  /** Resets Sleepwalker and RRT Advocate state and marks the foundation as uninitialized. */
  async shutdown(): Promise<void> {
    sleepwalker.reset();
    rrt.reset(this.config.userId);
    this.initialized = false;
  }
}
