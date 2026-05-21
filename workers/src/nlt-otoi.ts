import type { Env, GovernRequest, GovernResponse } from './types'

const GOVERNANCE_SYSTEM_PROMPT = `You are the NLT-OTOI component of the ASFDK Solidarity Framework.

Your role is to ensure agent responses comply with the user's Terms of Interaction (TOI).
Review the agent response and apply governance rules:
- Privacy: no data leakage, no storing sensitive info without consent
- Tone: match the user's declared preferences (default: professional, clear)
- Boundaries: respect any user-declared topic restrictions
- Transparency: flag if the response is evasive or unclear

Respond with ONLY a JSON object:
{
  "governedResponse": "the (potentially modified) response text",
  "flags": ["list of governance flags triggered, empty array if none"],
  "modified": true | false
}`

export async function governInteraction(
  req: GovernRequest,
  env: Env,
): Promise<GovernResponse> {
  const model = env.GOVERNANCE_MODEL as AiTextGenerationModels
  const toiContext = req.toi
    ? `\nUser TOI preferences: ${JSON.stringify(req.toi)}`
    : ''

  const result = await env.AI.run(model, {
    messages: [
      { role: 'system', content: GOVERNANCE_SYSTEM_PROMPT + toiContext },
      {
        role: 'user',
        content: `User message: ${req.message}\n\nAgent response to govern: ${req.agentResponse}`,
      },
    ],
  })

  try {
    const text = (result as { response?: string }).response ?? ''
    const parsed = JSON.parse(text) as GovernResponse
    return {
      governedResponse: parsed.governedResponse ?? req.agentResponse,
      flags: Array.isArray(parsed.flags) ? parsed.flags : [],
      modified: parsed.modified ?? false,
    }
  } catch {
    return { governedResponse: req.agentResponse, flags: [], modified: false }
  }
}
