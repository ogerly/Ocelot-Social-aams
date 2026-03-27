# WP-001 — Ocelot-Social Architecture Overview

**Created**: 2026-03-27
**Status**: Active
**Author**: GitHub Copilot (AAMS Bootstrap)

---

## 1. System Overview

Ocelot-Social is a free and open-source social network platform designed for civic communities. It enables news feeds, posts, articles, events, comments, groups, maps, user accounts, and role-based access.

**Vision**: Enable fair participation in online social networks. ActivityPub/Fediverse integration planned.

**Current version**: 3.15.1 (released 2026-03-24)

---

## 2. Monorepo Structure

The project is organized as a yarn workspace monorepo:

| Directory | Role | Language |
|---|---|---|
| `backend/` | GraphQL API server | TypeScript (Node.js) |
| `webapp/` | SSR web application | JavaScript (Vue.js 2 / Nuxt.js) |
| `cypress/` | End-to-end tests | JavaScript (Cucumber/Gherkin) |
| `packages/ui/` | Shared UI component library | Vue.js |
| `styleguide/` | Storybook visual component docs | Vue.js |
| `neo4j/` | Database container config | Dockerfile |
| `deployment/` | Production deployment | Helm/YAML |
| `scripts/` | Automation | Shell |

---

## 3. Architecture Layers

```
┌─────────────────────────────────────────────┐
│           Browser / Client                   │
├─────────────────────────────────────────────┤
│     webapp (Nuxt.js SSR, port 3000)         │
│     ├── Vue Components + Vuex Store          │
│     ├── Apollo Client (GraphQL)              │
│     └── Nuxt Middleware + Plugins            │
├─────────────────────────────────────────────┤
│     backend (Apollo Server 4, port 4000)     │
│     ├── GraphQL Schema + Resolvers           │
│     ├── JWT Authentication                   │
│     ├── File Upload (S3-compatible)          │
│     ├── Email Service (Nodemailer)           │
│     └── Neo4j Driver (Cypher queries)        │
├─────────────────────────────────────────────┤
│     Neo4j (Graph Database, port 7687)        │
│     └── Bolt protocol, no auth in dev        │
└─────────────────────────────────────────────┘
```

---

## 4. Data Flow

1. **Client → Webapp**: Browser requests hit Nuxt.js SSR server
2. **Webapp → Backend**: Apollo Client sends GraphQL queries/mutations to `http://backend:4000`
3. **Backend → Neo4j**: Resolvers execute Cypher queries via Neo4j driver over `bolt://neo4j:7687`
4. **Authentication**: JWT tokens issued by backend, validated on each GraphQL request via context
5. **File uploads**: Handled by backend, stored in S3-compatible storage (MinIO in dev)

---

## 5. Development Environment

Docker Compose orchestrates all services:

| Service | Image | Port | Depends on |
|---|---|---|---|
| `webapp` | Custom (Nuxt build) | 3000 | backend |
| `backend` | Custom (Node.js) | 4000 | neo4j |
| `neo4j` | neo4j:community | 7687 | — |
| `maintenance` | Custom (static page) | 3001 | — |

**Setup**: `docker compose up` starts full stack. Hot-reload via `yarn dev` in individual services.

**Seeding**: `yarn db:seed` populates Neo4j with test data. `yarn db:reset` clears it.

---

## 6. Testing Strategy

| Level | Tool | Location | Command |
|---|---|---|---|
| Unit (backend) | Jest | `backend/src/**/*.spec.ts` | `cd backend && yarn test` |
| Unit (frontend) | Jest + Vue Test Utils | `webapp/**/*.spec.js` | `cd webapp && yarn test` |
| E2E | Cypress + Cucumber | `cypress/e2e/*.feature` | `yarn cypress:run` |
| Visual | Storybook | `styleguide/` | `cd styleguide && yarn storybook` |
| Lint | ESLint | All packages | `yarn lint` |

---

## 7. Key Architectural Decisions

- **Neo4j over relational DB**: Social graph queries (friends, followers, recommendations) are native graph traversals — orders of magnitude faster than SQL JOINs
- **Nuxt.js SSR**: Server-side rendering for SEO and initial page load performance
- **GraphQL over REST**: Single endpoint, typed schema, client-driven data fetching
- **Monorepo**: Shared tooling, atomic commits across frontend/backend, single version
- **Docker-first**: Every contributor gets identical environment regardless of OS
- **Cucumber/Gherkin E2E**: Business-readable test scenarios, bridging dev and stakeholder communication

---

## 8. Authentication & Authorization

- JWT-based authentication
- Roles: `user`, `moderator`, `admin`
- Backend resolvers enforce role-based access
- Frontend route guards via Nuxt middleware

---

## 9. Deployment

- **Staging**: `stage.ocelot.social` (auto-deploy from master)
- **Production**: Kubernetes cluster with Helm charts (`deployment/helm/`)
- **CI/CD**: GitHub Actions
- **Releases**: release-please automation (`release-please-config.json`)
