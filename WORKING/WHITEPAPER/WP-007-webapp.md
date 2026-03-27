# WP-007 — Webapp (Frontend) Analysis

**Created**: 2026-03-27 | **Status**: Active | **Author**: GitHub Copilot (AAMS Bootstrap)

---

## 1. Overview

| Aspect | Detail |
|---|---|
| Framework | Nuxt.js 2.18.1 (Vue 2.7.16) |
| Mode | Universal (SSR, `mode: 'universal'`) |
| Build | Webpack 4 (via Nuxt), `modern: 'server'` in production |
| State | Vuex (7 modules) |
| API | Apollo Client 2.6 (GraphQL + WebSocket subscriptions) |
| i18n | 11 locales (EN, DE, NL, FR, IT, ES, PT, PL, RU, SQ, UK) |
| PWA | Enabled via `@nuxtjs/pwa` |
| Monitoring | Sentry via `@nuxtjs/sentry` |
| UI Library | `@ocelot-social/ui` 0.0.1 (local link) |

---

## 2. Architecture

### Request Flow

```
Browser → Nuxt SSR (Node.js) → /api proxy → Backend (Apollo Server)
                               → /activitypub proxy → Backend
                               → /.well-known/webfinger proxy → Backend
```

### SSR + Client Hydration

1. Server: `nuxtServerInit` → dispatches `auth/init` (reads JWT from cookie)
2. Server: Middleware chain (`authenticated` → `termsAndConditions`)
3. Server: Page `asyncData` + `fetch` hooks (GraphQL queries via Apollo)
4. Client: Hydration → client-only plugins load (maps, chat, tooltips, etc.)

### Proxy Configuration

| Path | Target | Headers |
|---|---|---|
| `/.well-known/webfinger` | `GRAPHQL_URI` | Accept: application/json, X-UI-Request, X-API-TOKEN |
| `/activitypub` | `GRAPHQL_URI` | Same |
| `/api` | `GRAPHQL_URI` (path rewritten) | Same |

---

## 3. Route Structure (44 routes)

### Public Pages

| Route | Page |
|---|---|
| `/login` | Login |
| `/registration` | Registration |
| `/password-reset/request` | Password reset flow |
| `/password-reset/enter-nonce` | Password reset flow |
| `/password-reset/change-password` | Password reset flow |
| `/:static` | Footer pages (data-privacy, imprint, terms, etc.) |

### Authenticated Pages

| Route | Page |
|---|---|
| `/` | Home feed (filterable, keep-alive) |
| `/map` | Map view (Mapbox GL) |
| `/search/search-results` | Search results |
| `/post/create/:type` | Create post |
| `/post/edit/:id` | Edit post |
| `/post/:id/:slug` | Post detail view |
| `/profile/:id/:slug` | User profile |
| `/groups/:id` | Group detail |
| `/moderation` | Moderation dashboard |
| `/terms-and-conditions-confirm` | T&C acceptance |

### Settings (14 sub-pages)

`/settings/` — badges, blocked-users, data-download, delete-account, embeds, invites, languages, muted-users, my-organizations, my-social-media, notifications, privacy, security, my-email-address (3 sub-pages)

### Admin (9 pages)

`/admin/` — categories, donations, hashtags, invite, notifications, organizations, pages, settings

---

## 4. Layouts (5)

| Layout | Use Case |
|---|---|
| `default` | Main layout — HeaderMenu, content, PageFooter, Chat panel |
| `basic` | Auth pages — simplified header (Logo + LocaleSwitch + LoginButton) |
| `blank` | Minimal — just content with padding |
| `no-header` | No header, sticky PageFooter |
| `error` | Error display (403/404/500/503 with image + message) |

---

## 5. Vuex Store (7 modules)

| Module | State | Key Actions |
|---|---|---|
| **Root** | — | `nuxtServerInit` → `auth/init` |
| **auth** | `user`, `token`, `pending` | `init`, `login`, `logout`, `check`, `fetchCurrentUser`. Getters: `isLoggedIn`, `isAdmin`, `isModerator`, `termsAndConditionsAgreed` |
| **categories** | `categories[]` | Fetch from GraphQL, transform to objects |
| **chat** | `showChat`, `roomID`, `unreadRoomCount` | Toggle chat panel, set active room |
| **posts** | `filter`, `order`, `postType` | Filter by: followed, groups, categories, languages, emotions, post types (Event). Order: createdAt/updatedAt |
| **pinnedPosts** | `maxPinnedPosts`, `pinnedPostsCount` | Fetch from `PostsPinnedCounts` query |
| **search** | `searchValue` | Simple search term storage |

---

## 6. GraphQL Operations (37 files)

### Query/Mutation Files (24)

| Domain | Operations |
|---|---|
| **Posts** | PostQuery, PostMutations, PostsPinnedCounts |
| **Comments** | CommentQuery, CommentMutations |
| **Users** | User (currentUser, profiles), Registration |
| **Groups** | groups (CRUD, membership) |
| **Chat** | Messages, Rooms |
| **Search** | Search (full-text) |
| **Categories** | CategoryQuery, SaveCategories |
| **Moderation** | Moderation (reports, decisions) |
| **Admin** | Badges, Roles, Statistics |
| **Settings** | BlockedUsers, MutedUsers, MutedGroups |
| **Other** | Donations, EmailAddress, EmbedQuery, InviteCode, inviteCodes, location, SocialMedia, updateOnlineStatus |

### Fragments (10)

`badges`, `comment`, `group`, `imageUrls`, `location`, `post`, `postCounts`, `tagsCategoriesAndPinned`, `user`, `userCounts`

---

## 7. Middleware (4)

| Middleware | Scope | Logic |
|---|---|---|
| `authenticated` | Global (router) | Skip public pages; dispatch `auth/check`; redirect to `/login` with return path if unauthenticated |
| `termsAndConditions` | Global (router) | Skip public pages + T&C page; check `termsAndConditionsAgreed`; redirect to `/terms-and-conditions-confirm` |
| `isAdmin` | Page-level | Return 403 if not admin role |
| `isModerator` | Page-level | Return 403 if not moderator role |

---

## 8. Plugins (14)

| Plugin | SSR | Purpose |
|---|---|---|
| `i18n` | ✅ | vue-i18n setup |
| `axios` | ❌ | Axios configuration |
| `keep-alive` | ❌ | Page keep-alive management |
| `vue-directives` | ❌ | Custom Vue directives |
| `v-tooltip` | ❌ | Tooltip directive |
| `izi-toast` | ❌ | Toast notifications |
| `vue-filters` | ✅ | Vue filters (both modes) |
| `vue-infinite-loading` | ❌ | Infinite scroll |
| `vue-observe-visibility` | ❌ | IntersectionObserver |
| `v-mapbox` | ❌ | Mapbox GL maps |
| `vue-advanced-chat` | ❌ | Chat UI component |
| `onlineStatus` | ❌ | Online/offline detection |
| `apollo-config` | — | Apollo client: InMemoryCache, WS endpoint, cookie auth |
| Fragment types JSON | — | GraphQL interface/union type resolution |

---

## 9. Components (67 top-level)

### By Domain

| Domain | Components |
|---|---|
| **Content** | ContributionForm, Editor, Embed, CommentCard, CommentForm, CommentList |
| **Post** | PostTeaser, EmotionButton, ShoutButton, ContentMenu, Hashtag, HashtagsFilter |
| **User** | AvatarMenu, UserTeaser, Badges, BadgeSelection, LoginForm, LoginButton |
| **Navigation** | HeaderMenu, FilterMenu, DropdownFilter, NotificationMenu, PageFooter, LocaleSwitch, Logo |
| **Layout** | MasonryGrid, LayoutToggle, ComponentSlider, Modal, Dropdown, Empty, Ribbon |
| **Chat** | Chat, ChatNotificationMenu |
| **Group** | Group |
| **Moderation** | NotificationsTable |
| **Admin** | DonationInfo |
| **Forms** | OcelotInput, OcelotSelect, Select, Password, ShowPassword, EnterNonce, CategoriesSelect |
| **Media** | Uploader, ResponsiveImage, ProgressBar |
| **Account** | Registration, PasswordReset, DeleteData, InviteButton |
| **Map** | Map, LocationInfo, LocationTeaser |
| **Social** | SocialMedia, ObserveButton |
| **Utility** | DateTime, DateTimeRange, ActionButton, CustomButton, `generic/`, `utils/`, `features/`, `_new/` |

---

## 10. Mixins (11)

| Mixin | Purpose |
|---|---|
| `formValidation` | Form field validation helpers |
| `getCategoriesMixin` | Category data loading |
| `internalPageMixins` | Static/internal page rendering |
| `localeUpdate` | Locale switching handler |
| `mobile` | Mobile device/breakpoint detection |
| `persistentLinks` | Link persistence logic |
| `pinnedPosts` | Pinned posts management |
| `postListActions` | Post list interaction helpers |
| `scrollToAnchor` | Scroll-to-anchor behavior |
| `seo` | SEO/meta tag generation |
| `sortCategoriesMixin` | Category sorting logic |

---

## 11. Internationalization

### 11 Active Locales

EN, DE, NL, FR, IT, ES, PT, PL, RU, SQ, UK

### Static HTML Pages (per locale)

Each locale can have HTML internal pages: code-of-conduct, data-privacy, donate, FAQ, imprint, organization, support, terms-and-conditions. Currently only `en/` and `de/` have full HTML sets.

---

## 12. Branding System

The webapp supports white-label deployments through a branding override system:

| Constant | Override |
|---|---|
| `metadata.js` | Application name, description, theme color, cookie name |
| `manifest.js` | PWA manifest from metadata |
| `links.js` | Footer links, landing page |
| `logos.js` → `logosBranded.js` | Logo overrides |
| `login.js` → `loginBranded.js` | Login page customization |
| `registration.js` → `registrationBranded.js` | Registration customization |
| `headerMenu.js` → `headerMenuBranded.js` | Header menu customization |
| SCSS branding imports | Color overrides, theme variables |
| Icon registry | SVG icon overrides via `~/assets/_new/icons/svgs/` |

Pattern: `constants/xxx.js` provides defaults, `constants/xxxBranded.js` overrides for branding.

---

## 13. Configuration (Environment Variables)

| Group | Variables |
|---|---|
| **Server** | `GRAPHQL_URI`, `BACKEND_TOKEN`, `WEBSOCKETS_URI` |
| **Sentry** | `SENTRY_DSN_WEBAPP`, `COMMIT` |
| **Features** | `PUBLIC_REGISTRATION`, `INVITE_REGISTRATION`, `BADGES_ENABLED`, `ASK_FOR_REAL_NAME`, `REQUIRE_LOCATION` |
| **UI** | `MAPBOX_TOKEN`, `LANGUAGE_DEFAULT`, `LANGUAGE_FALLBACK`, `NETWORK_NAME` |
| **Security** | `COOKIE_EXPIRE_TIME` (730 days), `COOKIE_HTTPS_ONLY` |
| **Limits** | `MAX_GROUP_PINNED_POSTS` (1), `INVITE_LINK_LIMIT` (7) |

---

## 14. Key Architectural Patterns

| Pattern | Usage |
|---|---|
| **Apollo Client** for all data | No REST calls, pure GraphQL + subscriptions (WS) |
| **Mixins** over Composition API | 11 mixins; Vue 2.7 Composition API available but unused |
| **Vuex** for global state | Auth, chat, filters, search — not per-entity caching (Apollo handles that) |
| **SSR** for SEO/first paint | `asyncData`/`fetch` hooks for server-side GraphQL |
| **Router middleware** for auth | Two global middleware (auth + T&C), two page-level (admin/mod) |
| **Branding override system** | Constants + SCSS + icons layered for white-label |
| **Proxy** for API calls | Frontend never exposes backend URL; `/api` proxied via Nuxt |

---

## 15. Risk Assessment

| Risk | Severity | Detail |
|---|---|---|
| Vue 2 / Nuxt 2 EOL | **CRITICAL** | No security patches; Vue 3 + Nuxt 3 migration required |
| Apollo Client 2 | **HIGH** | v2 is unmaintained; v3+ has breaking API changes |
| Webpack 4 (via Nuxt 2) | **HIGH** | Slow builds, missing modern features |
| Mixin-heavy architecture | **MEDIUM** | 11 mixins make composition opaque; blocks Composition API adoption |
| `subscriptions-transport-ws` | **MEDIUM** | Deprecated in favor of `graphql-ws` |
| 67 top-level components | **LOW** | Large surface area but organized by domain |
| Incomplete locale coverage | **LOW** | Only EN/DE have full HTML pages |
