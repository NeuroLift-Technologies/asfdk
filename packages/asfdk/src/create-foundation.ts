import { FoundationConfig, FoundationMode } from './types.js';
import { NeuroLiftFoundation } from './foundation.js';

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
