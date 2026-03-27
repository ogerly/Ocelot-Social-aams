# WP-003 — Cypress/E2E Testing Analysis

**Created**: 2026-03-27 | **Status**: Active | **Author**: GitHub Copilot (AAMS Bootstrap)

---

## 1. Overview

End-to-end testing uses **Cypress 15.11** with **Cucumber/Gherkin** BDD via `@badeball/cypress-cucumber-preprocessor`. Tests are written as `.feature` files with step definitions in JavaScript.

| Aspect | Detail |
|---|---|
| Framework | Cypress 15.11.0 |
| BDD Layer | @badeball/cypress-cucumber-preprocessor 24.0.1 |
| Step Language | @cucumber/cucumber 12.7.0 |
| Base URL | http://localhost:3000 |
| Viewport | 1290×720 |
| Timeout | 60s command, 180s page load |
| Retries | 0 (no retries) |
| Video | Disabled |
| Browser | Electron (default) |

---

## 2. Feature Coverage

### Active Features (20)

| Feature | Domain |
|---|---|
| Admin.DonationInfo | Admin panel — donation settings |
| Admin.PinPost | Admin panel — pin posts |
| Admin.TagOverview | Admin panel — tag management |
| Chat.Notification | Chat messaging notifications |
| Group.Create | Group management |
| Internationalization | i18n language switching |
| Moderation.HidePost | Content moderation — hide |
| Moderation.ReportContent | Content moderation — report |
| Notification.Mention | @mention notifications |
| PersistentLinks | URL persistence |
| Post.Comment | Commenting on posts |
| Post.Create | Creating new posts |
| Post | Post CRUD operations |
| Post.Images | Image upload in posts |
| Search.Results | Search result display |
| User.Authentication | Login/logout/session |
| UserProfile.Avatar | Avatar upload/change |
| UserProfile.ChangePassword | Password change flow |
| UserProfile.NameDescriptionLocation | Profile editing |
| UserProfile.SocialMedia | Social media links |

### Broken Features (4)

| Feature | Status |
|---|---|
| Search.feature.broken | Renamed with `.broken` suffix |
| User.Block.feature.broken | Blocking functionality broken |
| User.Mute.feature.broken | Muting functionality broken |
| User.SettingNotifications.feature.broken | Notification settings broken |

**Assessment**: 17% of feature files are marked broken. These represent functionality that either regressed or was never fully tested. The `.broken` suffix convention prevents Cypress from finding them.

---

## 3. Test Infrastructure

### Webpack Preprocessor

Cucumber features are compiled via Webpack with:
- `@badeball/cypress-cucumber-preprocessor/webpack` loader
- `node-polyfill-webpack-plugin` (Buffer, process polyfills)
- Development mode with `eval-source-map`

### Test Data (Factories)

```javascript
// cypress/support/factories.js
import Factory from '../../backend/build/src/db/factories'
import { getNeode } from '../../backend/build/src/db/neo4j'
```

**Critical coupling**: E2E tests directly import from `backend/build/`. This means:
1. Backend must be built (`yarn build`) before E2E tests can run
2. Changes to backend data models require rebuilding
3. Tests bypass the API layer for data setup

### Database Reset

```javascript
beforeEach(() => cy.then(() => 
  neodeInstance.writeCypher('MATCH (everything) DETACH DELETE everything;')
))
```

**Every test clears the entire database**. This ensures clean state but is slow.

### Custom Commands

| Command | Purpose |
|---|---|
| `cy.logout()` | Navigate to /logout |
| `cy.authenticateAs({ email, password })` | Get GraphQL client with auth |
| `cy.mutate(mutation, variables)` | Execute GraphQL mutation |
| `cy.neode()` | Access Neode ORM instance |
| `cy.factory()` | Access Factory builder |
| `cy.build(name, attrs, options)` | Build test data via factory |

### Fixtures

| File | Content |
|---|---|
| `users.json` | admin/moderator/user credentials (password: `1234`) |
| `example.json` | Base Cypress fixture |
| `humanconnection.png` | Test image |
| `onourjourney.png` | Test image |

---

## 4. Step Definition Organization

137 step definition files organized by feature in `cypress/support/step_definitions/`:

```
step_definitions/
├── common/             ← Shared steps (login, navigation)
├── Admin.DonationInfo/
├── Admin.PinPost/
├── Chat.Notification/
├── Group.Create/
├── Internationalization/
├── Moderation.HidePost/
├── Moderation.ReportContent/
├── Notification.Mention/
├── Post/
├── Post.Comment/
├── Post.Create/
├── Post.Images/
├── Search/
├── Search.Results/
├── User.Authentication/
├── User.Block/
├── User.Mute/
├── User.SettingNotifications/
├── UserProfile.Avatar/
├── UserProfile.ChangePassword/
├── UserProfile.NameDescriptionLocation/
└── UserProfile.SocialMedia/
```

---

## 5. Parallel Execution

`parallel-features.sh` distributes feature files across parallel jobs:
- Accepts `CUR_JOB` and `MAX_JOBS` arguments
- Divides features evenly with remainder distributed to first jobs
- Outputs comma-separated feature file list

---

## 6. Reporting

`create-cucumber-html-report.js` generates HTML test reports from Cucumber JSON output via `multiple-cucumber-html-reporter`.

---

## 7. Risks & Technical Debt

| Issue | Severity | Detail |
|---|---|---|
| 4 broken features | **HIGH** | 17% of E2E tests non-functional |
| Direct backend import | **MEDIUM** | Tight coupling to build artifacts |
| Full DB wipe per test | **MEDIUM** | Performance bottleneck |
| No retry strategy | **LOW** | Retries disabled (flaky tests fail hard) |
| Legacy command pattern | **LOW** | `commands.js` uses deprecated patterns |
| `supportFile: false` | **INFO** | Support loaded through preprocessor, not Cypress native |
