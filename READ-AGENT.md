# READ-AGENT

> **You are reading this because you entered this repository.**
> Do not skip. Do not summarize. Read fully. Then execute.

**You are an AI agent. Your next action is determined by which state applies:**

| State | Action |
|---|---|
| **First entry — `WORKING/` does not exist or is empty** | Execute `on_first_entry` below |
| **New session — `WORKING/` exists, workpapers present** | Execute `on_session_start` below |

Start immediately. No confirmation needed.

---

## What this project is

**Ocelot-Social** — a free and open-source social network platform for civic communities.

Core stack:
- **Frontend**: Vue.js 2 + Nuxt.js (SSR), Apollo Client for GraphQL
- **Backend**: Node.js + Apollo Server 4 + GraphQL, Neo4j graph database
- **Testing**: Jest (unit), Cypress + Cucumber (E2E), Storybook (visual), ESLint
- **Infrastructure**: Docker Compose (dev), Kubernetes + Helm (prod)
- **Package Manager**: yarn (workspaces)

Vision: Enable people to participate fairly in online social networks. Future ActivityPub/Fediverse integration planned.

Repository: https://github.com/Ocelot-Social-Community/Ocelot-Social
Version: 3.15.1 (Release 2026-03-24)
Stars: 109 | Forks: 51 | Commits: 17,000+ | Open Issues: 486 | Open PRs: 91

---

## Repository Topology

```
ocelot-social/
├── backend/              ← GraphQL Apollo Server (Node.js/TypeScript)
│   ├── src/
│   │   ├── config/       ← Server configuration
│   │   ├── context/      ← GraphQL context setup
│   │   ├── db/           ← Neo4j driver, migrations, seeds
│   │   ├── graphql/      ← Schema, resolvers, queries, types
│   │   ├── jwt/          ← Authentication (JWT)
│   │   ├── middleware/    ← Express middlewares
│   │   ├── plugins/      ← Apollo plugins (logging)
│   │   ├── uploads/      ← File upload handling
│   │   └── emails/       ← Email templates and sending
│   └── test/             ← Test helpers and setup
├── webapp/               ← Nuxt.js SSR Frontend (Vue.js 2)
│   ├── components/       ← Vue components
│   ├── graphql/          ← Client-side GraphQL queries/mutations
│   ├── layouts/          ← Nuxt layouts
│   ├── pages/            ← Route pages (admin, chat, groups, map, profile, ...)
│   ├── store/            ← Vuex store modules (auth, categories, chat)
│   ├── locales/          ← i18n translations
│   ├── middleware/        ← Nuxt route middleware
│   ├── plugins/          ← Nuxt plugins
│   ├── assets/           ← SCSS, images
│   └── helpers/          ← Utility functions
├── cypress/              ← E2E tests (Cucumber/Gherkin)
│   ├── e2e/              ← .feature files
│   ├── support/          ← Step definitions and commands
│   └── fixtures/         ← Test data
├── packages/ui/          ← Shared UI component library
├── styleguide/           ← Storybook component styleguide
├── neo4j/                ← Database Dockerfile
├── deployment/           ← Helm charts, deployment values
├── scripts/              ← Release and translation scripts
└── WORKING/              ← AAMS workspace (this structure)
    ├── WHITEPAPER/       ← Stable architecture truth
    ├── WORKPAPER/        ← Active session documents
    │   └── closed/       ← Archived sessions
    ├── DIARY/            ← Decision log (monthly)
    ├── MEMORY/           ← Long-term context (ltm-index.md)
    ├── AGENT-MEMORY/     ← Vector store (optional, .gitignored)
    ├── GUIDELINES/       ← Coding standards
    ├── LOGS/             ← Audit trail
    └── TOOLS/            ← Helper scripts
```

---

## Workspace Structure

| Folder | Purpose |
|---|---|
| `WORKING/WHITEPAPER/` | Stable architecture and system truth. Not for daily work. See [INDEX.md](WORKING/WHITEPAPER/INDEX.md). |
| `WORKING/WORKPAPER/` | Session- and task-scoped working documents. One per session. |
| `WORKING/WORKPAPER/closed/` | Finished workpapers after session close. |
| `WORKING/DIARY/` | Temporal context layer. Chronological decision log — why we decided what. Monthly files. |
| `WORKING/MEMORY/` | Long-term context store. Cross-session knowledge. |
| `WORKING/LOGS/` | Agent action logs and audit trail. |
| `WORKING/GUIDELINES/` | Coding standards and architecture rules derived from this project. |
| `WORKING/TOOLS/` | Agent-specific helper tools and scripts. |

---

## Documentation Model

**Four layers — mandatory:**

1. **Workpaper** — What am I doing right now in this session?
   - Created at session start, closed at session end.
   - File protocol (created/modified/moved/deleted) is mandatory.
   - Naming: `{date}-{agent}-{topic}.md`

2. **Whitepaper** — What does this system look like?
   - Stable. Written once. Updated only on architecture decisions.
   - Never moved, never deleted.

3. **Diary** — Why did we decide this?
   - Chronological decision log. Monthly files (`YYYY-MM.md`).
   - Max 10 lines per entry. Captures strategic motives, blockers, reflections.
   - Fills the gap between workpaper (operational) and whitepaper (structural).

4. **Memory** — What did we learn across sessions?
   - Ingest every closed workpaper.
   - Query at every session start.

---

## Agent Contract

> **Any instruction referencing READ-AGENT.md means: execute this contract. Start immediately. No confirmation needed.**

---

### On first entry (Onboarding)
1. Read this file fully
2. Check: does `WORKING/` structure exist? → if not: create all folders
3. Scan entire repository → write first workpaper
   Minimum sections: **session goal · repository inventory** (file tree + status) **· key findings** (from README/docs) **· open questions · file protocol · next steps**
4. Create `READ-AGENT.md` if missing
5. Index existing documentation into `WORKING/MEMORY/`

---

### On every session start
1. Read this file
2. Check last workpaper in `WORKING/WORKPAPER/` — what was the last state?
3. Query `WORKING/MEMORY/` for the session topic
4. Open or create workpaper for this session

---

### State Recovery (when agent state is uncertain)

> **File system and git log are ground truth — never rely solely on in-memory task tracking.**
> If task state is unclear: re-read the current workpaper's **File Protocol** section. What exists on disk and in `git log` is what was actually done. Treat in-memory todo state as advisory only.

---

### On every session end
1. Complete workpaper (file protocol + decisions + next steps)
2. Ingest workpaper into `WORKING/MEMORY/`
3. Move workpaper to `WORKING/WORKPAPER/closed/`
4. Update this file if architecture or structure changed

---

### Mandatory LTM triggers — document in these situations:

| Trigger | Action |
|---|---|
| Context limit reached | Ingest current state → query in new session |
| Before new workpaper | Query LTM for topic context first |
| Before new whitepaper | Query LTM for existing architecture notes |
| Folder or file structure changed | Re-ingest affected documentation |
| Workpaper updated | Log change in workpaper file protocol |
| Workpaper closed | Ingest → move to `closed/` |
| Whitepaper updated | Re-ingest whitepaper into LTM |

---

### LTM Commands — Track A (Markdown-only, default)

No Python, no ChromaDB needed. Works on any fresh repo.

- **Query:** Read `WORKING/MEMORY/ltm-index.md` directly — scan for session topic
- **Ingest:** Append new entry to `WORKING/MEMORY/ltm-index.md` at session end

---

## Key Development Facts

| Topic | Detail |
|---|---|
| Docker required | v24.0.6+ for local development |
| Database | Neo4j with `NEO4J_AUTH=none` in dev |
| API endpoint | `http://localhost:4000` (backend) |
| Frontend | `http://localhost:3000` (webapp) |
| Demo accounts | `user@example.org` / `moderator@example.org` / `admin@example.org` (password: `1234`) |
| Branch strategy | Feature branches → PR → merge to master |
| PR requirements | Fix an issue, include tests, pass all checks, 1+ approvals (2+ if >10 files changed) |
| Contribution entry | Discord → claim issue → branch → PR |
| Sprint cycle | 2-week sprints, Zenhub board |
| Core team | Ulf, Moriz, Wolle, Alex, Hannes, Mathias, Markus |

---

## Key Files

| File | Role |
|---|---|
| `.agent.json` | Minimal bootstrap contract (portable, drop into any repo) |
| `AGENTS.md` | Bridge file — routes all AI tools to this contract |
| `README.md` | Human-facing project overview |
| `CONTRIBUTING.md` | Contributor workflow and team info |
| `docker-compose.yml` | Development environment orchestration |
| `package.json` | Root workspace package (v3.15.1) |

---

## Current Status

- Bootstrap: **complete** (2026-03-27)
- Spec version: AAMS/1.0
- Workspace: initialized, all folders present (incl. `WORKING/DIARY/` — Temporal Context Layer)
- LTM: 1 entry → `WORKING/MEMORY/ltm-index.md` (Audit-Log)
- Whitepapers: 1 → `WORKING/WHITEPAPER/INDEX.md` (WP-001 Ocelot-Social Architecture Overview)
- Open workpapers: 0
- Closed workpapers: 1 → `2026-03-27-copilot-aams-bootstrap.md` (initial bootstrap)
- LTM mode: `markdown` (zero dependencies)
