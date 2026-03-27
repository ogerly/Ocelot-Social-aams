# Workpaper — 2026-03-27 — Copilot — AAMS Bootstrap

**Session**: 001
**Date**: 2026-03-27
**Agent**: GitHub Copilot (Claude Opus 4.6)
**Status**: CLOSED

---

## Session Goal

Execute the AAMS `on_first_entry` contract for the Ocelot-Social repository. Create the full workspace structure, scan the repository, document architecture in a whitepaper, and initialize long-term memory. This is the foundational session — every future session inherits from this.

---

## Repository Inventory

**Project**: Ocelot-Social v3.15.1
**Repository**: https://github.com/Ocelot-Social-Community/Ocelot-Social
**Stats**: 109 stars, 51 forks, 17,000+ commits, 486 open issues, 91 open PRs

### Top-level structure
| Path | Type | Description |
|---|---|---|
| `backend/` | TypeScript/Node.js | GraphQL Apollo Server 4 + Neo4j |
| `webapp/` | JavaScript/Vue.js 2 | Nuxt.js SSR frontend |
| `cypress/` | JavaScript | E2E tests (Cucumber/Gherkin) |
| `packages/ui/` | Vue.js | Shared UI component library |
| `styleguide/` | Vue.js | Storybook component docs |
| `neo4j/` | Dockerfile | Database configuration |
| `deployment/` | Helm/YAML | Kubernetes deployment |
| `scripts/` | Shell | Release and translation automation |
| `docker-compose.yml` | YAML | Dev environment orchestration |

### Backend key paths
- `backend/src/graphql/` — Schema, resolvers, queries, types
- `backend/src/db/` — Neo4j driver, migrations, seeds
- `backend/src/jwt/` — JWT authentication
- `backend/src/config/` — Server configuration
- `backend/src/middleware/` — Express middlewares
- `backend/src/uploads/` — File upload handling
- `backend/src/emails/` — Email templates

### Webapp key paths
- `webapp/pages/` — Route pages (admin, chat, groups, login, map, profile, search, settings)
- `webapp/components/` — Vue components
- `webapp/store/` — Vuex modules (auth, categories, chat)
- `webapp/graphql/` — Client-side GraphQL operations
- `webapp/locales/` — i18n translations
- `webapp/layouts/` — Nuxt layouts
- `webapp/middleware/` — Route middleware

### Cypress E2E tests
- Feature files: Admin.DonationInfo, Admin.PinPost, Admin.TagOverview, Chat.Notification, Group.Create, and more
- Cucumber/Gherkin format with step definitions in `cypress/support/`

---

## Key Findings

1. **Stack**: Vue.js 2 + Nuxt.js (SSR) → GraphQL/Apollo Server 4 → Neo4j graph database
2. **Docker-first**: Full stack runs via `docker compose up` — webapp (3000), backend (4000), neo4j (7687)
3. **Auth**: JWT-based, roles: user/moderator/admin
4. **Contribution process**: Discord → claim issue → branch → PR → 1+ review → merge
5. **Active project**: Release 3.15.1 from 2026-03-24, regular sprints, core team of 7
6. **Testing pyramid**: Jest (unit) + Cypress/Cucumber (E2E) + Storybook (visual) + ESLint (lint)
7. **Deployment**: Kubernetes/Helm, staging at stage.ocelot.social, release-please automation
8. **Branding system**: `backend/branding/` and `webapp/branding/` allow white-label customization
9. **No existing agent structure**: No `.agent.json`, `AGENTS.md`, or equivalent files existed
10. **Package manager**: yarn (workspace-based monorepo)

---

## Open Questions

- Which `good-first-issue` should be the first AAMS-documented contribution?
- What is the community's stance on agent-assisted contributions?
- Is there an active Zenhub board to check sprint priorities?
- What is the status of the ActivityPub/Fediverse integration?
- How does the branding system interact with the core components?

---

## File Protocol

### Created
| File | Purpose |
|---|---|
| `.agent.json` | AAMS bootstrap contract adapted for Ocelot-Social |
| `AGENTS.md` | Bridge file for all AI tools (Copilot, Cursor, Claude Code, Codex, Windsurf) |
| `READ-AGENT.md` | Full project context and agent contract |
| `WORKING/WHITEPAPER/INDEX.md` | Whitepaper index |
| `WORKING/WHITEPAPER/WP-001-architecture-overview.md` | Architecture overview whitepaper |
| `WORKING/WORKPAPER/closed/2026-03-27-copilot-aams-bootstrap.md` | This workpaper |
| `WORKING/MEMORY/ltm-index.md` | Long-term memory audit log (Entry 001) |
| `WORKING/DIARY/2026-03.md` | March 2026 diary entry |
| `WORKING/LOGS/.gitkeep` | Placeholder for logs directory |
| `WORKING/GUIDELINES/.gitkeep` | Placeholder for guidelines directory |
| `WORKING/TOOLS/.gitkeep` | Placeholder for tools directory |
| `WORKING/AGENT-MEMORY/.gitkeep` | Placeholder for vector store directory |
| `WORKING/WORKPAPER/closed/.gitkeep` | Placeholder for closed workpapers |

### Modified
| File | Change |
|---|---|
| `.gitignore` | Added AAMS-specific ignore patterns |

### Deleted
None.

---

## Decisions

1. **LTM mode**: `markdown` — zero dependencies, suitable for bootstrapping. Switch to `vector` when Python environment is set up and session count exceeds ~50.
2. **No invasive changes**: AAMS structure is additive only. Existing project files untouched.
3. **Contributor role**: Agent-assisted contributor. AAMS demonstrates value through documented work, not as a standalone PR.
4. **Diary layer**: Active from day one. Monthly files, max 10 lines per entry.

---

## Next Steps

1. Select a `good-first-issue` from the 486 open issues
2. Create a workpaper for the chosen issue, documenting the entire process
3. Implement the fix/feature with full AAMS documentation
4. The resulting `WORKPAPER/closed/` trail becomes the proof-of-concept for AAMS in Ocelot-Social
5. Prepare a branch for presentation to the core team (via Discord or PR description)
