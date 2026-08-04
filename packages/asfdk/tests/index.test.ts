import { describe, it, expect } from 'vitest';
import {
  Channel,
  createFoundation,
  FoundationMode,
  InteractionType,
  NeuroLiftFoundation,
  toi,
  otoi,
  rrt,
  sleepwalker,
} from '../src/index.js';
import { normalizeChannel } from '../src/types.js';
import * as sleepwalkerAdapter from '../src/integration/sleepwalker.js';
import * as rrtAdapter from '../src/integration/rrt.js';

describe('createFoundation', () => {
  it('resolves with a NeuroLiftFoundation instance', async () => {
    const f = await createFoundation('test-user', FoundationMode.FRAMEWORK_ONLY);
    expect(f).toBeInstanceOf(NeuroLiftFoundation);
  });

  it('accepts a FoundationConfig object', async () => {
    const f = await createFoundation({ userId: 'test-user', mode: FoundationMode.DEVELOPMENT });
    expect(f).toBeInstanceOf(NeuroLiftFoundation);
  });
});

describe('NeuroLiftFoundation.healthCheck', () => {
  it('returns a well-formed health result', async () => {
    const f = await createFoundation('u1', FoundationMode.UNIFIED);
    const result = await f.healthCheck();
    expect(result.healthy).toBe(true);
    expect(result.timestamp).toBeInstanceOf(Date);
    expect(result.components).toHaveProperty('toi_otoi_framework');
    expect(result.components).toHaveProperty('sleepwalker_protocol');
    expect(result.components).toHaveProperty('rrt_advocate');
  });

  it('FRAMEWORK_ONLY mode has toi active and swp disabled', async () => {
    const f = await createFoundation('u1', FoundationMode.FRAMEWORK_ONLY);
    const result = await f.healthCheck();
    expect(result.components.toi_otoi_framework.active).toBe(true);
    expect(result.components.sleepwalker_protocol.active).toBe(false);
  });

  it('CONTINUITY_ONLY mode has swp active and toi disabled', async () => {
    const f = await createFoundation('u1', FoundationMode.CONTINUITY_ONLY);
    const result = await f.healthCheck();
    expect(result.components.toi_otoi_framework.active).toBe(false);
    expect(result.components.sleepwalker_protocol.active).toBe(true);
  });

  it('rrt_advocate is active with crisis detection in UNIFIED mode', async () => {
    const f = await createFoundation('u1', FoundationMode.UNIFIED);
    const result = await f.healthCheck();
    expect(result.components.rrt_advocate.active).toBe(true);
    expect(result.components.rrt_advocate.mode).toBe('crisis-detection');
  });

  it('rrt_advocate is disabled in FRAMEWORK_ONLY mode', async () => {
    const f = await createFoundation('u1', FoundationMode.FRAMEWORK_ONLY);
    const result = await f.healthCheck();
    expect(result.components.rrt_advocate.active).toBe(false);
    expect(result.components.rrt_advocate.mode).toBe('disabled');
  });
});

describe('NeuroLiftFoundation.getSystemStatus', () => {
  it('returns the mode and userId', async () => {
    const f = await createFoundation('joshua', FoundationMode.CRISIS_ONLY);
    const status = f.getSystemStatus();
    expect(status.mode).toBe(FoundationMode.CRISIS_ONLY);
    expect(status.userId).toBe('joshua');
    expect(status.initialized).toBe(true);
  });

  it('disabled components include mode: disabled for consistent shape', async () => {
    const f = await createFoundation('u1', FoundationMode.CRISIS_ONLY);
    const status = f.getSystemStatus() as { components: Record<string, { active: boolean; mode: string }> };
    expect(status.components.toi_otoi_framework.mode).toBe('disabled');
    expect(status.components.sleepwalker_protocol.mode).toBe('disabled');
  });
});

describe('NeuroLiftFoundation.processInteraction', () => {
  it('EMOTIONAL_ASSESSMENT returns emotionalState in content (CONTINUITY_ONLY mode)', async () => {
    const f = await createFoundation('u1', FoundationMode.CONTINUITY_ONLY);
    const response = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: 'I feel overwhelmed today' },
      userId: 'u1',
    });
    expect(response.success).toBe(true);
    expect(response.componentsInvolved).toContain('sleepwalker_protocol');
    expect(response.content).toHaveProperty('emotionalState');
  });

  it('PREFERENCE_UPDATE with invalid TOI throws in FRAMEWORK_ONLY mode', async () => {
    const f = await createFoundation('u1', FoundationMode.FRAMEWORK_ONLY);
    await expect(
      f.updatePreferences({ notAToi: true }),
    ).rejects.toThrow('TOI validation failed');
  });

  it('CRISIS_ALERT routes to rrt_advocate in CRISIS_ONLY mode', async () => {
    const f = await createFoundation('u1', FoundationMode.CRISIS_ONLY);
    const response = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.CRISIS_ALERT,
      data: { text: 'I need help now' },
      userId: 'u1',
    });
    expect(response.success).toBe(true);
    expect(response.componentsInvolved).toContain('rrt_advocate');
    expect(response.content).toHaveProperty('rrt');
  });

  it('unknown interaction type returns empty components array', async () => {
    const f = await createFoundation('u1', FoundationMode.UNIFIED);
    const response = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.STATUS_INQUIRY,
      data: {},
      userId: 'u1',
    });
    expect(response.success).toBe(true);
    expect(response.componentsInvolved).toHaveLength(0);
  });
});

describe('NeuroLiftFoundation.assessEmotionalState', () => {
  it('returns an assessment when sleepwalker is active', async () => {
    const f = await createFoundation('u1', FoundationMode.CONTINUITY_ONLY);
    const result = await f.assessEmotionalState('I am feeling overwhelmed');
    expect(result).not.toBeNull();
  });

  it('returns null when sleepwalker is not active', async () => {
    const f = await createFoundation('u1', FoundationMode.FRAMEWORK_ONLY);
    const result = await f.assessEmotionalState('I am feeling overwhelmed');
    expect(result).toBeNull();
  });
});

describe('NeuroLiftFoundation.updatePreferences', () => {
  it('resolves without error for a valid TOI document', async () => {
    const f = await createFoundation('u1', FoundationMode.FRAMEWORK_ONLY);
    await expect(
      f.updatePreferences({ $toi: '1.0.0', $tier: 'personal', identity: { author: 'test-user' } }),
    ).resolves.toBeUndefined();
  });
});

describe('NeuroLiftFoundation.shutdown', () => {
  it('marks the foundation as uninitialized', async () => {
    const f = await createFoundation('u1', FoundationMode.DEVELOPMENT);
    expect((f.getSystemStatus() as { initialized: boolean }).initialized).toBe(true);
    await f.shutdown();
    expect((f.getSystemStatus() as { initialized: boolean }).initialized).toBe(false);
  });
});

describe('pillar umbrella re-exports', () => {
  it('surfaces the four Solidarity Framework pillar packages', async () => {
    // @neurolift-technologies/toi
    const good = toi.safeParseToi({ $toi: '1.0.0', $tier: 'personal', identity: { author: 'u1' } });
    expect(good.success).toBe(true);
    expect(typeof toi.parseToi).toBe('function');

    // @neurolift-technologies/otoi
    expect(typeof otoi.honor).toBe('function');
    expect(typeof otoi.propagate).toBe('function');

    // @neurolift-technologies/rrt-advocate
    expect(typeof rrt.CrisisEngine).toBe('function');
    const assessment = await new rrt.CrisisEngine('u1').assess('just checking in, doing fine');
    expect(assessment).toHaveProperty('crisisLevel');

    // @neurolift-technologies/sleepwalker-protocol
    expect(typeof sleepwalker.SleepwalkerProtocol).toBe('function');
  });
});

// ============================================================================
// ASFDK provenance defense — channel classification (plan C1/C2, TDD cases)
// Decision-complete plan: .omo/plans/asfdk-provenance-defense.md (approved 2026-08-04)
// Locked semantics: D2 (optional channel, absent → unknown), D3 (closed enum),
// D4 (trust read only from top-level channel), D5 (gate-up predicate), D6
// (trusted := channel === 'user_input').
// ============================================================================
describe('ASFDK provenance defense — channel classification (C1/C2)', () => {
  // T1 — User channel unchanged crisis path: EMOTIONAL_ASSESSMENT + user_input →
  // channel recorded as user_input, trusted === true, componentsInvolved contains
  // sleepwalker_protocol (+ rrt_advocate when the handoff triggers). Existing
  // behavior preserved.
  it('T1: user_input channel preserves the unchanged crisis path', async () => {
    const f = await createFoundation('t1', FoundationMode.CONTINUITY_ONLY);
    const response = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: 'I feel overwhelmed today' },
      userId: 't1',
      channel: Channel.USER_INPUT,
    });
    expect(response.content.channel).toBe(Channel.USER_INPUT);
    expect(response.content.trusted).toBe(true);
    expect(response.componentsInvolved).toContain('sleepwalker_protocol');
    expect(response.content).toHaveProperty('emotionalState');

    // Same path with the RRT handoff triggered (requiresRrtaHandoff true).
    const f2 = await createFoundation('t1b', FoundationMode.UNIFIED);
    const handoff = await f2.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: 'I want to hurt myself' },
      userId: 't1b',
      channel: Channel.USER_INPUT,
    });
    expect(handoff.content.channel).toBe(Channel.USER_INPUT);
    expect(handoff.content.trusted).toBe(true);
    expect(handoff.componentsInvolved).toContain('sleepwalker_protocol');
    expect(handoff.componentsInvolved).toContain('rrt_advocate');
  });

  // T2 — Model channel recorded, still processed: EMOTIONAL_ASSESSMENT +
  // model_output → recorded model_output, trusted === false, components still
  // involved (no gating), provenance present.
  it('T2: model_output channel is recorded untrusted but still processed', async () => {
    const f = await createFoundation('t2', FoundationMode.CONTINUITY_ONLY);
    const response = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: 'I feel overwhelmed today' },
      userId: 't2',
      channel: Channel.MODEL_OUTPUT,
    });
    expect(response.content.channel).toBe(Channel.MODEL_OUTPUT);
    expect(response.content.trusted).toBe(false);
    expect(response.componentsInvolved).toContain('sleepwalker_protocol');
    expect(response.content).toHaveProperty('emotionalState');
  });

  // T3 — Absent channel → unknown/untrusted: no channel field on the interaction
  // (or on the assessEmotionalState call) → channel 'unknown', trusted false.
  it('T3: absent channel records unknown and untrusted', async () => {
    const f = await createFoundation('t3', FoundationMode.CONTINUITY_ONLY);
    const response = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: 'I feel overwhelmed today' },
      userId: 't3',
    });
    expect(response.content.channel).toBe(Channel.UNKNOWN);
    expect(response.content.trusted).toBe(false);

    // Same for assessEmotionalState without a channel.
    const assessment = (await f.assessEmotionalState('I feel overwhelmed today')) as Record<string, unknown>;
    expect(assessment).not.toBeNull();
    expect(assessment.channel).toBe(Channel.UNKNOWN);
    expect(assessment.trusted).toBe(false);
  });

  // T4 — Crisis types: CRISIS_ALERT / EMERGENCY_ESCALATION with model_output and
  // unknown channels → recorded untrusted, still assessed, provenance in content.
  it('T4: crisis types with untrusted channels are recorded untrusted but still assessed', async () => {
    const f = await createFoundation('t4', FoundationMode.CRISIS_ONLY);
    for (const channel of [Channel.MODEL_OUTPUT, Channel.UNKNOWN]) {
      const response = await f.processInteraction({
        timestamp: new Date(),
        interactionType: InteractionType.CRISIS_ALERT,
        data: { text: 'I need help now' },
        userId: 't4',
        channel,
      });
      expect(response.content.channel).toBe(channel);
      expect(response.content.trusted).toBe(false);
      expect(response.componentsInvolved).toContain('rrt_advocate');
      expect(response.content).toHaveProperty('rrt');
    }
    const emergency = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMERGENCY_ESCALATION,
      data: { text: 'I want to hurt myself' },
      userId: 't4',
      channel: Channel.MODEL_OUTPUT,
    });
    expect(emergency.content.channel).toBe(Channel.MODEL_OUTPUT);
    expect(emergency.content.trusted).toBe(false);
    expect(emergency.componentsInvolved).toContain('rrt_advocate');
    expect(emergency.content).toHaveProperty('rrt');
  });

  // T5 — Both sleepwalker entry points threaded: detectEmotionalState and
  // assessInteraction both receive (and record) the channel; absent → 'unknown'.
  it('T5: both sleepwalker entry points receive and record the channel', () => {
    const detected = sleepwalkerAdapter.detectEmotionalState(
      'I feel overwhelmed today',
      [],
      Channel.MODEL_OUTPUT,
    ) as unknown as Record<string, unknown>;
    expect(detected.channel).toBe(Channel.MODEL_OUTPUT);
    expect(detected.trusted).toBe(false);

    const assessed = sleepwalkerAdapter.assessInteraction(
      'I feel overwhelmed today',
      [],
      Channel.USER_INPUT,
    ) as unknown as Record<string, unknown>;
    expect(assessed.channel).toBe(Channel.USER_INPUT);
    expect(assessed.trusted).toBe(true);

    const absent = sleepwalkerAdapter.assessInteraction(
      'I feel overwhelmed today',
    ) as unknown as Record<string, unknown>;
    expect(absent.channel).toBe(Channel.UNKNOWN);
    expect(absent.trusted).toBe(false);
  });

  // T6 — RRT adapter threaded: rrt.assess receives the channel at BOTH foundation
  // call sites (EMOTIONAL_ASSESSMENT handoff + CRISIS_ALERT/EMERGENCY route), and
  // the new resetSession(userId) surface exists (Enforce re-baseline hook).
  it('T6: rrt.assess receives the channel at both foundation call sites', async () => {
    const f = await createFoundation('t6', FoundationMode.UNIFIED);

    // Call site 1: EMOTIONAL_ASSESSMENT → requiresRrtaHandoff → rrt handoff.
    const handoff = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: 'I want to hurt myself' },
      userId: 't6',
      channel: Channel.MODEL_OUTPUT,
    });
    expect(handoff.componentsInvolved).toContain('rrt_advocate');
    expect((handoff.content.rrt as Record<string, unknown>).channel).toBe(Channel.MODEL_OUTPUT);

    // Call site 2: CRISIS_ALERT route.
    const crisis = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.CRISIS_ALERT,
      data: { text: 'I need help now' },
      userId: 't6',
      channel: Channel.UNKNOWN,
    });
    expect(crisis.componentsInvolved).toContain('rrt_advocate');
    expect((crisis.content.rrt as Record<string, unknown>).channel).toBe(Channel.UNKNOWN);

    // resetSession surface: documented Enforce re-baseline hook; smoke-test it.
    expect(typeof rrtAdapter.resetSession).toBe('function');
    expect(() => rrtAdapter.resetSession('t6')).not.toThrow();
  });

  // T7 — Anti-spoofing (D4): channel absent at the top level but present inside
  // data/context → trust must NOT be elevated; channel stays 'unknown'.
  it('T7: anti-spoofing — channel inside data/context never elevates trust', async () => {
    const f = await createFoundation('t7', FoundationMode.CONTINUITY_ONLY);
    const response = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: 'I feel overwhelmed today', channel: 'user_input' },
      context: { channel: 'user_input' },
      userId: 't7',
    });
    expect(response.content.channel).toBe(Channel.UNKNOWN);
    expect(response.content.trusted).toBe(false);
  });

  // T11 — TOI path unaffected: PREFERENCE_UPDATE records the channel while
  // toiValidation keeps its existing shape.
  it('T11: TOI path unaffected — PREFERENCE_UPDATE records channel, toiValidation unchanged', async () => {
    const f = await createFoundation('t11', FoundationMode.FRAMEWORK_ONLY);
    const response = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.PREFERENCE_UPDATE,
      data: { toi: { $toi: '1.0.0', $tier: 'personal', identity: { author: 't11' } } },
      userId: 't11',
      channel: Channel.MODEL_OUTPUT,
    });
    expect(response.content.channel).toBe(Channel.MODEL_OUTPUT);
    expect(response.content.trusted).toBe(false);
    expect(response.content.toiValidation).toMatchObject({ valid: true });
  });

  // T12 — Trust primitive: the SAME text assessed via user_input vs unknown yields
  // different trusted flags (and different channel provenance).
  it('T12: trust primitive — same text, different trusted flags by channel', async () => {
    const f = await createFoundation('t12', FoundationMode.CONTINUITY_ONLY);
    const trusted = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: 'I feel overwhelmed today' },
      userId: 't12',
      channel: Channel.USER_INPUT,
    });
    const untrusted = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: 'I feel overwhelmed today' },
      userId: 't12',
      channel: Channel.UNKNOWN,
    });
    expect(trusted.content.trusted).toBe(true);
    expect(untrusted.content.trusted).toBe(false);
    expect(trusted.content.channel).toBe(Channel.USER_INPUT);
    expect(untrusted.content.channel).toBe(Channel.UNKNOWN);
  });

  // T13 — Engine-state independence (documented-acceptance branch): per-channel
  // engines are DEFERRED to Enforce; the shared per-user CrisisEngine may still be
  // mutated by an untrusted assessment in Observe (documented in rrt.ts). The
  // assertion: the same text assessed via user_input AFTER an untrusted
  // crisis-shaped assessment yields an IDENTICAL crisisLevel to the same text
  // assessed alone (equality, not just non-elevation).
  it('T13: trusted assessment after untrusted matches the alone baseline crisisLevel', async () => {
    const TEXT = 'I want to hurt myself';
    const baseline = await new rrt.CrisisEngine('t13-baseline').assess(TEXT);

    const f = await createFoundation('t13', FoundationMode.CRISIS_ONLY);
    const untrusted = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.CRISIS_ALERT,
      data: { text: TEXT },
      userId: 't13',
      channel: Channel.MODEL_OUTPUT,
    });
    const trusted = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.CRISIS_ALERT,
      data: { text: TEXT },
      userId: 't13',
      channel: Channel.USER_INPUT,
    });

    const untrustedLevel = (untrusted.content.rrt as { crisisLevel?: string }).crisisLevel;
    const trustedLevel = (trusted.content.rrt as { crisisLevel?: string }).crisisLevel;
    expect(untrustedLevel).toBe(baseline.crisisLevel);
    expect(trustedLevel).toBe(untrustedLevel);
  });

  // T14 — Runtime normalization (M3): any value not EXACTLY a closed-enum member —
  // casing, whitespace, unicode lookalikes, non-strings, nested objects — collapses
  // to 'unknown' and is never elevated to a trusted channel.
  it('T14: runtime normalization — malformed values collapse to unknown, never elevated', async () => {
    const f = await createFoundation('t14', FoundationMode.CONTINUITY_ONLY);
    const malformed: unknown[] = [
      'USER_INPUT',
      'user input',
      'tool_result ',
      'ｕｓｅｒ＿ｉｎｐｕｔ', // full-width unicode lookalike
      'user\u00A0input', // non-breaking space
      42,
      true,
      { channel: 'user_input' },
      null,
      undefined,
    ];
    for (const value of malformed) {
      const response = await f.processInteraction({
        timestamp: new Date(),
        interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
        data: { text: 'I feel overwhelmed today' },
        userId: 't14',
        channel: value as unknown as Channel,
      });
      expect(response.content.channel).toBe(Channel.UNKNOWN);
      expect(response.content.trusted).toBe(false);
    }

    // Direct normalizer unit assertions.
    expect(normalizeChannel(Channel.USER_INPUT)).toBe(Channel.USER_INPUT);
    expect(normalizeChannel(Channel.MODEL_OUTPUT)).toBe(Channel.MODEL_OUTPUT);
    expect(normalizeChannel(Channel.TOOL_RESULT)).toBe(Channel.TOOL_RESULT);
    expect(normalizeChannel(Channel.SYSTEM)).toBe(Channel.SYSTEM);
    expect(normalizeChannel(Channel.UNKNOWN)).toBe(Channel.UNKNOWN);
    expect(normalizeChannel('USER_INPUT')).toBe(Channel.UNKNOWN);
    expect(normalizeChannel(' user_input ')).toBe(Channel.UNKNOWN);
    expect(normalizeChannel('user\u00A0input')).toBe(Channel.UNKNOWN);
    expect(normalizeChannel('ｕｓｅｒ＿ｉｎｐｕｔ')).toBe(Channel.UNKNOWN);
    expect(normalizeChannel(undefined)).toBe(Channel.UNKNOWN);
    expect(normalizeChannel(null)).toBe(Channel.UNKNOWN);
    expect(normalizeChannel({ channel: 'user_input' })).toBe(Channel.UNKNOWN);
    expect(normalizeChannel(42)).toBe(Channel.UNKNOWN);
  });

  // T15 (foundation-level portion; the deploy-kit logging half is by-inspection) —
  // Gate-up (D5): untrusted channel + high-severity crisis signal → gateUp true;
  // user_input + the same signal → gateUp false. High-severity: EMERGENCY_ESCALATION
  // is always high; CRISIS_ALERT is high when RRT returns RED/BLACK (or, with RRT
  // inactive, the interaction type alone — fail-safe); the emotional path is high
  // when the sleepwalker state carries explicit crisis flags.
  it('T15 (foundation): gate-up — untrusted high-severity escalates, trusted never gates up', async () => {
    const f = await createFoundation('t15', FoundationMode.CRISIS_ONLY);

    // EMERGENCY_ESCALATION is always high-severity (D5) → untrusted gates up.
    const untrustedEmergency = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMERGENCY_ESCALATION,
      data: { text: 'I want to hurt myself' },
      userId: 't15',
      channel: Channel.MODEL_OUTPUT,
    });
    expect(untrustedEmergency.content.gateUp).toBe(true);

    // Same signal via user_input → trusted → never gates up.
    const trustedEmergency = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMERGENCY_ESCALATION,
      data: { text: 'I want to hurt myself' },
      userId: 't15',
      channel: Channel.USER_INPUT,
    });
    expect(trustedEmergency.content.gateUp).toBe(false);

    // CRISIS_ALERT with RRT active: RED/BLACK crisisLevel → high → gates up.
    const redAlert = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.CRISIS_ALERT,
      data: { text: 'I want to hurt myself' }, // empirical: crisisLevel 'emergency'
      userId: 't15',
      channel: Channel.UNKNOWN,
    });
    expect(redAlert.content.gateUp).toBe(true);

    // CRISIS_ALERT with RRT active but non-high severity → no gate-up.
    const greenAlert = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.CRISIS_ALERT,
      data: { text: 'I need help now' }, // empirical: crisisLevel 'stable'
      userId: 't15',
      channel: Channel.MODEL_OUTPUT,
    });
    expect(greenAlert.content.gateUp).toBe(false);

    // CRISIS_ALERT with RRT inactive → fall back to the interaction type alone
    // (fail-safe: never silently ignored).
    const f2 = await createFoundation('t15b', FoundationMode.CONTINUITY_ONLY);
    const fallback = await f2.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.CRISIS_ALERT,
      data: { text: 'I need help now' },
      userId: 't15b',
      channel: Channel.MODEL_OUTPUT,
    });
    expect(fallback.content.gateUp).toBe(true);

    // assessEmotionalState records channel/trusted/gateUp additively (no envelope).
    const f3 = await createFoundation('t15c', FoundationMode.CONTINUITY_ONLY);
    const emo = (await f3.assessEmotionalState(
      'I want to hurt myself',
      undefined,
      Channel.MODEL_OUTPUT,
    )) as Record<string, unknown>;
    expect(emo.channel).toBe(Channel.MODEL_OUTPUT);
    expect(emo.trusted).toBe(false);
    expect(emo.gateUp).toBe(true);

    const emoTrusted = (await f3.assessEmotionalState(
      'I want to hurt myself',
      undefined,
      Channel.USER_INPUT,
    )) as Record<string, unknown>;
    expect(emoTrusted.gateUp).toBe(false);

    const emoLow = (await f3.assessEmotionalState(
      'I feel overwhelmed today',
      undefined,
      Channel.MODEL_OUTPUT,
    )) as Record<string, unknown>;
    expect(emoLow.gateUp).toBe(false);
  });

  // T16 — Mode fail-loud: an unrecognized foundation mode yields an explicit
  // error, never silent all-components-off.
  it('T16: unrecognized mode fails loud — never silent all-off', async () => {
    await expect(
      createFoundation('t16', 'bogus_mode' as unknown as FoundationMode),
    ).rejects.toThrow(/unrecognized foundation mode/i);
  });

  // T18 — Malformed interactions: String(undefined) data, absent text, and
  // concurrent interactions on different channels on the same instance — no
  // cross-talk, no crash.
  it('T18: malformed interactions — no cross-talk, no crash', async () => {
    const f = await createFoundation('t18', FoundationMode.UNIFIED);

    // data.text = String(undefined) → 'undefined' string; must not crash.
    const a = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: { text: String(undefined) },
      userId: 't18',
      channel: Channel.MODEL_OUTPUT,
    });
    expect(a.success).toBe(true);
    expect(a.content.channel).toBe(Channel.MODEL_OUTPUT);

    // Absent text entirely.
    const b = await f.processInteraction({
      timestamp: new Date(),
      interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
      data: {},
      userId: 't18',
    });
    expect(b.success).toBe(true);
    expect(b.content.channel).toBe(Channel.UNKNOWN);

    // Concurrent interactions on different channels — channel provenance must not
    // cross-talk between responses (channel/trusted/gateUp are per-response).
    const [c1, c2, c3] = await Promise.all([
      f.processInteraction({
        timestamp: new Date(),
        interactionType: InteractionType.EMOTIONAL_ASSESSMENT,
        data: { text: 'I feel overwhelmed today' },
        userId: 't18',
        channel: Channel.USER_INPUT,
      }),
      f.processInteraction({
        timestamp: new Date(),
        interactionType: InteractionType.CRISIS_ALERT,
        data: { text: 'I need help now' },
        userId: 't18',
        channel: Channel.MODEL_OUTPUT,
      }),
      f.processInteraction({
        timestamp: new Date(),
        interactionType: InteractionType.EMERGENCY_ESCALATION,
        data: { text: 'I want to hurt myself' },
        userId: 't18',
        channel: Channel.UNKNOWN,
      }),
    ]);

    expect(c1.content.channel).toBe(Channel.USER_INPUT);
    expect(c1.content.trusted).toBe(true);
    expect(c1.content.gateUp).toBe(false); // trusted channel never gates up

    expect(c2.content.channel).toBe(Channel.MODEL_OUTPUT);
    expect(c2.content.trusted).toBe(false);

    expect(c3.content.channel).toBe(Channel.UNKNOWN);
    expect(c3.content.trusted).toBe(false);
    expect(c3.content.gateUp).toBe(true); // EMERGENCY_ESCALATION always high + untrusted
  });
});
