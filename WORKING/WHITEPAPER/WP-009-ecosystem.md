# WP-009 — Ocelot Ecosystem

**Created**: 2026-03-27 | **Status**: Active | **Author**: GitHub Copilot (AAMS Bootstrap)

---

## 1. Project Identity

| Aspect | Detail |
|---|---|
| Name | Ocelot.Social |
| Version | 3.15.1 (March 2026) |
| License | MIT |
| Repository | `Ocelot-Social-Community/Ocelot-Social` |
| Website | https://ocelot.social |
| Staging | https://stage.ocelot.social |
| Discord | https://discord.gg/AJSX9DCSUA |
| Organization | busFaktor() e.V. (German charity, registered association) |
| History | Fork/evolution of Human Connection project |
| Stats | 109 stars, 51 forks, 17,000+ commits, 486 open issues, 91 open PRs |

### Mission

> Enable people to participate fairly and equally in online social networks. Equality of opportunity for all people and their diverse voices.

### Vision

Federate via ActivityPub / Fediverse (preparatory schema fields exist, not yet active).

---

## 2. Core Team

| Name | GitHub | Role |
|---|---|---|
| Ulf | @ulfgebhardt | Core |
| Moriz | @Mogge | Core |
| Wolle | @Tirokk | Core |
| Alex | @ogerly | Core |
| Hannes | @elweyn5803 | Core |
| Mathias | @mahula | Core |
| Markus | @maeckes | Core |

### Working Model

- Daily standup Mon–Thu 11:30 CET on Discord
- Sprint-based (Zenhub board)
- Pair programming sessions available
- Collective code ownership
- Philosophy: open-source as a learning experience

---

## 3. Feature Set

| Feature | Description |
|---|---|
| **News Feed** | Filterable feed (followed, groups, categories, languages, emotions, post types) |
| **Posts** | Articles + Events with rich text (Tiptap), hashtags, mentions, categories |
| **Comments** | Threaded comments on posts |
| **Groups** | Public/closed/hidden groups with roles (owner/admin/usual/pending) |
| **Chat** | Real-time messaging (WebSocket), rooms, file attachments |
| **Search** | Full-text search across posts, users, groups, hashtags (Neo4j Lucene) |
| **Map** | Geographic view (Mapbox GL) |
| **User Profiles** | Avatar, about, location, social media links, badges |
| **Moderation** | Report system, content disable/enable, moderator review |
| **Admin** | Category management, user roles, donations, invites, statistics |
| **Notifications** | Real-time (WebSocket) + email notifications |
| **Internationalization** | 11 locales (EN, DE, NL, FR, IT, ES, PT, PL, RU, SQ, UK) |
| **PWA** | Progressive Web App support |
| **White-Label** | Full branding system for custom deployments |
| **Invite System** | Personal + group invite codes with expiry |
| **Badges** | Verification + trophy badge system |
| **Donations** | Donation goal tracking with progress bar |
| **Embeds** | URL metadata (oEmbed + metascraper) |

---

## 4. Repository Structure

**Not a monorepo** (no `workspaces` field). Each sub-project has its own `package.json`:

```
ocelot-social/
├── backend/          → Node.js GraphQL API
├── webapp/           → Nuxt.js SSR frontend
├── packages/ui/      → Shared component library
├── cypress/          → E2E test suite
├── neo4j/            → Database Dockerfile
├── deployment/       → Helm charts
├── styleguide/       → Legacy (retired)
├── scripts/          → Release + translation scripts
├── minio/            → Object storage config
└── .github/          → CI/CD workflows
```

### Root Scripts

| Script | Command |
|---|---|
| `db:seed` | Seed database |
| `db:reset` | Reset database |
| `docs:build` | VuePress documentation build |
| `docs:dev` | VuePress dev server |
| `cypress:run` | E2E tests headless |
| `cypress:open` | E2E tests interactive |
| `release` | Release script |

---

## 5. Contribution Workflow

### Process (8 Steps)

1. Find issue (sprint planning or anytime)
2. Communicate availability with team
3. Understand issue in detail
4. Self-assign, move to "In Progress" on Zenhub
5. Branch: `<issue-number>-<description>` (push directly, no fork)
6. WIP PR with regular pushes
7. Remove WIP, request reviews
8. Incorporate feedback → merge to master

### PR Requirements

- Must fix an existing issue (create one first if needed)
- Include tests
- Pass all CI checks (linter, backend tests, webapp tests, coverage, E2E)
- 1 approval minimum (2 approvals if >10 files changed)

### Issue Templates (7)

bug_report, devops_ticket, epic, feature_request, question, refactor_ticket, release

---

## 6. CI/CD Pipeline

### GitHub Actions Workflows (19)

| Category | Workflows |
|---|---|
| **Testing** | test-backend, test-webapp, test-e2e, test.lint_pr |
| **Publishing** | publish, docker-push |
| **Documentation** | check-documentation, deploy-documentation |
| **UI Library** | ui-build, ui-compatibility, ui-docker, ui-lint, ui-release, ui-size, ui-storybook, ui-test, ui-verify, ui-visual |

### Dependabot

Weekly Saturday updates for 7 ecosystems:
- Root (npm + github-actions)
- Backend (npm + docker)
- Webapp (npm + docker)
- Neo4j (docker)
- Deployment (docker)
- packages/ui (npm)
- packages/ui/examples/* (npm)

Dependency grouping: babel, cypress, vuepress, apollo-server, metascraper, apollo, jest, mapbox, storybook, vue, vite, vitest.

### Release Automation

| Component | Tool |
|---|---|
| Main repository | `scripts/release.sh` + `auto-changelog` |
| `@ocelot-social/ui` | `release-please` (Node type, semantic versioning) |

---

## 7. White-Label / Branding System

### Architecture

The platform supports full white-label deployments. Operators create a **separate branding repository** (template: `stage.ocelot.social`) and overlay it via Docker volumes.

### Branding Mount Points

| Backend | Webapp |
|---|---|
| `backend/branding/constants/` | `webapp/branding/` |
| `backend/branding/data/` | `webapp/constants/metadata.js` |
| `backend/branding/email/` | `webapp/constants/xxxBranded.js` files |
| `backend/branding/middlewares/` | `webapp/assets/_new/icons/svgs/` |
| `backend/branding/public/` | `webapp/assets/styles/imports/_branding.scss` |

### Customizable Elements

| Element | Mechanism |
|---|---|
| Application name/description | metadata.js override |
| Logo | SVG in branding directory |
| Colors/theme | SCSS `_branding.scss` + CSS Custom Properties |
| Icons | SVG override (branding wins over library) |
| Login page | `loginBranded.js` constants |
| Registration page | `registrationBranded.js` constants |
| Header menu | `headerMenuBranded.js` constants |
| Logo variations | `logosBranded.js` constants |
| Email templates | Backend branding email directory |
| Footer links | `links.js` constants |
| Internal pages | HTML locale files |

### Identity Constants (duplicated)

`metadata.js` exists in both `backend/src/config/` and `webapp/constants/` — must be kept in sync manually or via branding overlay.

---

## 8. Documentation

| Source | Format |
|---|---|
| VuePress site | Markdown → static site (`docs:build` / `docs:dev`) |
| `SUMMARY.md` | VuePress sidebar navigation |
| Per-module READMEs | backend/, webapp/, cypress/, neo4j/, deployment/ |
| Feature specs | `cypress/features.md` |
| Code-level docs | Inline, JSDoc (sparse) |
| Storybook | Component documentation (packages/ui) |
| Wiki | GitHub Wiki (screenshots, guides) |

---

## 9. Human Connection Heritage

Ocelot.Social evolved from the **Human Connection** project:
- Package prefix `@human-connection/styleguide` (legacy, now retired)
- `Ds` component prefix from Human Connection design system
- Some database seed data and migration patterns inherited
- busFaktor() e.V. was founded to support continued development
- Community and mission continuity from Human Connection

---

## 10. Deployment Variants

| Variant | Method |
|---|---|
| **Local Development** | Docker Compose (`docker compose up`) |
| **Testing** | Docker Compose (`docker compose -f docker-compose.test.yml`) |
| **Staging** | Kubernetes/Helm (stage.ocelot.social) |
| **Production** | Kubernetes/Helm (custom branding overlay) |
| **Custom Instance** | Fork + branding repo + Helm deployment |

Demo credentials available on staging: `user@example.org` / `moderator@example.org` / `admin@example.org` (pw: 1234).

---

## 11. External Services & Dependencies

| Service | Purpose | Required |
|---|---|---|
| **Neo4j** | Graph database | Yes |
| **MinIO/S3** | Object storage | Yes |
| **Imagor** | Image proxy/transforms | Yes (for images) |
| **Redis** | WebSocket PubSub | Optional (in-memory fallback) |
| **Maildev** | Email testing | Dev only |
| **SMTP** | Email delivery | Production |
| **Mapbox** | Map tiles + geocoding | Optional |
| **Sentry** | Error tracking | Optional |
| **BrowserStack** | Cross-browser testing | Optional |

---

## 12. Current Strategic Direction

Based on v3.15.0 changelog and codebase analysis:

| Initiative | Status |
|---|---|
| **UI Migration** (ds-* → Os*) | 89% complete |
| **Vue 3 Preparation** | vue-demi bridge active, Composition API available |
| **Backend TypeScript** | Migration in progress |
| **Tailwind CSS 4** | Active in packages/ui |
| **ActivityPub/Federation** | Schema fields prepared, not active |
| **Node.js modernization** | Running Node 20+ (latest compatibility tests up to 25) |
| **Neo4j upgrade** | Not started (blocked by neo4j-graphql-js) |
| **Nuxt 3 migration** | Not started |
| **Supabase evaluation** | Not started (pending analysis) |
