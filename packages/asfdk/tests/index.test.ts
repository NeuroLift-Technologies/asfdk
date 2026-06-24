import { describe, it, expect } from 'vitest';
import {
  createFoundation,
  FoundationMode,
  InteractionType,
  NeuroLiftFoundation,
  toi,
  otoi,
  rrt,
  sleepwalker,
} from '../src/index.js';

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
