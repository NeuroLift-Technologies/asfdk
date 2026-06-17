import { describe, it, expect } from 'vitest';
import { createFoundation, FoundationMode, NeuroLiftFoundation } from '../src/index.js';

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
});
