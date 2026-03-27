# Workpaper: Version Currency Assessment

**Session**: 2026-03-27 | **Author**: GitHub Copilot | **Type**: Assessment

---

## 1. Purpose

Comprehensive analysis of all dependency versions across the Ocelot-Social monorepo to identify outdated, deprecated, end-of-life, and security-relevant packages. Provides a prioritized upgrade roadmap.

## 2. File Protocol

| File | Operation |
|---|---|
| `backend/package.json` | READ — 63 deps + 21 devDeps |
| `webapp/package.json` | READ — 45 deps + 35 devDeps |
| `packages/ui/package.json` | READ — 4 deps + 32 devDeps |
| `package.json` (root) | READ — 17 devDeps + 4 optionalDeps |
| `styleguide/package.json` | READ — 1 dep + 46 devDeps |

---

## 3. Dependency Inventory Summary

| Layer | Dependencies | DevDependencies | Total |
|---|---|---|---|
| Root | 0 | 17 (+4 optional) | 21 |
| Backend | 63 | 21 | 84 |
| Webapp | 45 | 35 | 80 |
| Packages/UI | 4 (+2 peer) | 32 | 38 |
| Styleguide (legacy) | 1 | 46 | 47 |
| **Total unique** | — | — | **~270** |

---

## 4. CRITICAL — Deprecated / Unmaintained / EOL

These packages have no active maintenance and represent security and compatibility risks.

| Package | Layer | Version | Status | Risk |
|---|---|---|---|---|
| `neo4j-graphql-js` | Backend | `2.11.5` (exact pin) | **DEPRECATED** since 2021, replaced by `@neo4j/graphql` | 🔴 CRITICAL — blocks Neo4j 5 upgrade, no security patches |
| `neode` | Backend | `^0.4.9` | **UNMAINTAINED** since 2020 | 🔴 CRITICAL — no Neo4j 5 support, no bug fixes |
| `subscriptions-transport-ws` | Backend | `^0.11.0` | **DEPRECATED**, replaced by `graphql-ws` | 🟡 MEDIUM — already dual-protocol, can drop |
| `apollo-client` | Webapp | `~2.6.10` | **UNMAINTAINED** v2, replaced by `@apollo/client` v3+ | 🔴 HIGH — no security patches |
| `apollo-cache-inmemory` | Webapp | `~1.6.6` | **UNMAINTAINED** v1 (part of Apollo Client v2) | 🔴 HIGH — same as above |
| `@nuxtjs/apollo` | Webapp | `^4.0.0-rc19` | **RC release** for Nuxt 2, likely abandoned | 🟡 MEDIUM |
| `vue-template-compiler` | Styleguide | `^2.6.10` | **Legacy** (only for Vue 2 SFC compilation) | ⚪ N/A — styleguide is retired |
| `core-js` | Webapp | `~2.6.10` | **v2 is unmaintained**, v3 is current | 🟡 MEDIUM |

---

## 5. HIGH PRIORITY — Significantly Behind Current

| Package | Layer | Installed | Current | Gap | Notes |
|---|---|---|---|---|---|
| `@sentry/node` | Backend | `^5.30.0` | `8.x` | 3 majors | v5 → v8: complete API rewrite, performance monitoring |
| `neo4j-driver` | Backend | `^4.4.11` | `5.x` | 1 major | Blocked by neo4j-graphql-js |
| `graphql` | Webapp | `14.7.0` (pinned) | `16.x` | 2 majors | Force-resolved to 14.x for Apollo Client 2 compat |
| `jsonwebtoken` | Backend | `~8.5.1` | `9.x` | 1 major | v9 added algorithm validation (security) |
| `eslint` | Webapp | `^7.28.0` | `9.x` | 2 majors | eslint 7 is unmaintained |
| `nuxt` | Webapp | `^2.18.1` | `3.x` | 1 major | Vue 3 / Nitro / Vite migration |
| `vue` | Webapp | `~2.7.16` | `3.5.x` | 1 major | Significant migration effort |
| `date-fns` | Webapp | `2.22.1` (pinned) | `4.x` | 2 majors | Tree-shaking improvements |
| `mapbox-gl` | Webapp | `1.13.3` (pinned) | `3.x` | 2 majors | License change (v2+: proprietary ToS) |
| `tiptap` | Webapp | `~1.26.6` | `2.x` | 1 major | Complete rewrite for Vue 3 |
| `tiptap-extensions` | Webapp | `~1.28.8` | ^2.x (modular) | 1 major | Replaced by individual packages |
| `@storybook/vue` | Webapp | `~7.4.0` | `10.x` | 3 majors | Storybook Vue 2 support being dropped |
| `@babel/core` | Styleguide | `~7.6.0` | `7.29.x` | 23 minors | Deeply legacy |
| `Express` | Backend | `^4.22.1` | `5.x` | 1 major | Express 5 recently released |

---

## 6. MEDIUM PRIORITY — Behind Current

| Package | Layer | Installed | Current | Gap |
|---|---|---|---|---|
| `graphql-upload` | Backend | `^13.0.0` | `16.x` | 3 majors |
| `node-fetch` | Backend | `^2.7.0` | `3.x` (ESM only) | 1 major |
| `helmet` | Backend | `~8.1.0` | `8.x` | Current ✅ |
| `lodash` | Backend | `~4.17.23` | `4.17.21` | Current ✅ |
| `sanitize-html` | Backend | `~2.17.2` | `2.x` | Current ✅ |
| `tippy.js` | Webapp | `^4.3.5` | `6.x` | 2 majors |
| `v-tooltip` | Webapp | `~2.1.3` | `5.x` (Vue 3 only) | Blocked by Vue 2 |
| `sass` | Webapp | `1.77.6` (pinned) | `1.97.x` | 20 minors |
| `sass-loader` | Webapp | `^10.4.1` | `16.x` | 6 majors |
| `babel-loader` | Webapp | `~8.1.0` | `9.x` | 1 major |
| `css-loader` | Webapp | `^4.2.0` | `7.x` | 3 majors |
| `style-loader` | Webapp | `~0.23.1` | `4.x` | 4 majors |
| `cropperjs` | Webapp | `^1.6.2` | `2.x` | 1 major |
| `graphql-request` | Root | `^2.0.0` | `7.x` | 5 majors |

---

## 7. LOW PRIORITY — Slightly Behind or Current

| Package | Layer | Status |
|---|---|---|
| `bcryptjs` | Backend | `~3.0.3` — Current ✅ |
| `express` | Backend | `^4.22.1` — Latest 4.x ✅ |
| `ws` | Backend | `^8.18.2` — Current ✅ |
| `ioredis` | Backend | `^5.10.1` — Current ✅ |
| `uuid` | Backend | `~9.0.1` — v11.x available (minor gap) |
| `validator` | Both | `^13.15.26` — Current ✅ |
| `typescript` | Backend | `^5.8.3` — Near current ✅ |
| `jest` | Backend | `^30.3.0` — Cutting edge ✅ |

---

## 8. Packages/UI Layer — Modern ✅

The `packages/ui` layer is the most current:

| Package | Version | Current | Status |
|---|---|---|---|
| `vite` | `^7.3.1` | 7.x | ✅ Latest |
| `vitest` | `^4.0.18` | 4.x | ✅ Latest |
| `vue` | `^3.5.29` | 3.5.x | ✅ Latest |
| `typescript` | `^5.9.3` | 5.9.x | ✅ Latest |
| `tailwindcss` | `^4.2.2` | 4.x | ✅ Latest |
| `storybook` | `^10.2.16` | 10.x | ✅ Latest |
| `eslint` | `^9.39.2` | 9.x | ✅ Latest |
| `@playwright/test` | `^1.58.2` | 1.58.x | ✅ Latest |

---

## 9. Version Resolution Conflicts

Force-resolved versions indicate compatibility issues:

| Resolution | Location | Reason |
|---|---|---|
| `graphql: 14.7.0` | Webapp | Apollo Client 2 requires graphql <16 |
| `vue: 2.7.16` | Webapp | Prevent accidental Vue 3 install |
| `vue-server-renderer: 2.7.16` | Webapp | Must match Vue version |
| `neo4j-graphql-js/graphql: ^16.11.0` | Backend | Force neo4j-graphql-js to use graphql 16 |
| `graphql-upload/graphql: ^16.11.0` | Backend | Same |
| `fs-capacitor: ^6.2.0` | Backend | Fix for graphql-upload internal |
| `strip-ansi: 6.0.1` | Backend | ESM/CJS compat issue |
| `string-width: 4.2.0` | Backend | ESM/CJS compat issue |
| `wrap-ansi: 7.0.0` | Backend | ESM/CJS compat issue |
| `nan: 2.17.0` | Root + Webapp | Node.js native addon compat |

---

## 10. Upgrade Roadmap (Prioritized)

### Phase 1: Security & Stability (No breaking changes)

| Action | Effort | Impact |
|---|---|---|
| Upgrade `jsonwebtoken` 8 → 9 | Low | Security: algorithm validation |
| Upgrade `@sentry/node` 5 → 8 | Medium | Performance + error tracking improvements |
| Remove `subscriptions-transport-ws` (keep `graphql-ws` only) | Low | Remove deprecated code |
| Upgrade `sass` 1.77 → 1.97 | Low | Bug fixes + performance |

### Phase 2: Database Modernization (Major effort, prerequisite for everything)

| Action | Effort | Impact |
|---|---|---|
| Replace `neo4j-graphql-js` 2.11 → `@neo4j/graphql` 6.x | **VERY HIGH** | Schema rewrite, resolver rewrite |
| Replace `neode` 0.4 → direct Cypher / `@neo4j/graphql` | **HIGH** | Model layer rewrite |
| Upgrade `neo4j-driver` 4.4 → 5.x | Medium | Blocked by above |
| Upgrade Neo4j 4.4 → 5.x | Medium | After driver upgrade |

### Phase 3: Frontend Modernization (Major effort)

| Action | Effort | Impact |
|---|---|---|
| Vue 2.7 → Vue 3 | **VERY HIGH** | Every component affected |
| Nuxt 2 → Nuxt 3 | **VERY HIGH** | Webpack → Vite, Nitro server |
| Apollo Client 2 → @apollo/client 3 | **HIGH** | Cache API changes |
| graphql 14 → 16 | Medium | Unblocked by Apollo 3 |
| tiptap 1 → tiptap 2 | **HIGH** | Complete editor rewrite |
| ESLint 7 → ESLint 9 | Medium | Config format change (flat config) |

### Phase 4: Cleanup

| Action | Effort | Impact |
|---|---|---|
| Delete `styleguide/` directory | Low | Remove 47 legacy dependencies |
| Update remaining minor versions | Low | Maintenance |
| Remove force resolutions | Low | After major upgrades unblock them |

---

## 11. Risk Matrix

```
                    LOW EFFORT ←→ HIGH EFFORT
         ┌──────────────────────────────────────┐
HIGH     │ jsonwebtoken 9  │ neo4j-graphql-js  │
IMPACT   │ Sentry 8        │ Vue 3 / Nuxt 3    │
         │ drop sub-ws     │ Apollo Client 3   │
         │                 │ tiptap 2          │
         ├──────────────────────────────────────┤
LOW      │ sass update     │ mapbox-gl 3       │
IMPACT   │ uuid update     │ style-loader      │
         │                 │ css-loader        │
         └──────────────────────────────────────┘
```

---

## 12. Key Findings

1. **Two critical deprecated packages** (`neo4j-graphql-js`, `neode`) block the entire upgrade chain for database-related work
2. **Webapp is 1–2 generations behind** on every major dependency (Vue, Nuxt, Apollo, graphql, ESLint)
3. **packages/ui is fully modern** — serves as the target architecture
4. **9 force resolutions** indicate deep compatibility tensions
5. **Styleguide carries 47 dead dependencies** — deleting the directory is free wins
6. **Backend is in decent shape** except for the Neo4j layer and Sentry
7. **The upgrade order matters**: Neo4j stack first (unblocks backend), then Vue 3/Nuxt 3 (unblocks Apollo 3 + graphql 16 + tiptap 2)

---

## 13. Decisions

- [ ] Confirm Phase 1 quick wins can proceed immediately
- [ ] Decide on Neo4j vs Supabase before investing in Phase 2 (see Supabase evaluation workpaper)
- [ ] Timeline estimation for Vue 3 / Nuxt 3 migration
- [ ] Decision on `mapbox-gl` v2+ license implications

---

## 14. Next Steps

1. Create Supabase evaluation workpaper (companion to Phase 2 decision)
2. Create migration workpaper for `neo4j-graphql-js` → `@neo4j/graphql` if staying with Neo4j
3. Create Vue 3 migration workpaper with component-by-component plan
