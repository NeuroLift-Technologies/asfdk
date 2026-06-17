import { describe, it, expect } from 'vitest';
import {
  createFoundation,
  FoundationMode,
  InteractionType,
  NeuroLiftFoundation,
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

  it('rrt_advocate is always a stub', async () => {
    const f = await createFoundation('u1', FoundationMode.UNIFIED);
    const result = await f.healthCheck();
    expect(result.components.rrt_advocate.active).toBe(false);
    expect(result.components.rrt_advocate.mode).toBe('stub-python-only');
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
