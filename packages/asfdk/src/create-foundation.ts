import { FoundationConfig, FoundationMode } from './types.js';
import { NeuroLiftFoundation } from './foundation.js';

/**
 * Constructs and initializes a {@link NeuroLiftFoundation} instance.
 *
 * Two call signatures are supported:
 * - `createFoundation(userId, mode?)` — shorthand; `mode` defaults to `UNIFIED`.
 * - `createFoundation(config)` — full config object.
 */
export async function createFoundation(userId: string, mode?: FoundationMode): Promise<NeuroLiftFoundation>;
export async function createFoundation(config: FoundationConfig): Promise<NeuroLiftFoundation>;
export async function createFoundation(
  userIdOrConfig: string | FoundationConfig,
  mode: FoundationMode = FoundationMode.UNIFIED,
): Promise<NeuroLiftFoundation> {
  const config: FoundationConfig =
    typeof userIdOrConfig === 'string'
      ? { userId: userIdOrConfig, mode }
      : userIdOrConfig;

  const foundation = new NeuroLiftFoundation(config);
  await foundation.initialize();
  return foundation;
}
