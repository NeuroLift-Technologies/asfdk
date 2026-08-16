/**
 * TOI bootstrap: the generator runs before any component activates.
 */
import { describe, it, expect } from 'vitest';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { createFoundation, FoundationConfig, FoundationMode, NeuroLiftFoundation } from '../src/index.js';

describe('TOI bootstrap', () => {
  it('generates a personal TOI from defaults when no source is given', async () => {
    const f = await createFoundation('user-1', FoundationMode.UNIFIED);
    const doc = f.getActiveToi();
    expect(doc).not.toBeNull();
    expect(doc?.$tier).toBe('personal');
    expect(doc?.$toi).toBe('1.0.0');
    expect(doc?.identity.author).toBe('anonymous');
    expect(f.getSystemStatus().toi).toMatchObject({ generated: true });
  });

  it('merges a partial preferences source over defaults', async () => {
    const config: FoundationConfig = {
      userId: 'u2',
      mode: FoundationMode.UNIFIED,
      toi: { communication: { tone: 'friendly' } },
    };
    const f = await createFoundation(config);
    const doc = f.getActiveToi();
    expect(doc?.communication?.tone).toBe('friendly');
    // Untouched defaults survive the merge.
    expect(doc?.privacy?.retention).toBe('session-only');
  });

  it('parses and regenerates a file source', async () => {
    const dir = mkdtempSync(join(tmpdir(), 'asfdk-toi-'));
    try {
      const path = join(dir, 'team.toi');
      writeFileSync(
        path,
        JSON.stringify({ $toi: '1.0.0', $tier: 'project', identity: { author: 'carol' } }),
        'utf8',
      );
      const f = await createFoundation({
        userId: 'u3',
        mode: FoundationMode.UNIFIED,
        toi: path,
      });
      const doc = f.getActiveToi();
      expect(doc?.$tier).toBe('project');
      expect(doc?.identity.author).toBe('carol');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it('rejects an invalid source before activation (fail-loud)', async () => {
    const f = new NeuroLiftFoundation({
      userId: 'u4',
      mode: FoundationMode.UNIFIED,
      toi: { communication: { tone: 'gibberish' } },
    });
    await expect(f.initialize()).rejects.toThrow();
    expect(f.getActiveToi()).toBeNull();
    expect(f.getSystemStatus().initialized).toBe(false);
  });
});