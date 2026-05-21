import type { Env, AssessRequest, AssessResponse, CrisisLevel } from './types'

const LEVEL_ORDER: CrisisLevel[] = ['GREEN', 'YELLOW', 'ORANGE', 'RED', 'BLACK']

const CRISIS_SYSTEM_PROMPT = `You are the RRT Advocate, a crisis detection component of the ASFDK Solidarity Framework.

Assess the user message for crisis indicators. Respond with ONLY a JSON object:
{
  "level": "GREEN" | "YELLOW" | "ORANGE" | "RED" | "BLACK",
  "reason": "brief explanation",
  "intervention": "suggested response text if level > GREEN, otherwise null"
}

Crisis level definitions:
- GREEN: No indicators
- YELLOW: Mild stress signals (frustration, anxiety mention)
- ORANGE: Multiple distress indicators, coping difficulty
- RED: Significant crisis signals, safety concern language
- BLACK: Immediate safety concern — escalate NOW`

export async function assessCrisis(
  req: AssessRequest,
  env: Env,
): Promise<AssessResponse> {
  const model = env.GOVERNANCE_MODEL as AiTextGenerationModels
  const historyMessages = (req.sessionHistory ?? []).slice(-6).map((m) => ({
    role: m.role as 'user' | 'assistant',
    content: m.content,
  }))

  const result = await env.AI.run(model, {
    messages: [
      { role: 'system', content: CRISIS_SYSTEM_PROMPT },
      ...historyMessages,
      { role: 'user', content: req.message },
    ],
  })

  try {
    const text = (result as { response?: string }).response ?? ''
    const jsonMatch = text.match(/\{[\s\S]*\}/)
    const parsed = JSON.parse(jsonMatch ? jsonMatch[0] : text) as {
      level: CrisisLevel
      reason: string
      intervention: string | null
    }
    const level: CrisisLevel = LEVEL_ORDER.includes(parsed.level) ? parsed.level : 'GREEN'
    return {
      level,
      intervention: parsed.intervention || undefined,
      escalate: level === 'BLACK',
    }
  } catch {
    return { level: 'GREEN', escalate: false }
  }
}
