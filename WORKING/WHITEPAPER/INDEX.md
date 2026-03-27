# Whitepaper Index — Ocelot-Social

> Stable architecture truth. Written once, updated only on architecture decisions. Never deleted.

---

## WP-001 — Architecture Overview

**Created**: 2026-03-27 | **Status**: Active
**File**: [WP-001-architecture-overview.md](./WP-001-architecture-overview.md)

High-level platform architecture: monorepo structure, tech stack layers (Vue/Nuxt frontend → GraphQL/Apollo middleware → Neo4j graph database), Docker-based development, Kubernetes/Helm deployment. Service topology, data flow, JWT auth, testing strategy.

---

## WP-002 — Backend Deep Analysis

**Created**: 2026-03-27 | **Status**: Active
**File**: [WP-002-backend.md](./WP-002-backend.md)

GraphQL Apollo Server 4, TypeScript, Neo4j driver (4.4), middleware pipeline (16 layers), resolver architecture, JWT auth, S3 uploads, email system, Redis PubSub, database models (18 Neode models), migration system.

---

## WP-003 — Cypress/E2E Testing Analysis

**Created**: 2026-03-27 | **Status**: Active
**File**: [WP-003-cypress.md](./WP-003-cypress.md)

24 feature files (4 broken), Cucumber/Gherkin BDD, Webpack preprocessor, 137 step definitions, factory-based test data, direct Neo4j access in tests, parallel execution support.

---

## WP-004 — Deployment & Infrastructure Analysis

**Created**: 2026-03-27 | **Status**: Active
**File**: [WP-004-deployment.md](./WP-004-deployment.md)

Docker Compose (4 configs), Kubernetes/Helm (2 charts), GHCR container registry, MinIO S3, Imagor image processing, Maildev, multi-stage Dockerfile builds.

---

## WP-005 — Neo4j Database Analysis

**Created**: 2026-03-27 | **Status**: Active
**File**: [WP-005-database.md](./WP-005-database.md)

Neo4j 4.4 Community, `neo4j-graphql-js` 2.11.5 (deprecated), Neode ORM 0.4.9 (unmaintained), APOC plugin, 18 data models, Cypher queries, migration system, data seeding.

---

## WP-006 — Styleguide & UI Library Analysis

**Created**: 2026-03-27 | **Status**: Active
**File**: [WP-006-styleguide.md](./WP-006-styleguide.md)

Legacy styleguide (`@human-connection/styleguide` v0.5.22, Vue CLI 3), new `@ocelot-social/ui` (Vite + Vue 2.7/3 compatible, Tailwind 4, CVA, Storybook 10). Two-generation design system coexistence.

---

## WP-007 — Webapp/Frontend Analysis

**Created**: 2026-03-27 | **Status**: Active
**File**: [WP-007-webapp.md](./WP-007-webapp.md)

Nuxt.js 2.18/Vue 2.7, Apollo Client 2, 85+ Vue components, 11 Vuex modules, 30+ pages, Tiptap editor, Mapbox maps, PWA, 11 locales, design system tokens, branding system.

---

## WP-008 — API Interfaces & Data Flow

**Created**: 2026-03-27 | **Status**: Active
**File**: [WP-008-api-interfaces.md](./WP-008-api-interfaces.md)

GraphQL schema (neo4j-graphql-js augmented), WebSocket subscriptions (dual protocol), ActivityPub proxy routes, S3/MinIO file storage, Imagor image processing, Redis PubSub, SMTP email.

---

## WP-009 — Ocelot Ecosystem Overview

**Created**: 2026-03-27 | **Status**: Active
**File**: [WP-009-ecosystem.md](./WP-009-ecosystem.md)

Community structure, branding/white-label system, deployment variants, contribution workflow, Human Connection heritage, release automation, CI/CD pipeline, external integrations.

---

## DP-001 — Supabase Evaluation (Diskussionspapier)

**Created**: 2026-03-27 | **Status**: Offen (zur Diskussion)
**File**: [DP-001-supabase-evaluation.md](./DP-001-supabase-evaluation.md)
**Herkunft**: Reklassifiziert aus Workpaper `2026-03-27-supabase-evaluation.md`

Neo4j → Supabase Migration Assessment. Evaluierung von Feasibility, Aufwand, Benefits, Risiken. Empfehlung: Inkrementelle Migration (Auth+Storage zuerst, dann PostgreSQL parallel, Backend-Umstellung, Neo4j-Abschaltung). 12–16 Wochen Gesamtaufwand. Apache AGE als ActivityPub-Hedge. 6 offene Entscheidungspunkte.
