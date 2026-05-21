import { Hono } from 'hono'
import { assessCrisis } from './rrt-advocate'
import { governInteraction } from './nlt-otoi'
import { handleContinuity } from './sleepwalker'
import type { Env } from './types'

const app = new Hono<{ Bindings: Env }>()

app.get('/health', (c) =>
  c.json({ status: 'ok', version: c.env.ASFDK_VERSION, ts: Date.now() }),
)

app.post('/assess', async (c) => {
  const body = await c.req.json()
  const result = await assessCrisis(body, c.env)
  return c.json(result)
})

app.post('/govern', async (c) => {
  const body = await c.req.json()
  const result = await governInteraction(body, c.env)
  return c.json(result)
})

app.post('/continuity', async (c) => {
  const body = await c.req.json()
  const result = await handleContinuity(body, c.env)
  return c.json(result)
})

// Unified pipeline: assess → govern → save continuity
app.post('/process', async (c) => {
  const body = await c.req.json().catch(() => ({})) as Record<string, string>
  const { userId, message, agentResponse } = body

  if (!userId || !message || !agentResponse) {
    return c.json({ error: 'Missing required fields: userId, message, agentResponse' }, 400)
  }

  const assessment = await assessCrisis({ userId, message }, c.env)

  if (assessment.level === 'BLACK') {
    return c.json({
      assessment,
      governed: { governedResponse: agentResponse, flags: [], modified: false },
      finalResponse: assessment.intervention ?? 'Crisis intervention required.',
    })
  }

  const governed = await governInteraction({ userId, message, agentResponse }, c.env)

  await handleContinuity(
    {
      userId,
      action: 'save',
      sessionData: { lastMessage: message, lastLevel: assessment.level, ts: Date.now() },
    },
    c.env,
  )

  return c.json({
    assessment,
    governed,
    finalResponse: governed.governedResponse,
  })
})

export default app
