# LTM Index — Ocelot-Social

> Long-term memory audit log. Human-readable. In Git. Survives fresh clone.
> Append after every session close. Never delete entries.

---

## Entry 001 — 2026-03-27 — Bootstrap

- **Session**: AAMS bootstrap for Ocelot-Social
- **Agent**: GitHub Copilot (Claude Opus 4.6)
- **Summary**: Initial AAMS workspace created. Full repo scan performed. Architecture documented in WP-001. Repository topology mapped: backend/ (GraphQL/Apollo/Neo4j), webapp/ (Vue/Nuxt), cypress/ (E2E/Cucumber), packages/ui/ (shared components), deployment/ (Helm). Version 3.15.1, 17,000+ commits, 486 open issues, 91 open PRs. Contribution model: Discord-based onboarding, 2-week sprints, Zenhub board.
- **Key decisions**: LTM mode set to `markdown` (zero dependencies). Four-layer documentation model initialized. Contributor role: agent-assisted contributor demonstrating AAMS value.
- **Files created**: `.agent.json`, `AGENTS.md`, `READ-AGENT.md`, full `WORKING/` structure, `WP-001` whitepaper, first workpaper, diary entry.
- **Open questions**: Which `good-first-issue` to target for first AAMS-documented contribution? Community receptiveness to AAMS structure in PR?
- **Tags**: `bootstrap`, `architecture`, `onboarding`, `aams-init`

## Entry 002 — 2026-03-27 — Deep Analysis

- **Session**: Comprehensive codebase analysis for AAMS documentation example
- **Agent**: GitHub Copilot (Claude Opus 4.6)
- **Summary**: Created 9 whitepapers (WP-001 through WP-009) covering all project areas and 2 workpapers (version currency, Supabase evaluation). Deep-scanned all package.json files (270 total dependencies). Identified 2 CRITICAL deprecated packages (neo4j-graphql-js 2.11.5, neode 0.4.9) that block the entire upgrade chain. UI migration from legacy styleguide to @ocelot-social/ui is 89% complete. Webapp is 1-2 generations behind on all major deps (Vue 2, Nuxt 2, Apollo 2, graphql 14, ESLint 7). packages/ui is fully modern (Vite 7, Vue 3, Tailwind 4, Storybook 10).
- **Key decisions**: Recommended Supabase migration over Neo4j upgrade — app doesn't use graph-specific features, comparable effort but gains auth+storage+realtime+managed hosting+backups. Upgrade order: database first → then Vue 3/Nuxt 3.
- **Files created**: WP-002 through WP-009, version-currency-assessment workpaper, supabase-evaluation workpaper. Updated INDEX.md, diary, ltm-index.
- **Open questions**: Go/No-Go on Supabase? Hosting model (Cloud vs self-hosted)? ORM choice (Prisma vs Drizzle)? Timeline: parallel or sequential with Vue 3 migration?
- **Tags**: `analysis`, `database`, `supabase`, `version-currency`, `migration-planning`, `neo4j`, `vue3`

## Entry 003 — 2026-03-27 — Supabase Strategy Refined

- **Session**: Tradeoff-Abwägung und pragmatische Migrationsstrategie
- **Agent**: GitHub Copilot (Claude Opus 4.6)
- **Summary**: Supabase-Empfehlung verfeinert. Inkrementelle Migration: Auth+Storage zuerst (low risk, immediate win), dann PostgreSQL parallel aufbauen, dann Resolver migrieren, dann Neo4j abschalten. ActivityPub/Fediverse als Graph-Protokoll erfordert Hedge — Apache AGE (Graph-Extension für PostgreSQL) evaluieren. pg_graphql reicht nicht für bestehende Business-Logik — Apollo Server behalten, nur DB-Layer wechseln. Datenmigration als eigenen Milestone planen (Slugs, Relationships, Timestamps, S3-Paths).
- **Key decisions**: Kein Big Bang. Auth+Storage first. Apollo Server bleibt. Apache AGE auf Radar. Datenmigration != Nebenaufgabe.
- **Files modified**: supabase-evaluation workpaper (Sections 6, 7, 8, 10, 11, 12, 13, 14 überarbeitet), diary, ltm-index.
- **Tags**: `supabase`, `migration-strategy`, `activitypub`, `apache-age`, `pragmatic`

## Entry 004 — 2026-03-27 — Dokument-Reklassifizierung

- **Session**: Supabase-Evaluation von Workpaper zu Diskussionspapier überführt
- **Agent**: GitHub Copilot (Claude Opus 4.6)
- **Summary**: Supabase-Evaluation als DP-001 (Diskussionspapier) in WHITEPAPER/ reklassifiziert. Altes Workpaper als SUPERSEDED markiert mit Cross-Referenz. WHITEPAPER/INDEX.md um DP-001 erweitert. Rationale: Das Dokument ist eine strategische Entscheidungsgrundlage, nicht ein Session-Artefakt.
- **Key decisions**: Diskussionspapiere (DP-*) als neue Dokumentenkategorie in WHITEPAPER/ neben Whitepapers (WP-*).
- **Files created**: `WHITEPAPER/DP-001-supabase-evaluation.md`
- **Files modified**: `WHITEPAPER/INDEX.md`, `WORKPAPER/2026-03-27-supabase-evaluation.md` (SUPERSEDED), `DIARY/2026-03.md`
- **Tags**: `aams-governance`, `document-management`, `supabase`

## Entry 005 — 2026-03-27 — Full-Stack Upgrade-Plan

- **Session**: Upgrade-Planung mit Abhängigkeitsanalyse und Simulationsskript
- **Agent**: GitHub Copilot (Claude Opus 4.6)
- **Summary**: Vollständiger 5-Phasen-Upgrade-Plan erstellt. Alle 5 Layer deep-scanned (270 Pakete). 6 kritische Abhängigkeitsketten identifiziert: GraphQL (16 vs 14 cross-layer), Vue/Nuxt (Vue 3 braucht Nuxt 3), Neo4j (neo4j-graphql-js blockiert alles), Webpack (Nuxt 2 bindet Loader), ESLint (7 vs 9), Jest (vue2-jest bindet). Testinfrastruktur: 472 Testdateien (71 Backend/92%, 152 Webapp/83%, 27 UI, 24 E2E + 4 broken). Python-Simulationsskript erzeugt — prüft Versionskompatibilität offline, simuliert Phasen, generiert HTML-Reports. Test-Ergebnis: Phase 1+2 bereit (keine Blocker), Phase 3 hat 1 Blocker (neo4j-graphql-js), Phase 4 hat 4 Blocker (Apollo→graphql→Nuxt→Vue Kette).
- **Key decisions**: (1) 5-Phasen-Modell: Cleanup→Backend→Webapp→DB→Frontend, (2) Phase 1+2 parallel möglich, (3) Python-Simulator statt manueller Prüfung, (4) mapbox-gl→maplibre-gl (Lizenz), (5) Styleguide löschen (47 tote Deps).
- **Files created**: `WORKPAPER/2026-03-27-upgrade-plan.md`, `TOOLS/upgrade-simulator.py`, `WORKPAPER/closed/2026-03-27-session-004-upgrade-planning.md`
- **Files modified**: `DIARY/2026-03.md`
- **Open questions**: Styleguide-Löschung bestätigen? mapbox vs maplibre? Jest vs Vitest bei Nuxt 3? Nuxt Bridge als Zwischenschritt?
- **Tags**: `upgrade`, `dependency-analysis`, `simulation`, `testing`, `python-tool`, `cross-layer`
