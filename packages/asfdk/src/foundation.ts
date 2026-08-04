import {
  Channel,
  FoundationConfig,
  FoundationMode,
  FoundationResponse,
  HealthCheckResult,
  InteractionType,
  normalizeChannel,
  UserInteraction,
} from './types.js';
import * as toiOtoi from './integration/toi-otoi.js';
import * as sleepwalker from './integration/sleepwalker.js';
import * as rrt from './integration/rrt.js';
import { validateOutput, logSecurityEvent } from './prompt-defense.js';

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
  const base = defaults[mode];
  // Fail-loud (T16): an unrecognized mode must never silently disable every
  // component — that would look like "governance off" instead of "bad config".
  if (!base) {
    throw new Error(`Unrecognized foundation mode: '${String(mode)}'`);
  }
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
   * Validates a component result (e.g. RRT) against the output contract.
   * On failure, logs a security event and returns `undefined` so the caller can
   * leave the corresponding `content.*` field unset — invalid output must never
   * reach a {@link FoundationResponse}.
   */
  private validateComponentOutput(result: unknown): unknown {
    if (result === null || result === undefined) return result;
    const outputValid = validateOutput(JSON.stringify(result), { type: 'json' });
    if (outputValid.valid) return result;
    logSecurityEvent({
      type: 'VALIDATION_FAILURE',
      userId: this.config.userId,
      details: `Component output validation failed: ${outputValid.reason}`,
      timestamp: Date.now(),
    });
    return undefined;
  }

  /**
   * Routes a {@link UserInteraction} to the appropriate active components and
   * returns a {@link FoundationResponse} with aggregated content.
   *
   * Security: Input is sanitized and output is validated to prevent prompt injection.
   *
   * - `EMOTIONAL_ASSESSMENT` → Sleepwalker Protocol (+ RRT handoff if crisis indicated)
   * - `PREFERENCE_UPDATE` → TOI-OTOI schema validation
   * - `CRISIS_ALERT` / `EMERGENCY_ESCALATION` → RRT Advocate crisis detection
   * - All other types → empty `componentsInvolved` array with `success: true`
   */
  async processInteraction(interaction: UserInteraction): Promise<FoundationResponse> {
    const components: string[] = [];
    const content: Record<string, unknown> = {};

    // Provenance (D2/D4/D6): resolve the channel from the TOP-LEVEL field only —
    // values nested inside data/context are ignored for trust (anti-spoofing).
    // Absent → 'unknown'; trusted := channel === 'user_input'.
    const channel = normalizeChannel(interaction.channel ?? undefined);
    const trusted = channel === Channel.USER_INPUT;

    // D5 gate-up predicate: untrusted channel AND high-severity crisis signal.
    let highSeverity = false;

    if (this.active.swp && interaction.interactionType === InteractionType.EMOTIONAL_ASSESSMENT) {
      try {
        const input = String(interaction.data?.['text'] ?? '');
        const state = sleepwalker.detectEmotionalState(input, [], channel, this.config.userId);
        // Emotional-path high-severity: explicit crisis flags on the state.
        highSeverity =
          state.explicitSuicidalIdeation || state.selfHarmIndicators || state.inabilityToEnsureSafety;
        content.emotionalState = state;

        if (this.active.rrt && sleepwalker.requiresRrtaHandoff(state)) {
          // Own error boundary so an RRT failure is attributed to rrt_advocate
          // (not sleepwalker) and does not discard the emotional-state result.
          try {
            const rrtResult = this.validateComponentOutput(await rrt.assess(this.config.userId, input, channel));
            if (rrtResult !== undefined) content.rrt = rrtResult;
          } catch (err) {
            content.error = { component: 'rrt_advocate', message: String(err) };
          }
          // Listed whenever attempted (success or failure), consistent with the
          // crisis/emergency route and with sleepwalker_protocol.
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
      // Error boundary: an RRT failure must not abort a crisis/emergency route.
      try {
        const rrtResult = this.validateComponentOutput(await rrt.assess(this.config.userId, input, channel));
        if (rrtResult !== undefined) content.rrt = rrtResult;
        // CRISIS_ALERT is high-severity only on an actual RED/BLACK reading; a
        // failed detection is not evidence of severity, so it does not gate up.
        if (interaction.interactionType === InteractionType.CRISIS_ALERT) {
          const level = (content.rrt as { crisisLevel?: rrt.CrisisLevel } | undefined)?.crisisLevel;
          highSeverity = level === rrt.CrisisLevel.RED || level === rrt.CrisisLevel.BLACK;
        }
      } catch (err) {
        content.error = { component: 'rrt_advocate', message: String(err) };
      }
      components.push('rrt_advocate');
    }

    // D5 high-severity fallbacks:
    // - EMERGENCY_ESCALATION is always high-severity.
    // - CRISIS_ALERT with RRT inactive is high-severity by interaction type
    //   alone (fail-safe: never silently ignored when detection is off).
    if (interaction.interactionType === InteractionType.EMERGENCY_ESCALATION) {
      highSeverity = true;
    }
    if (
      interaction.interactionType === InteractionType.CRISIS_ALERT &&
      !this.active.rrt
    ) {
      highSeverity = true;
    }

    content.channel = channel;
    content.trusted = trusted;
    content.gateUp = !trusted && highSeverity;

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
   * Channel provenance (D4) is recorded additively on the returned assessment —
   * no envelope — so existing consumers see the same shape plus `channel`,
   * `trusted`, and `gateUp` properties. Absent channel → `unknown`/untrusted.
   *
   * @param input - Free-text user input to assess.
   * @param _context - Reserved for future context enrichment; currently unused.
   * @param channel - Optional channel the interaction arrived on; absent → `unknown`.
   */
  async assessEmotionalState(
    input: string,
    _context?: Record<string, unknown>,
    channel?: Channel,
  ): Promise<unknown> {
    if (!this.active.swp) return null;
    const resolved = normalizeChannel(channel ?? undefined);
    const trusted = resolved === Channel.USER_INPUT;
    const result = sleepwalker.assessInteraction(input) as Record<string, unknown>;
    // assessInteraction nests the state; read the crisis flags from it (falling
    // back to the top level for flat-shaped callers).
    const inner = (result.emotionalState ?? result) as Record<string, unknown>;
    const highSeverity = Boolean(
      inner.explicitSuicidalIdeation ||
        inner.selfHarmIndicators ||
        inner.inabilityToEnsureSafety,
    );
    result.channel = resolved;
    result.trusted = trusted;
    result.gateUp = !trusted && highSeverity;
    return result;
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
