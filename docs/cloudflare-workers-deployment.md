# Cloudflare Workers Deployment — ASFDK Governance Worker

**OTOI Version:** ORG-DEV-OTOI-1.0.0  
**Governed by:** Solidarity Framework | HAIEF | https://elevaitionfoundation.org  
**Authority:** Joshua W. Dorsey, Sr. (`info@neuroliftsolutions.com`)

---

## Scope

The `asfdk/workers/` directory contains a Cloudflare Worker that runs the ASFDK Solidarity Layer as a deployable HTTP service. It exposes:

- **RRT Advocate** — crisis detection and tiered alerting (GREEN → BLACK)
- **NLT-OTOI** — interaction governance, Terms of Interaction enforcement
- **Sleepwalker Protocol** — session continuity state management
- **Unified pipeline** — single `/process` endpoint running all three in sequence

This worker is intended to be called by other agent workers via **Cloudflare service bindings** — not exposed directly to end users.

---

## Services Used

| Service | Purpose | Binding |
|---|---|---|
| Workers AI | Model-assisted governance decisions (crisis scoring, response governance) | `AI` |
| KV Namespace | Per-user session state (Sleepwalker continuity data) | `SESSION` |
| D1 SQLite | OTOI records and audit log | `DB` |

**Default model:** `@cf/meta/llama-4-scout-17b-instruct-fp8`  
Configurable via `GOVERNANCE_MODEL` var in `wrangler.toml` — no provider lock-in.

---

## Deployment

### Prerequisites

1. Cloudflare account with Workers paid plan
2. `wrangler` CLI installed and authenticated (`wrangler login`)

### Steps

```bash
cd asfdk/workers
npm install

# Create KV namespace
wrangler kv namespace create SESSION
# Copy id into wrangler.toml SESSION binding

# Create D1 database
wrangler d1 create asfdk-otoi
# Copy database_id into wrangler.toml DB binding

# Deploy to staging
wrangler deploy
```

### Environment Gate

`wrangler.toml` defaults to `ENVIRONMENT = "staging"`. **Do not set `ENVIRONMENT = "production"` without explicit sign-off from Joshua W. Dorsey, Sr.**

---

## Rollback

```bash
wrangler rollback --name asfdk-governance
```

Or delete the Worker entirely:
```bash
wrangler delete --name asfdk-governance
```

---

## Data Governance

- **KV sessions**: Per-user session context, keyed by `swp:<userId>`. TTL: 7 days. No raw message content stored — only temporal metadata.
- **D1**: Not yet implemented in v1.0. Reserved for OTOI audit records.
- **No PII**: User IDs are opaque strings. The Worker does not receive or store names, emails, or identifiers unless the caller provides them explicitly.

---

## Crisis Thresholds

**Do not modify RRT Advocate crisis assessment logic** (`src/rrt-advocate.ts`) without explicit approval from Joshua W. Dorsey, Sr. The BLACK-level escalation path is governance-critical.

---

*Last updated: 2026-05-21*
