# WP-002 — Backend Deep Analysis

**Created**: 2026-03-27 | **Status**: Active | **Author**: GitHub Copilot (AAMS Bootstrap)

---

## 1. Overview

The backend is a **TypeScript Node.js** server running **Apollo Server 4** with **Express**, connecting to **Neo4j 4.4** via the official driver and **Neode ORM**. Schema is auto-augmented by `neo4j-graphql-js`.

| Aspect | Detail |
|---|---|
| Entry point | `src/index.ts` → `createServer()` |
| Runtime | Node.js ≥20.12.1 |
| Language | TypeScript 5.8, target ES2016, module CommonJS |
| Framework | Express + Apollo Server 4 |
| GraphQL | `graphql` 16.13, `neo4j-graphql-js` 2.11.5 |
| Database | Neo4j via `neo4j-driver` 4.4.11 + `neode` 0.4.9 |
| Auth | JWT (`jsonwebtoken` 8.5.1) |
| PubSub | Redis (`ioredis` 5.10) or in-memory fallback |
| Storage | S3 via `@aws-sdk/client-s3` 3.1005 |
| Email | Nodemailer 8 + `email-templates` 13 + Pug templates |
| Testing | Jest 30 + ts-jest 29 |
| Build | `tsc` + `tsc-alias` |

---

## 2. Server Architecture

```
src/index.ts
  └── createServer()  [src/server.ts]
        ├── Express app
        ├── helmet (security headers)
        ├── bodyParser (10mb limit)
        ├── graphqlUploadExpress (file uploads)
        ├── ApolloServer
        │   ├── schema = middleware(makeAugmentedSchema(...))
        │   ├── csrfPrevention: false (TODO — Nuxt 2 compatibility)
        │   └── plugins: [DrainHttpServer, WS cleanup, custom]
        ├── WebSocket: graphql-ws (modern protocol)
        ├── WebSocket: subscriptions-transport-ws (legacy)
        └── HTTP proxy: S3 (if PROXY_S3 configured)
```

### Dual WebSocket Protocol

The server maintains **two** WebSocket servers for subscription compatibility:
- **graphql-ws** (subprotocol: `graphql-transport-ws`) — modern clients
- **subscriptions-transport-ws** (subprotocol: `graphql-ws`) — legacy clients (Nuxt 2 / Apollo Client 2)

Upgrade requests are routed by `Sec-WebSocket-Protocol` header.

**Assessment**: The legacy protocol exists solely for the Nuxt 2 webapp. A Nuxt 3 migration would eliminate this dual-stack requirement.

---

## 3. GraphQL Schema Architecture

```
src/graphql/
├── schema.ts          ← makeAugmentedSchema (neo4j-graphql-js)
├── types/             ← .gql type definitions (auto-loaded)
│   ├── directive/     ← Neo4j-specific directives
│   ├── enum/          ← 11 enums (UserRole, PostType, GroupType, ...)
│   ├── scalar/        ← Upload scalar
│   └── type/          ← 25 entity types (User, Post, Group, Comment, ...)
├── resolvers/         ← 40+ resolver files (auto-loaded by filename)
│   ├── attachments/   
│   ├── embeds/
│   ├── helpers/
│   ├── images/
│   ├── searches/
│   └── users/
└── queries/           ← .gql query/mutation definitions
    ├── auth/
    ├── badges/
    ├── comments/
    ├── donations/
    ├── emotions/
    ├── groups/
    ├── interactions/
    ├── invites/
    ├── messaging/
    ├── moderation/
    ├── notifications/
    ├── posts/
    └── users/
```

### Auto-Loading Pattern

- **Types**: `loadFilesSync` scans `types/**/*.gql` → `mergeTypeDefs`
- **Resolvers**: `loadFilesSync` scans `resolvers/!(*.spec|index).(ts|js)` → `mergeResolvers`
- **Schema**: `makeAugmentedSchema` from `neo4j-graphql-js` augments types with auto-generated CRUD queries

### Critical Dependency: `neo4j-graphql-js` 2.11.5

This package is **deprecated** (last release 2021). It auto-generates:
- Query resolvers for Neo4j types
- Filter/sort arguments
- Cypher directives (`@cypher`, `@relation`)

**Risk**: No updates, no Neo4j 5.x support, locked to graphql 16 via resolution overrides. The successor `@neo4j/graphql` has a different API.

---

## 4. Middleware Pipeline

The backend uses `graphql-middleware` to compose 16 middleware layers in strict order:

| # | Name | Purpose |
|---|---|---|
| 1 | sentry | Error tracking (Sentry SDK) |
| 2 | permissions | Authorization rules (graphql-shield) |
| 3 | xss | HTML sanitization (sanitize-html) |
| 4 | validation | Input validation |
| 5 | userInteractions | User activity tracking |
| 6 | sluggify | URL-safe slug generation |
| 7 | languages | Language detection (languagedetect) |
| 8 | excerpt | Text excerpt generation |
| 9 | login | Authentication handling |
| 10 | notifications | Notification generation (mentions, follows, groups) |
| 11 | hashtags | Hashtag extraction (#tag) |
| 12 | softDelete | Soft-delete support |
| 13 | includedFields | Field selection optimization |
| 14 | orderBy | Sort/order middleware |
| 15 | chatMiddleware | Chat/messaging handler |
| 16 | categories | Category management |

Additionally: **branding middlewares** run as a function call before the middleware chain (not a graphql middleware).

Middleware can be disabled via `DISABLED_MIDDLEWARES` env var (comma-separated).

---

## 5. Context System

The GraphQL context is constructed per-request:

```typescript
{
  database: { driver, neode, query(), write() },
  driver,        // Neo4j driver (direct)
  neode,         // Neode ORM instance
  pubsub,        // Redis PubSub or in-memory PubSub
  logger,        // tslog instance
  user,          // Decoded JWT user or null
  req,           // Express request
  cypherParams: {
    currentUserId,    // For Cypher query injection
    languageDefault   // Uppercase language code
  },
  config         // Full CONFIG object
}
```

---

## 6. Database Layer

### Neo4j Driver

- **Connection**: `neo4j-driver` 4.4.11 via `bolt://` protocol
- **ORM**: `neode` 0.4.9 (schema-based Node.js ORM for Neo4j)
- **Singleton**: Both driver and Neode instance are cached (singleton pattern)

### 18 Neode Models

```
Badge, Category, Comment, Donations, EmailAddress, File, Group, Image,
InviteCode, Location, Migration, Post, Report, SocialMedia, Tag,
UnverifiedEmailAddress, User, (index.ts exports all)
```

Note: `Post` is extended to `Article` via `neodeInstance.extend('Post', 'Article', {})`

### Database Operations

| Script | Command | Purpose |
|---|---|---|
| `db:reset` | `tsx src/db/reset.ts` | Clear all data |
| `db:seed` | `tsx src/db/seed.ts` | Seed test data |
| `db:migrate` | `migrate` CLI | Run migrations |
| `db:data:admin` | `tsx src/db/admin.ts` | Create admin user |
| `db:data:categories` | `tsx src/db/categories.ts` | Seed categories |
| `db:data:branding` | `tsx src/db/data-branding.ts` | Seed branding data |

### Migration System

Uses `migrate` package with TypeScript compiler. Migrations stored in `src/db/migrations/` with timestamp-based naming (`yyyymmddHHmmss`).

---

## 7. Authentication (JWT)

### Token Format

```
Header: Bearer <token>
Payload: { id, name, slug, sub: user.id }
Issued by: GRAPHQL_URI
Audience: CLIENT_URI
Expiry: 2 years (default)
Secret: JWT_SECRET env var
```

### Decode Flow

1. Extract token from `Authorization` header
2. Verify with `JWT_SECRET`
3. Match `sub` claim to Neo4j User node
4. Update `lastActiveAt` timestamp
5. Return `{ id, slug, name, role, disabled }` + token

---

## 8. File Storage (S3)

- **Client**: `@aws-sdk/client-s3` v3 (singleton, cached)
- **Upload**: `@aws-sdk/lib-storage` (multipart)
- **ACL**: `public-read` by default
- **Cache**: `public, max-age=604800` (1 week)
- **Dev**: MinIO localhost:9000
- **Prod**: Any S3-compatible storage

Image processing via **Imagor** (separate service, HMAC-signed URLs).

---

## 9. Email System

- **Transport**: Nodemailer (SMTP pool, DKIM support)
- **Templates**: Pug-based via `email-templates`
- **Config**: SMTP host/port/credentials from env
- **Features**: Registration, password reset, notifications, invitations
- **Dev**: Maildev (port 1080 web UI, port 1025 SMTP)

---

## 10. Configuration

### Required Environment Variables (fatal if missing)

```
EMAIL_DEFAULT_SENDER, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
AWS_ENDPOINT, AWS_REGION, AWS_BUCKET, IMAGOR_PUBLIC_URL,
IMAGOR_SECRET, MAPBOX_TOKEN, JWT_SECRET
```

### Key Options

| Variable | Default | Purpose |
|---|---|---|
| `PUBLIC_REGISTRATION` | false | Allow public signup |
| `INVITE_REGISTRATION` | true | Allow invite-only signup |
| `CATEGORIES_ACTIVE` | false | Enable content categories |
| `MAX_PINNED_POSTS` | 1 | Pinned posts per context |
| `LANGUAGE_DEFAULT` | en | Default language |

---

## 11. Critical Dependencies Assessment

| Package | Version | Status | Risk |
|---|---|---|---|
| `neo4j-graphql-js` | 2.11.5 | **DEPRECATED** (2021) | HIGH — no Neo4j 5 support, no maintenance |
| `neode` | 0.4.9 | **UNMAINTAINED** | HIGH — last release 2020 |
| `neo4j-driver` | 4.4.11 | **EOL** | MEDIUM — v5.x available, breaking changes |
| `jsonwebtoken` | 8.5.1 | **OLD** | LOW — works but v9 available |
| `subscriptions-transport-ws` | 0.11.0 | **DEPRECATED** | LOW — only for legacy clients |
| `graphql-upload` | 13.0.0 | Locked via resolution | LOW — resolution override needed |
| `@sentry/node` | 5.30.0 | **VERY OLD** | MEDIUM — v8.x available, API changed |
| `node-fetch` | 2.7.0 | v2 legacy | LOW — built-in fetch available in Node 20+ |
| `express` | 4.22.1 | Stable | LOW — Express 5 available |
