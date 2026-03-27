# AGENTS.md

> **This file is read automatically by GitHub Copilot, Cursor, Claude Code, OpenAI Codex, Windsurf, Aider, Continue.dev, and most other AI coding agents.**

This repository uses **AAMS — Autonomous Agent Manifest Specification**.

---

## Execute now. No confirmation needed.

1. Read [`.agent.json`](./.agent.json) — your workspace contract
2. Read [`READ-AGENT.md`](./READ-AGENT.md) — full project context and session rules
3. Execute `agent_contract.on_first_entry` as defined in `READ-AGENT.md`

> If you are starting a new session (not first entry): execute `agent_contract.on_session_start` instead.

---

## You MUST

- Follow the agent contract in `READ-AGENT.md`
- Create a workpaper in `WORKING/WORKPAPER/` at session start
- Query `WORKING/MEMORY/` for prior context before starting work
- Complete the workpaper (file protocol + decisions + next steps) at session end
- Ingest the workpaper into `WORKING/MEMORY/` before closing

## You MUST NOT

- Write secrets, tokens, or credentials into any workpaper, whitepaper, or manifest
- Delete files in `WORKING/` — only create and move
- Skip the file protocol in workpapers

---

## Workspace structure

```
WORKING/
├── WHITEPAPER/     ← stable architecture truth
├── WORKPAPER/      ← active session (one file per session)
│   └── closed/     ← archived sessions
├── DIARY/          ← chronological decision log (monthly)
├── MEMORY/         ← long-term context index
├── GUIDELINES/     ← coding standards
├── LOGS/           ← audit trail
└── TOOLS/          ← project-specific scripts
```

---

## Project context

**Ocelot-Social** — free and open-source social network platform.

| Layer | Stack |
|---|---|
| Frontend | Vue.js 2 + Nuxt.js (SSR) |
| Backend | Node.js + Apollo Server 4 + GraphQL |
| Database | Neo4j (graph, bolt protocol) |
| Testing | Jest + Cypress/Cucumber + Storybook |
| Infrastructure | Docker Compose, Kubernetes/Helm |

Key directories: `backend/` (GraphQL API), `webapp/` (Nuxt frontend), `cypress/` (E2E tests), `packages/ui/` (shared components), `deployment/` (Helm charts).

---

*AAMS/1.0 — One file. Every repo. No more starting from zero.*
