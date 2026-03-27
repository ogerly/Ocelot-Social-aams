# Workpaper: Ocelot-Social Full-Stack Upgrade Plan

**Session**: 2026-03-27 | **Autor**: GitHub Copilot | **Typ**: Upgrade-Planung  
**Sprache**: Deutsch

---

## 1. Zweck

Systematische Planung des vollständigen Dependency-Upgrades aller Ocelot-Social-Layer auf die aktuellsten Versionen. Paketweise Analyse mit Abhängigkeitsketten, Upgrade-Reihenfolge, Risikobewertung und Validierungsstrategie.

## 2. File Protocol

| Datei | Operation |
|---|---|
| `backend/package.json` | READ — 63 Deps + 21 DevDeps |
| `webapp/package.json` | READ — 45 Deps + 35 DevDeps |
| `packages/ui/package.json` | READ — 4 Deps + 32 DevDeps |
| `package.json` (Root) | READ — 17 DevDeps + 4 OptionalDeps |
| `styleguide/package.json` | READ — 1 Dep + 46 DevDeps |
| `cypress/cypress.config.js` | READ — E2E-Konfiguration |
| WP-Version-Currency | READ — Bestehende Versionsanalyse |

---

## 3. Zusammenfassung: Aktueller Stand

### Inventar

| Layer | Dependencies | DevDeps | Gesamt | Zustand |
|---|---|---|---|---|
| **Root** | 0 | 17 (+4 opt.) | 21 | 🟡 Cypress + Build-Tools |
| **Backend** | 63 | 21 | 84 | 🟡 Neo4j-Layer kritisch, Rest OK |
| **Webapp** | 45 | 35 | 80 | 🔴 2 Generationen zurück |
| **packages/ui** | 4 (+2 peer) | 32 | 38 | 🟢 Vollständig modern |
| **Styleguide** | 1 | 46 | 47 | 🔴 Legacy, kann entfernt werden |
| **Gesamt** | — | — | **~270** | — |

### Testinfrastruktur

| Layer | Framework | Testdateien | Coverage-Schwelle | Kommando |
|---|---|---|---|---|
| Backend | Jest 30.3 | ~71 `.spec.ts` | 92% Lines | `cd backend && yarn test` |
| Webapp | Jest 29.7 | ~152 `.spec.js` | 83% Lines | `cd webapp && yarn test` |
| packages/ui | Vitest 4.0 | ~27 `.spec.ts` | — | `cd packages/ui && yarn test` |
| E2E | Cypress 15.11 + Cucumber | 24 Features + 137 Steps | — | `yarn cypress:run` |
| Styleguide | Jest (inaktiv) | 0 aktive | — | `echo "TODO"` |

**Gesamte Testabdeckung: ~472 Testdateien/Szenarien**

---

## 4. Abhängigkeitsketten — Was hängt wovon ab?

### 4.1 GraphQL-Kette (KRITISCH)

```
Backend:  graphql ^16.13.1  ←→  @apollo/server 4.11.3
                                   ↕
                               neo4j-graphql-js 2.11.5 (DEPRECATED)
                                   ↕
                               neode 0.4.9 (UNMAINTAINED)

Webapp:   graphql 14.7.0 (HARDCODED Resolution!)
              ↕
          apollo-client 2.6.10 (EOL)
              ↕
          @nuxtjs/apollo 4.0.0-rc19 (Abandoned RC)
```

**Problem**: Backend und Webapp nutzen **inkompatible graphql-Versionen** (16 vs 14). Die Webapp ist durch Apollo Client 2 auf graphql 14 festgenagelt.

**Auflösung**: Apollo Client 2 → @apollo/client 3 muss VOR graphql 14 → 16 passieren.

### 4.2 Vue/Nuxt-Kette (KRITISCH)

```
packages/ui:  vue 2.7 || 3.x (via vue-demi) ✅
Webapp:       vue 2.7.16 → Nuxt 2.18.1 → KANN NICHT auf Vue 3 ohne Nuxt 3
Styleguide:   vue 2.6.10 (URALT)
```

**Problem**: Vue 3 erfordert Nuxt 3. Nuxt 3 ist ein kompletter Rewrite (Nitro, Vite statt Webpack). Das ist die größte Einzelmigration.

**Auflösung**: Nuxt 2 → Nuxt 3 ist der Gatekeeper für Vue 3, das wiederum tiptap 2, @vue/test-utils 2, vue-router 4 etc. freischaltet.

### 4.3 Neo4j-Kette (KRITISCH)

```
neo4j-graphql-js 2.11.5 (DEPRECATED 2021)
    ↓ erfordert
neo4j-driver 4.4.11 (EOL)
    ↓ erfordert
Neo4j Server 4.4 (EOL seit Dez 2023)

neode 0.4.9 (UNMAINTAINED 2020)
    ↓ erfordert
neo4j-driver 4.x
```

**Problem**: `neo4j-graphql-js` ist tot. Kein Upgrade-Pfad innerhalb Neo4j ohne vollständigen Rewrite zu `@neo4j/graphql` 6.x (komplett andere Schema-Syntax und API).

**Auflösung**: Entweder @neo4j/graphql 6.x Migration ODER Supabase-Migration (siehe DP-001).

### 4.4 Webpack/Loader-Kette (Webapp)

```
Nuxt 2.18.1 → Webpack 4 (intern)
    ↓ erfordert kompatible Loader
style-loader 0.23.1 (2018!)
css-loader 4.2.0
sass-loader 10.4.1
babel-loader 8.1.0
```

**Problem**: Alle Loader sind an Webpack 4 (via Nuxt 2) gebunden. Upgrade auf aktuelle Versionen NUR mit Nuxt 3 (Vite).

**Auflösung**: Loader-Upgrades sind automatisch erledigt, sobald Nuxt 3 (Vite) kommt. Vorher nicht anfassen.

### 4.5 ESLint-Kette

```
Backend:      eslint 9.27.0 (Flat Config) ✅
packages/ui:  eslint 9.39.2 (Flat Config) ✅
Webapp:       eslint 7.28.0 (Legacy .eslintrc) 🔴
Styleguide:   @vue/cli-plugin-eslint 3.11 🔴
```

**Problem**: Webapp nutzt ESLint 7 mit Legacy-Config. Backend/UI sind bereits auf Flat Config.

**Auflösung**: Webapp ESLint 7 → 9 ist unabhängig von anderen Upgrades möglich. Config-Format muss migriert werden.

### 4.6 Jest/Test-Kette

```
Backend:      jest 30.3.0 + ts-jest 29.4.6 ✅
Webapp:       jest 29.7 + @vue/vue2-jest 29 ✅
packages/ui:  vitest 4.0.18 ✅
```

**Problem**: Webapp-Jest ist an vue2-jest gebunden. Vue 3 erfordert @vue/vue3-jest oder Wechsel zu Vitest.

**Auflösung**: Test-Framework-Upgrade kommt MIT der Vue 3 Migration.

---

## 5. Layer-Analyse: Was kann pro Layer passieren?

### 5.1 Backend — Paketliste

#### 🟢 SOFORT MÖGLICH (keine Abhängigkeitskonflikte)

| Paket | Aktuell | Ziel | Aufwand | Risiko | Hinweis |
|---|---|---|---|---|---|
| `jsonwebtoken` | ~8.5.1 | 9.x | Gering | Gering | Sicherheit: Algorithm-Validierung |
| `@sentry/node` | ^5.30.0 | 8.x | Mittel | Gering | API komplett neu, Performance-Monitoring |
| `express` | ^4.22.1 | 5.x | Gering | Gering | Express 5 kürzlich released |
| `uuid` | ~9.0.1 | 11.x | Gering | Gering | API stabil |
| `graphql-upload` | ^13.0.0 | 16.x | Gering | Gering | API-Änderungen minimal |
| `helmet` | ~8.1.0 | 8.x | — | — | Bereits aktuell ✅ |
| `bcryptjs` | ~3.0.3 | 3.x | — | — | Bereits aktuell ✅ |
| `ws` | ^8.18.2 | 8.x | — | — | Bereits aktuell ✅ |
| `ioredis` | ^5.10.1 | 5.x | — | — | Bereits aktuell ✅ |
| `typescript` | ^5.8.3 | 5.9.x | Gering | Gering | Minor-Update |

#### 🟡 ERFORDERT PLANUNG

| Paket | Aktuell | Ziel | Aufwand | Blocker |
|---|---|---|---|---|
| `subscriptions-transport-ws` | ^0.11.0 | ENTFERNEN | Gering | Prüfen ob Clients noch altes Protokoll nutzen |
| `node-fetch` | ^2.7.0 | 3.x (ESM) | Mittel | ESM-Only — erfordert import-Syntax |

#### 🔴 BLOCKIERT (Neo4j-Kette)

| Paket | Aktuell | Ziel | Aufwand | Blocker |
|---|---|---|---|---|
| `neo4j-graphql-js` | 2.11.5 | @neo4j/graphql 6.x | SEHR HOCH | Kompletter Schema- und Resolver-Rewrite |
| `neode` | ^0.4.9 | ENTFERNEN | HOCH | Alle 18 Model-Dateien umschreiben |
| `neo4j-driver` | ^4.4.11 | 5.x | Mittel | Blockiert durch neo4j-graphql-js |

### 5.2 Webapp — Paketliste

#### 🟢 SOFORT MÖGLICH

| Paket | Aktuell | Ziel | Aufwand | Risiko | Hinweis |
|---|---|---|---|---|---|
| `sass` | 1.77.6 | 1.97.x | Gering | Gering | Nur Minor, Bugfixes |
| `cropperjs` | ^1.6.2 | 2.x | Mittel | Gering | API-Änderungen |
| `date-fns` | 2.22.1 | 4.x | Mittel | Gering | Tree-Shaking verbessert, Import-Pfade ändern sich |
| `core-js` | ~2.6.10 | 3.x | Gering | Gering | Polyfill-Struktur ändert sich |

#### 🟡 ERFORDERT ESLint-Migration (unabhängig)

| Paket | Aktuell | Ziel | Aufwand | Hinweis |
|---|---|---|---|---|
| `eslint` | ^7.28.0 | 9.x | Mittel | Config-Format: `.eslintrc` → `eslint.config.js` (Flat Config) |

#### 🔴 BLOCKIERT (Vue/Nuxt-Kette — Big Bang)

| Paket | Aktuell | Ziel | Aufwand | Blocker |
|---|---|---|---|---|
| `vue` | ~2.7.16 | 3.5.x | SEHR HOCH | Nuxt 3 muss zuerst |
| `nuxt` | ^2.18.1 | 3.x | SEHR HOCH | Kompletter Rewrite (Nitro, Vite) |
| `apollo-client` | ~2.6.10 | @apollo/client 3.x | HOCH | Cache-API komplett anders |
| `graphql` | 14.7.0 | 16.x | Mittel | Blockiert durch Apollo Client 2 |
| `@nuxtjs/apollo` | ^4.0.0-rc19 | @nuxtjs/apollo 5.x (Nuxt 3) | HOCH | Blockiert durch Nuxt 2 |
| `tiptap` | ~1.26.6 | 2.x | HOCH | Kompletter Editor-Rewrite, braucht Vue 3 |
| `@storybook/vue` | ~7.4.0 | 10.x + vue3 | HOCH | Storybook Vue 2 Support wird eingestellt |
| `v-tooltip` | ~2.1.3 | 5.x | Mittel | Braucht Vue 3 |
| `tippy.js` | ^4.3.5 | 6.x | Mittel | Unabhängig, aber v-tooltip bindet |
| `style-loader` | ~0.23.1 | ENTFÄLLT | — | Vite ersetzt Webpack bei Nuxt 3 |
| `css-loader` | ^4.2.0 | ENTFÄLLT | — | Vite ersetzt Webpack bei Nuxt 3 |
| `sass-loader` | ^10.4.1 | ENTFÄLLT | — | Vite ersetzt Webpack bei Nuxt 3 |
| `babel-loader` | ~8.1.0 | ENTFÄLLT | — | Vite ersetzt Webpack bei Nuxt 3 |

#### ⚠️ LIZENZ-ENTSCHEIDUNG

| Paket | Aktuell | Ziel | Problem |
|---|---|---|---|
| `mapbox-gl` | 1.13.3 | 3.x | Ab v2 proprietäre ToS. Alternative: `maplibre-gl` (FOSS-Fork) |

### 5.3 Cypress / E2E

#### 🟢 AKTUELLER STAND

| Paket | Aktuell | Ziel | Aufwand |
|---|---|---|---|
| `cypress` | 15.11.0 | 15.x | Bereits aktuell ✅ |
| `@badeball/cypress-cucumber-preprocessor` | 24.0.1 | 24.x | Bereits aktuell ✅ |
| `@cucumber/cucumber` | 12.7.0 | 12.x | Bereits aktuell ✅ |
| `@cypress/webpack-preprocessor` | 7.0.2 | 7.x | Bereits aktuell ✅ |
| `multiple-cucumber-html-reporter` | 3.10.0 | 3.x | Bereits aktuell ✅ |

**Cypress ist vollständig aktuell. Kein Handlungsbedarf.**

Kaputte Features (vorher reparieren!):
- `Search.feature.broken`
- `User.Block.feature.broken`
- `User.Mute.feature.broken`
- `User.SettingNotifications.feature.broken`

### 5.4 packages/ui

#### 🟢 AKTUELLER STAND

| Paket | Aktuell | Status |
|---|---|---|
| `vite` | ^7.3.1 | ✅ Aktuell |
| `vitest` | ^4.0.18 | ✅ Aktuell |
| `vue` | ^3.5.29 | ✅ Aktuell |
| `typescript` | ^5.9.3 | ✅ Aktuell |
| `tailwindcss` | ^4.2.2 | ✅ Aktuell |
| `storybook` | ^10.2.16 | ✅ Aktuell |
| `eslint` | ^9.39.2 | ✅ Aktuell |
| `@playwright/test` | ^1.58.2 | ✅ Aktuell |

**packages/ui ist vollständig modern. Kein Handlungsbedarf.**

### 5.5 Styleguide

**Empfehlung: LÖSCHEN.** 

Der Styleguide trägt 47 tote Dependencies. Tests sind "TODO". Die Funktionalität ist in `packages/ui` (Storybook 10, Vue 3) aufgegangen. Das Verzeichnis kann gefahrlos entfernt werden.

### 5.6 Datenbank (Neo4j)

Siehe DP-001 (Supabase Diskussionspapier). Zwei Optionspfade:

| Option | Aufwand | Ergebnis |
|---|---|---|
| **A: Neo4j 5 Upgrade** | SEHR HOCH | neo4j-graphql-js → @neo4j/graphql 6.x + neode entfernen + Driver 5.x |
| **B: Supabase Migration** | SEHR HOCH | PostgreSQL, Auth, Storage, Realtime — alles aus einer Hand |

**Beide Optionen erfordern kompletten Resolver-Rewrite.** Der Aufwand ist vergleichbar, aber Supabase liefert mehr Gegenwert (siehe DP-001).

---

## 6. Upgrade-Reihenfolge — Der kritische Pfad

### Phase 0: Cleanup (Woche 1)

| # | Aktion | Aufwand | Validierung |
|---|---|---|---|
| 0.1 | `styleguide/` Verzeichnis entfernen | 1 Stunde | Bestätigen dass nichts importiert wird |
| 0.2 | Root `package.json` — Workspaces einrichten | 2 Stunden | `yarn install` ohne Fehler |
| 0.3 | Kaputte Cypress-Features dokumentieren/entfernen | 1 Tag | Restliche Features laufen |

### Phase 1: Sichere Backend-Upgrades (Woche 1–2)

*Keine Breaking Changes, keine Cross-Layer-Abhängigkeiten*

| # | Aktion | Aufwand | Validierung |
|---|---|---|---|
| 1.1 | `jsonwebtoken` 8 → 9 | 2 Stunden | Backend-Tests: 71 Specs müssen grün sein |
| 1.2 | `@sentry/node` 5 → 8 | 1 Tag | Error-Tracking im Dev-Modus testen |
| 1.3 | `express` 4 → 5 | 4 Stunden | Server startet, Health-Endpoints antworten |
| 1.4 | `uuid` 9 → 11 | 1 Stunde | Backend-Tests grün |
| 1.5 | `graphql-upload` 13 → 16 | 4 Stunden | Upload-Tests grün |
| 1.6 | `subscriptions-transport-ws` entfernen | 4 Stunden | WebSocket-Subscriptions mit graphql-ws testen |
| 1.7 | `typescript` 5.8 → 5.9 | 1 Stunde | `tsc --noEmit` fehlerfrei |

**Validierung Phase 1**: `cd backend && yarn test` — alle 71 Tests grün, Coverage ≥ 92%

### Phase 2: Sichere Webapp-Upgrades (Woche 2–3)

*Unabhängig von Vue/Nuxt-Kette*

| # | Aktion | Aufwand | Validierung |
|---|---|---|---|
| 2.1 | `sass` 1.77 → 1.97 | 1 Stunde | Build + visuelle Prüfung |
| 2.2 | `date-fns` 2 → 4 | 4 Stunden | Import-Pfade ändern, Tests anpassen |
| 2.3 | `core-js` 2 → 3 | 2 Stunden | Polyfill-Importe anpassen |
| 2.4 | `cropperjs` 1 → 2 | 4 Stunden | Bild-Cropping-Funktionalität testen |
| 2.5 | ESLint 7 → 9 (Flat Config Migration) | 1–2 Tage | `yarn lint` fehlerfrei |

**Validierung Phase 2**: `cd webapp && yarn test` — alle 152 Tests grün, Coverage ≥ 83%

### Phase 3: Datenbank-Entscheidung (Woche 3–4)

Hier muss die Entscheidung fallen: **Neo4j 5 oder Supabase?**

| Option A: Neo4j 5 | Option B: Supabase |
|---|---|
| `neo4j-graphql-js` → `@neo4j/graphql` 6.x | Auth + Storage zuerst |
| `neode` → Direkt-Cypher oder OGM | PostgreSQL Schema aufbauen |
| `neo4j-driver` 4 → 5 | Resolver auf SQL umschreiben |
| Neo4j Server 4.4 → 5.x | Neo4j abschalten |
| **8–12 Wochen** | **12–16 Wochen** |

**Unabhängig von dieser Entscheidung** können Phase 1 und Phase 2 sofort starten.

### Phase 4: Frontend-Modernisierung (Woche 5–16)

*Die große Migration — erfordert sorgfältige Planung*

| # | Aktion | Aufwand | Abhängigkeit |
|---|---|---|---|
| 4.1 | `apollo-client` 2 → `@apollo/client` 3 | 2–3 Wochen | Kann VOR Nuxt 3 passieren |
| 4.2 | `graphql` 14 → 16 (Resolution entfernen) | 2 Tage | Erst nach 4.1 |
| 4.3 | `nuxt` 2 → 3 (inkl. Vite, Nitro) | 4–6 Wochen | Größte Einzelaufgabe |
| 4.4 | `vue` 2.7 → 3.5 | Inkl. in 4.3 | Kommt mit Nuxt 3 |
| 4.5 | `tiptap` 1 → 2 | 1–2 Wochen | Erst nach Vue 3 |
| 4.6 | `@storybook/vue` 7 → 10 (vue3) | 1 Woche | Erst nach Vue 3 |
| 4.7 | `mapbox-gl` 1 → `maplibre-gl` | 1 Woche | Lizenz-sauber (FOSS) |
| 4.8 | Webpack-Loader entfernen (style/css/sass/babel) | 1 Tag | Automatisch mit Nuxt 3/Vite |
| 4.9 | Jest → Vitest (optional) | 1 Woche | Nach Nuxt 3 möglich |

**Validierung Phase 4**: Webapp-Tests + E2E + manuelle Funktionsprüfung

### Phase 5: Konsolidierung (Woche 16–17)

| # | Aktion | Aufwand |
|---|---|---|
| 5.1 | Force-Resolutions in allen package.json entfernen | 1 Tag |
| 5.2 | Alle Versionen final prüfen | 1 Tag |
| 5.3 | Vollständiger Test-Durchlauf (Backend + Webapp + E2E) | 2 Tage |
| 5.4 | Performance-Baseline messen | 1 Tag |

---

## 7. Cross-Layer-Auswirkungsmatrix

### Wenn ich X ändere, bricht Y

| Änderung | Auswirkung Backend | Auswirkung Webapp | Auswirkung Cypress |
|---|---|---|---|
| `graphql` 14 → 16 (Webapp) | ❌ Kein Effekt (bereits 16) | ⚠️ Apollo Client 2 bricht | ❌ Kein Effekt |
| `apollo-client` 2 → 3 | ❌ Kein Effekt | ⚠️ Cache-API, Queries, Mutations | ⚠️ Wenn GraphQL-Aufrufe anders werden |
| `neo4j-driver` 4 → 5 | ⚠️ neo4j-graphql-js bricht | ❌ Kein Effekt | ❌ Kein Effekt |
| `vue` 2 → 3 | ❌ Kein Effekt | 🔴 ALLES ändert sich | ⚠️ DOM-Selektoren könnten brechen |
| `nuxt` 2 → 3 | ❌ Kein Effekt | 🔴 ALLES ändert sich | ⚠️ Routing könnte sich ändern |
| `express` 4 → 5 | ⚠️ Middleware-Signaturen | ❌ Kein Effekt | ⚠️ API-Verhalten prüfen |
| `jsonwebtoken` 8 → 9 | ⚠️ Algorithm-Validierung | ❌ Kein Effekt | ❌ Kein Effekt |
| ESLint 7 → 9 (Webapp) | ❌ Kein Effekt | ⚠️ Config-Format | ❌ Kein Effekt |
| `tiptap` 1 → 2 | ❌ Kein Effekt | ⚠️ Editor-Komponente | ⚠️ Post-Erstellung in E2E |

### Sichere Parallel-Arbeit

Diese Upgrades können **gleichzeitig** an verschiedenen Branches laufen:
- Phase 1 (Backend) und Phase 2 (Webapp) → **PARALLEL MÖGLICH**
- Phase 3 (Datenbank) → **UNABHÄNGIG** von Frontend
- Phase 4 (Nuxt 3) → **SEQUENTIELL** — erst nach Phase 1+2

---

## 8. Bestehende Tests — Vollständige Übersicht

### 8.1 Backend-Tests (71 Dateien)

**Kommando**: `cd backend && yarn test`  
**Framework**: Jest 30.3.0 + ts-jest  
**Coverage-Schwelle**: 92% Lines  
**Timeout**: 10.000ms

| Bereich | Dateien | Was wird getestet |
|---|---|---|
| `src/middleware/notifications/` | 6 Specs | Benachrichtigungen, Online-Status, Mentions, Posts, Follow, E-Mails |
| `src/middleware/` | 9 Specs | Validierung, Interaktionen, Berechtigungen, Slugify, OrderBy |
| `src/uploads/` | 1 Spec | S3-Service (MinIO) |
| `src/plugins/` | 1 Spec | Apollo Logger |
| `src/emails/` | 3 Specs | Registrierung, Passwort-Reset, Notification-E-Mails |
| `src/graphql/` | ~50 Specs | GraphQL-Resolver (CRUD, Auth, Moderation, Chat, Gruppen) |

**Setup**: `backend/test/setup.ts` — Apollo Test-Server mit Neo4j-Testdatenbank  
**Helpers**: `backend/test/helpers.ts` — GraphQL-Query-Execution, Context-Setup

### 8.2 Webapp-Tests (152 Dateien)

**Kommando**: `cd webapp && yarn test`  
**Framework**: Jest 29.7 + @vue/vue2-jest  
**Coverage-Schwelle**: 83% Lines

| Bereich | Dateien | Was wird getestet |
|---|---|---|
| `components/` | ~80 Specs | Modal, LoginForm, NotificationMenu, MasonryGrid, etc. |
| `store/` | 3 Specs | Posts, PinnedPosts, Categories, Auth |
| `pages/` | ~15 Specs | Settings, Static, Authentication |
| `layouts/` | ~5 Specs | Layout-Komponenten |
| `middleware/` | ~5 Specs | Route-Guards |
| `mixins/` | ~10 Specs | Shared Logic |
| `utils/` | ~15 Specs | Utility-Funktionen |

**Setup**: `webapp/test/testSetup.js`, `vueDemiSetup.js`, `registerContext.js`  
**Mocks**: `webapp/__mocks__/` — Komponenten, Assets, Mapbox

### 8.3 E2E-Tests (24 Features)

**Kommando**: `yarn cypress:run`  
**Framework**: Cypress 15.11 + Cucumber/Gherkin  
**Base-URL**: `http://localhost:3000`

| Feature | Status | Szenarien |
|---|---|---|
| Admin.DonationInfo | ✅ Aktiv | Spendeninfo-Verwaltung |
| Admin.PinPost | ✅ Aktiv | Posts pinnen |
| Admin.TagOverview | ✅ Aktiv | Tag-Verwaltung |
| Chat.Notification | ✅ Aktiv | Chat-Benachrichtigungen |
| Group.Create | ✅ Aktiv | Gruppenerstellung |
| Internationalization | ✅ Aktiv | Mehrsprachigkeit |
| Moderation.HidePost | ✅ Aktiv | Posts verstecken |
| Moderation.ReportContent | ✅ Aktiv | Inhalte melden |
| Notification.Mention | ✅ Aktiv | @-Mentions |
| PersistentLinks | ✅ Aktiv | Permanente Links |
| Post.Comment | ✅ Aktiv | Kommentare |
| Post.Create | ✅ Aktiv | Post-Erstellung |
| Post | ✅ Aktiv | Post-Ansicht |
| Post.Images | ✅ Aktiv | Bildupload |
| Search.Results | ✅ Aktiv | Suchergebnisse |
| User.Authentication | ✅ Aktiv | Login/Logout |
| UserProfile.Avatar | ✅ Aktiv | Profilbild |
| UserProfile.ChangePassword | ✅ Aktiv | Passwort ändern |
| UserProfile.NameDescriptionLocation | ✅ Aktiv | Profildaten |
| UserProfile.SocialMedia | ✅ Aktiv | Social-Media-Links |
| Search | 🔴 BROKEN | Suche |
| User.Block | 🔴 BROKEN | User blockieren |
| User.Mute | 🔴 BROKEN | User stummschalten |
| User.SettingNotifications | 🔴 BROKEN | Benachrichtigungs-Einstellungen |

**Step-Definitionen**: 137 Dateien in `cypress/support/step_definitions/`  
**E2E erfordert**: Alle Services müssen laufen (Neo4j, MinIO, Maildev, Backend, Webapp)

### 8.4 packages/ui Tests (27 Dateien)

**Kommando**: `cd packages/ui && yarn test`  
**Framework**: Vitest 4.0 + @vue/test-utils 2  
**Visual Tests**: Playwright

| Bereich | Dateien | Was wird getestet |
|---|---|---|
| Utilities | 2 Specs | cn(), Tailwind Preset |
| Components | ~20 Specs | OsSpinner, OsNumber, OsMenu, OsModal, OsIcon |
| Visual | ~5 Specs | Playwright Snapshot-Vergleiche |
| Plugin | 1 Spec | Vue-Plugin-Installation |

---

## 9. Validierungsstrategie — Wie prüfen wir, ob alles noch geht?

### 9.1 Dreistufiges Validierungsmodell

```
Stufe 1: STATISCH (ohne System hochzufahren)
├─ Dependency-Resolution: yarn install ohne Fehler
├─ TypeScript-Kompilierung: tsc --noEmit
├─ Lint: eslint (pro Layer)
└─ Python-Simulationsskript (siehe Abschnitt 10)

Stufe 2: UNIT-TESTS (ohne externe Services)
├─ Backend: jest --runInBand (71 Tests, 92% Coverage)
├─ Webapp: jest --coverage (152 Tests, 83% Coverage)
└─ UI: vitest run (27 Tests)
     Gesamt: 250 Tests in ~5 Minuten

Stufe 3: INTEGRATION + E2E (mit Docker Services)
├─ docker-compose.test.yml hochfahren
├─ Backend-Integration: Jest mit echtem Neo4j
├─ Cypress: 20 aktive Feature-Files
└─ Manuell: Kernfunktionen durchklicken
```

### 9.2 Validierung pro Upgrade-Schritt

**Regel**: Nach JEDEM Paket-Upgrade sofort die Stufe-1- und Stufe-2-Tests fahren. Nicht mehrere Pakete gleichzeitig upgraden.

```bash
# Workflow pro Paket-Upgrade
git checkout -b upgrade/PAKETNAME-VERSION
yarn upgrade PAKETNAME@VERSION
yarn install                          # Stufe 1a: Resolution
yarn tsc --noEmit                     # Stufe 1b: TypeScript (Backend)
yarn lint                             # Stufe 1c: Lint
yarn test                             # Stufe 2: Tests
# Wenn alles grün → Commit
# Wenn rot → Fix oder Revert
```

### 9.3 Python-Simulationsskript

Siehe **Abschnitt 10** und die Datei `WORKING/TOOLS/upgrade-simulator.py`.

---

## 10. Python-Simulationsskript — Konzept

### Was kann simuliert werden (ohne System)?

| Prüfung | Möglich? | Wie |
|---|---|---|
| **Versionskompatibilität** | ✅ Ja | npm-Registry-Abfragen (peerDependencies, engines) |
| **Bekannte Konflikte** | ✅ Ja | Regelbasierte Prüfung aus unserer Abhängigkeitskette |
| **Semantische Versionierung** | ✅ Ja | semver-Parsing, Breaking-Change-Erkennung |
| **Peer-Dependency-Verletzungen** | ✅ Ja | Cross-Check aller peerDependencies |
| **Resolution-Konflikte voraussagen** | ✅ Ja | Dependency-Tree-Simulation |
| **Tatsächliche Code-Kompatibilität** | ❌ Nein | Dafür braucht man die echten Tests |
| **Runtime-Fehler** | ❌ Nein | Dafür braucht man die Ausführungsumgebung |

### Funktionsumfang des Skripts

1. **Alle package.json einlesen** (Backend, Webapp, UI, Root, Styleguide)
2. **Aktuelle Versionen von npm-Registry abfragen** (live oder gecacht)
3. **Peer-Dependency-Ketten prüfen** (z.B. Apollo Client ↔ graphql Version)
4. **Bekannte Blockaden erkennen** (unsere manuell gepflegten Regeln)
5. **Upgrade-Vorschläge generieren** mit Risikoklassifizierung
6. **Simulierter Upgrade-Durchlauf**: Paket für Paket upgraden und prüfen ob die restlichen peerDependencies noch erfüllt sind
7. **HTML-Report generieren** mit Ampelfarben

### Grenzen der Simulation

**Was das Skript NICHT kann:**
- Garantieren, dass Code nach Upgrade funktioniert (dafür Tests nötig)
- API-Breaking-Changes erkennen (nur Versionsebene, nicht Code-Ebene)
- Runtime-Kompatibilität prüfen (Node.js Version, OS etc.)

**Was das Skript KANN:**
- **90% der Upgrade-Planungsarbeit automatisieren** — welche Pakete können rauf, welche blockieren
- **Regressionsprüfung** — nach einem Upgrade simulieren ob der Rest noch passt
- **Dry-Run eines Upgrade-Plans** — Phase 1 durchspielen und Konflikte voraussagen

---

## 11. Risikobewertung

### Hohe Risiken

| Risiko | Eintrittswahrscheinlichkeit | Auswirkung | Mitigation |
|---|---|---|---|
| Nuxt 2 → 3 bricht alles | HOCH | KRITISCH | Separater Branch, inkrementelle Migration, Parallel-Betrieb |
| Neo4j-Layer hat versteckte Abhängigkeiten | MITTEL | HOCH | Resolver-Tests als Sicherheitsnetz (71 Backend-Tests) |
| Apollo Client 3 ändert Caching-Verhalten | HOCH | MITTEL | Cache-Tests schreiben, lokale QA |
| tiptap 2 bricht Editor-Funktionalität | MITTEL | HOCH | Feature-Branch, UX-Testing |
| Cypress-Tests brechen nach DOM-Änderungen (Vue 3) | HOCH | MITTEL | Selektoren mit data-test-Attributen |

### Niedrige Risiken

| Risiko | Eintrittswahrscheinlichkeit | Auswirkung | Mitigation |
|---|---|---|---|
| Phase-1-Upgrades (Backend) verursachen Regressionen | GERING | GERING | 92% Test-Coverage fängt das ab |
| Phase-2-Upgrades (Webapp-Sofort) brechen Build | GERING | GERING | Minor-Upgrades, gut getestet |
| ESLint-Migration bricht Code | GERING | GERING | Nur Config-Änderung, kein Code |

---

## 12. Zeitplan — Zusammenfassung

| Phase | Was | Dauer | Team | Voraussetzung |
|---|---|---|---|---|
| **Phase 0** | Cleanup (Styleguide löschen, Workspaces) | 1–2 Tage | 1 Dev | — |
| **Phase 1** | Backend sichere Upgrades | 1 Woche | 1 Dev | — |
| **Phase 2** | Webapp sichere Upgrades | 1 Woche | 1 Dev | — |
| **Phase 3** | DB-Entscheidung + Start | 2–4 Wochen | 1 Dev | Phase 1 abgeschlossen |
| **Phase 4** | Frontend-Modernisierung (Nuxt 3) | 6–10 Wochen | 1–2 Dev | Phase 1+2 abgeschlossen |
| **Phase 5** | Konsolidierung | 1 Woche | 1 Dev | Alles abgeschlossen |
| **Gesamt** | — | **12–18 Wochen** | — | — |

**Hinweis**: Phase 1 + Phase 2 können **parallel** laufen. Phase 3 und Phase 4 können **parallel** laufen (DB-Team + Frontend-Team).

---

## 13. Offene Entscheidungen

- [ ] **Styleguide löschen** — Bestätigung, dass nichts mehr darauf zugreift
- [ ] **mapbox-gl vs maplibre-gl** — Lizenz-Entscheidung (proprietär vs FOSS)
- [ ] **Neo4j 5 vs Supabase** — Muss vor Phase 3 entschieden werden (siehe DP-001)
- [ ] **Jest vs Vitest (Webapp)** — Bei Nuxt 3 auf Vitest wechseln oder Jest 30 behalten?
- [ ] **Nuxt 3 Bridge vs Direct** — Nuxt Bridge als Zwischenschritt oder direkt auf Nuxt 3?
- [ ] **Parallel oder sequentiell?** — DB-Migration und Frontend-Migration gleichzeitig?

---

## 14. Nächste Schritte

1. **Python-Simulationsskript erstellen** → `WORKING/TOOLS/upgrade-simulator.py`
2. **Phase 0 umsetzen** — Styleguide-Abhängigkeit prüfen und löschen
3. **Phase 1 starten** — `jsonwebtoken` 8 → 9 als erstes Upgrade (niedrigstes Risiko)
4. **Datenbank-Entscheidung treffen** — Team-Diskussion auf Basis von DP-001
5. **Nuxt 3 Migrationsstrategie** — Eigenes Workpaper mit Komponenten-für-Komponenten-Plan

---

## 15. Zusammenfassung

> **Der Upgrade-Plan ist in 5 Phasen gegliedert: Cleanup → Backend → Webapp-Sofort → Datenbank → Frontend-Modernisierung.**
>
> Phase 1 und 2 sind risikoarm und können sofort starten. Die beiden harten Blöcke — Datenbank (Neo4j-Kette) und Frontend (Vue/Nuxt-Kette) — erfordern jeweils eigene strategische Entscheidungen.
>
> Das Python-Simulationsskript automatisiert die Versionskompatibilitätsprüfung und reduziert das Risiko von Trial-and-Error bei Upgrades.
>
> **Gesamtaufwand: 12–18 Wochen**, davon 4–6 Wochen allein für Nuxt 2 → 3.
