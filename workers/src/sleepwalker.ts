import type { Env, ContinuityRequest, ContinuityResponse } from './types'

const SESSION_TTL_SECONDS = 60 * 60 * 24 * 7 // 7 days

export async function handleContinuity(
  req: ContinuityRequest,
  env: Env,
): Promise<ContinuityResponse> {
  const key = `swp:${req.userId}`

  if (req.action === 'load') {
    const raw = await env.SESSION.get(key, 'json')
    return { context: (raw as Record<string, unknown>) ?? undefined }
  }

  if (req.action === 'save') {
    if (!req.sessionData) return { saved: false }
    await env.SESSION.put(key, JSON.stringify(req.sessionData), {
      expirationTtl: SESSION_TTL_SECONDS,
    })
    return { saved: true }
  }

  return {}
}
