# GitHub Copilot Instructions for NeuroLift Technologies

These instructions guide GitHub Copilot when working on any repository in the NeuroLift Technologies organization.

---

## ⚠️ GOVERNANCE PROTOCOL — MANDATORY (ORG-DEV-OTOI-1.0.2)

**Before writing any code or making any file change**, you must complete the following session start protocol. This is non-negotiable for all agents (including GitHub Copilot) in every NLT repository.

### Session Start Protocol (OTOI §4.1)

Complete these steps **in order** before beginning substantive work:

1. **Read `NLT-DEV-OTOI.md`** in `NeuroLift-Technologies/asfdk` — the canonical org-level agent governance contract. Focus on §4 (agent behavior), §4.3 (escalation triggers), §4.4 (guardrails), §5 (handoff), and §8 (ethical commitments).
2. **Read `AGENTS.md`** in the repository you are working in — the internal coordination gateway defining guardrails, commit format, and multi-agent rules.
3. **Read `CLAUDE.md`** in the repository you are working in — repo-specific scope, conventions, and in-scope/out-of-scope rules.
4. **Read `docs/active-threads.md`** — check for in-progress work that may conflict with your task.
5. **Self-register** using `templates/agent-registration.json` and commit to `docs/agent-log/registrations/{YYYY-MM-DD}-copilot-{session-id}.json` as your **first commit**.

### Mandatory Commit Format

Every commit you make **must** follow this exact format:

```
[COPILOT] type(scope): description
```

Valid types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`

Examples:
```
[COPILOT] feat(auth): add OAuth2 login flow
[COPILOT] fix(api): resolve null pointer in user endpoint
[COPILOT] chore(governance): register agent session {session-id}
```

> Commits that do not follow this format will fail the `agent-commit-format` CI check.

### Non-Negotiable Guardrails (OTOI §4.4)

- **No LLM provider lock-in** — do not hardcode or commit to a specific LLM provider without Joshua W. Dorsey, Sr. approval
- **No architecture decisions** — database, deployment, framework choices require human sign-off
- **No production deployments** — human must explicitly approve all production actions
- **No credential storage** — never store secrets, tokens, or credentials in code or version control
- **No external integrations** — third-party service connections require Joshua's approval
- **No OTOI amendments** — never modify `NLT-DEV-OTOI.md` or core governance files; file a governance proposal instead

### Escalation Triggers (OTOI §4.3)

Stop work and escalate to **Joshua W. Dorsey, Sr.** (`info@neuroliftsolutions.com`) immediately if:
- Task scope is unclear or conflicts with an active thread
- An architectural or deployment decision is required
- A blocker cannot be resolved
- An ethical concern arises
- An LLM provider or external service selection is needed
- A governance document amendment is proposed

Use `templates/escalation.md` or file a GitHub issue with the `agent-escalation` template.

### Session End — Handoff Record (OTOI §5)

Every session must end with a handoff record committed to `docs/agent-log/handoffs/{YYYY-MM-DD}-{session-id}.json` using `templates/handoff-record.json`. No session ends without a handoff record.

---

## Project Context

NeuroLift Technologies builds AI-powered tools and platforms focused on cognitive enhancement and developer productivity. Our projects include:
- Python-based machine learning libraries
- Web applications (TypeScript/React frontend, Python/Node.js backend)
- Developer tooling and CLI utilities

## Coding Standards

- **Python**: Follow PEP 8; use type hints; prefer `dataclasses` or `pydantic` models for structured data.
- **TypeScript/JavaScript**: Use strict TypeScript types; prefer functional patterns; use `const` over `let` where possible.
- **Tests**: Write tests for all new functionality. Use `pytest` for Python and `vitest` or `jest` for TypeScript.
- **Documentation**: Write clear docstrings (Google-style for Python, JSDoc for TypeScript/JavaScript).
- **Security**: Never hardcode secrets. Use environment variables for credentials and sensitive configuration.

## Conventions

- Keep functions small and focused on a single responsibility.
- Prefer explicit error handling over silent failures.
- Use descriptive variable and function names; avoid single-letter names outside of loop indices.
- Commit messages should use the imperative mood (e.g., "Add user authentication" not "Added user authentication").

## Pull Requests

- Reference the related issue number in the PR description.
- Keep PRs small and focused — one feature or fix per PR.
- Always fill in the PR template fully.
