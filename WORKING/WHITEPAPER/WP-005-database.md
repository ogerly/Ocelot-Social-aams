# WP-005 — Neo4j Database Analysis

**Created**: 2026-03-27 | **Status**: Active | **Author**: GitHub Copilot (AAMS Bootstrap)

---

## 1. Overview

The platform uses **Neo4j 4.4 Community** as its sole persistent data store. All data — users, posts, comments, groups, messages, notifications — lives in a single Neo4j graph database.

| Aspect | Detail |
|---|---|
| Neo4j Version | 4.4 Community (Dockerfile: `amd64/neo4j:4.4-community`) |
| Protocol | Bolt (`bolt://neo4j:7687`) |
| Auth | Disabled (`NEO4J_AUTH=none`) |
| APOC | 4.4.0.17 (installed via Dockerfile) |
| Driver | `neo4j-driver` 4.4.11 (Node.js) |
| ORM | `neode` 0.4.9 |
| Schema Generator | `neo4j-graphql-js` 2.11.5 |
| Architecture | Single instance (no clustering in Community Edition) |

---

## 2. Data Model (18 Entities)

### Core Entities

| Entity | Purpose | Key Relationships |
|---|---|---|
| **User** | User accounts | →WROTE→Post, →FOLLOWS→User, →BLOCKED→User, →MUTED→User |
| **Post** | Content items (posts + articles) | →TAGGED→Tag, →IN→Category, →IN_GROUP→Group |
| **Comment** | Post comments | →WROTE→Comment, Comment→ON→Post |
| **Group** | User groups | →MEMBER_OF→Group, Post→IN_GROUP→Group |
| **Tag** | Hashtags | Post→TAGGED→Tag |
| **Category** | Content categories | Post→IN→Category |
| **Message** | Direct messages | →SENT→Message, Message→IN→Room |
| **Room** | Chat rooms | User→PARTICIPANT→Room |

### Support Entities

| Entity | Purpose |
|---|---|
| **Badge** | User achievements/badges |
| **Donations** | Donation/sponsorship tracking |
| **EmailAddress** | Verified email addresses |
| **UnverifiedEmailAddress** | Pending email verification |
| **File** | Uploaded file metadata |
| **Image** | Image metadata + URLs |
| **InviteCode** | Registration invite codes |
| **Location** | Geographic coordinates |
| **Report** | Content moderation reports |
| **SocialMedia** | User social media links |
| **Migration** | Database migration state |

### Key Relationships (from GraphQL types)

```
User -[:WROTE]-> Post
User -[:WROTE]-> Comment  
User -[:FOLLOWS]-> User
User -[:BLOCKED]-> User
User -[:MUTED]-> User
User -[:SHOUTED]-> Post (share/boost)
User -[:EMOTED {emotion}]-> Post
User -[:AVATAR_IMAGE]-> Image
User -[:MEMBER_OF {role}]-> Group
User -[:PARTICIPANT]-> Room
Post -[:TAGGED]-> Tag
Post -[:IN]-> Category
Post -[:IN_GROUP]-> Group
Comment -[:ON]-> Post
Message -[:IN]-> Room
Report -[:FILED]-> (Post|Comment|User)
Report -[:REVIEWED]-> (by moderator)
Notification -[:NOTIFIED]-> User
```

---

## 3. Access Patterns

### Write Operations

- All writes go through Neo4j `session.writeTransaction()`
- Neode ORM used for model creation/updates
- Direct Cypher for complex graph operations
- Bulk operations: `MATCH (everything) DETACH DELETE everything` (test reset)

### Read Operations

- `neo4j-graphql-js` auto-generates Cypher from GraphQL queries
- Custom Cypher via `@cypher` directives in `.gql` types
- `session.readTransaction()` for custom queries
- No read replicas (Community Edition limitation)

### Query Patterns

```cypher
-- User lookup with activity update
MATCH (user:User {id: $id, deleted: false, disabled: false})
SET user.lastActiveAt = toString(datetime())
RETURN user {.id, .slug, .name, .role, .disabled, .actorId}

-- Soft delete (common pattern)
MATCH (node {id: $id})
SET node.deleted = true, node.deletedAt = toString(datetime())
```

---

## 4. Migration System

- Tool: `migrate` package (generic migration runner)
- Compiler: TypeScript via `src/db/compiler.ts`
- Storage: `src/db/migrate/store.ts` (Neo4j-based migration state)
- Location: `src/db/migrations/`
- Naming: `{yyyymmddHHmmss}-{description}.ts`
- Template: `src/db/migrate/template.ts`

Production migrations: `prod:migrate` reads from `build/src/db/migrations/`.

---

## 5. Seeding

- Factory pattern via `src/db/factories.ts`
- Seed script: `src/db/seed.ts` (requires graphql type registration)
- Separate scripts for categories, badges, admin, branding
- Uses `@faker-js/faker` 9.9.0 for test data generation

---

## 6. Neo4j 4.4 End-of-Life Assessment

### Version Status

| Version | Status | Support End |
|---|---|---|
| Neo4j 4.4 | **END OF LIFE** | December 2023 |
| Neo4j 5.x | Current | Active |

### Breaking Changes in Neo4j 5.x

1. **Removed**: `dbms.security.procedures.unrestricted` → new security model
2. **Changed**: Configuration property names (new namespace system)
3. **Changed**: Bolt protocol version
4. **Changed**: APOC plugin distribution (now built-in for some features)
5. **Removed**: `dbms.allow_format_migration` (auto-detected)

### Driver Compatibility

| Driver | Neo4j Support |
|---|---|
| `neo4j-driver` 4.4.x | Neo4j 3.5–4.4 |
| `neo4j-driver` 5.x | Neo4j 4.4–5.x |

**Assessment**: Driver upgrade to 5.x is possible while maintaining Neo4j 4.4, but the Neode ORM and `neo4j-graphql-js` hardcode v4 driver APIs.

---

## 7. Critical Dependency Chain

```
neo4j-graphql-js 2.11.5 (DEPRECATED, 2021)
  └── neo4j-driver 4.x only
  └── graphql 16.x (forced via resolution)
  
neode 0.4.9 (UNMAINTAINED, 2020)
  └── neo4j-driver 4.x assumed
  └── No TypeScript types
```

**This is the single biggest technical debt in the project.** Both `neo4j-graphql-js` and `neode` are unmaintained, lock the project to Neo4j 4.4, and prevent modern features.

### Successor Options

| Current | Replacement | Maturity |
|---|---|---|
| `neo4j-graphql-js` | `@neo4j/graphql` | Mature (v6.x, active) |
| `neode` | Direct Cypher / `@neo4j/graphql` | N/A (ORM not needed) |
| `neo4j-driver` 4.4 | `neo4j-driver` 5.x | Stable |

---

## 8. Performance Characteristics

### Strengths (Graph DB)

- Social graph traversals (friends-of-friends) are O(1) per hop
- Relationship-heavy queries (followers, mentions, group members) are native
- Recommendation queries are natural graph patterns

### Limitations (Current Setup)

- **Single instance**: No clustering, no read replicas
- **No backup automation**: Dump/restore is manual
- **No connection pooling config**: Default Neo4j driver pooling
- **No monitoring**: No metrics export or health endpoints
- **In-memory transactions**: No explicit transaction timeout configuration

---

## 9. Storage Architecture

| Data | Location |
|---|---|
| User data, posts, relations | Neo4j graph |
| File metadata | Neo4j (File/Image nodes) |
| File blobs | S3 (MinIO in dev) |
| Session state | JWT (stateless) |
| Subscriptions | Redis PubSub (or in-memory) |
| Full-text search | Neo4j native (via Cypher) |

---

## 10. Risk Summary

| Risk | Severity | Impact |
|---|---|---|
| Neo4j 4.4 EOL | **CRITICAL** | No security patches since 2023 |
| `neo4j-graphql-js` deprecated | **CRITICAL** | No migration path without rewrite |
| `neode` unmaintained | **HIGH** | No bug fixes, no Neo4j 5 support |
| No auth in dev/staging | **HIGH** | Security concern for non-local deployments |
| No clustering | **MEDIUM** | Single point of failure |
| No automated backups | **MEDIUM** | Data loss risk |
| Manual Cypher in resolvers | **LOW** | Maintenance burden (but flexible) |
