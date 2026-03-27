# WP-008 — API Interfaces

**Created**: 2026-03-27 | **Status**: Active | **Author**: GitHub Copilot (AAMS Bootstrap)

---

## 1. Overview

The platform exposes a single **GraphQL API** (no REST endpoints) with real-time capabilities via WebSocket subscriptions.

| Aspect | Detail |
|---|---|
| Protocol | GraphQL over HTTP (POST `/api`) + WebSocket (dual protocol) |
| Schema | Auto-augmented by `neo4j-graphql-js` (+ custom resolvers) |
| Types | 28 `.gql` type definitions, 11 enums |
| Queries | 35+ |
| Mutations | 60+ |
| Subscriptions | 3 (notifications, chat messages, room count) |
| Auth | JWT Bearer token (cookie-based on webapp) |
| Permissions | `graphql-shield` (default: deny all) |
| Middleware | 16-layer pipeline via `graphql-middleware` |

---

## 2. Schema Infrastructure

### Type Loading

```
backend/src/graphql/types/**/*.gql
  → @graphql-tools/load-files (glob)
  → @graphql-tools/merge (mergeTypeDefs)
  → neo4j-graphql-js makeAugmentedSchema()
```

### Resolver Loading

```
backend/src/graphql/resolvers/**/*.ts
  → @graphql-tools/load-files (glob, exclude *.spec.*, index.*)
  → @graphql-tools/merge (mergeResolvers)
```

### Auto-Augmentation

`neo4j-graphql-js` auto-generates Cypher for most Query types. **Excluded from auto-generation** (custom resolvers only):
Badge, Embed, EmailNotificationSettings, EmailAddress, Notification, Statistics, LoggedInUser, Location, SocialMedia, NOTIFIED, FILED, REVIEWED, Report, Group.

All mutations are **custom** (`mutation: false`).

---

## 3. Entity Type System

### Core Entities (6)

| Type | Key Fields | Graph Relationships |
|---|---|---|
| **User** | id, actorId, name, email, slug, avatar, role, publicKey, locationName, about, locale | WROTE→Post/Comment, FOLLOWS→User, BLOCKED→User, MUTED→User, MEMBER_OF→Group, PARTICIPANT→Room |
| **Post** | id, activityId, objectId, title, slug, content, visibility, language, postType, pinned, eventStart/End | IN→Category, TAGGED→Tag, IN_GROUP→Group, EMOTED←User |
| **Comment** | id, activityId, content, contentExcerpt, deleted, disabled | ON→Post, WROTE←User |
| **Group** | id, name, slug, about, description, groupType, actionRadius, locationName, myRole | MEMBER_OF←User, IN_GROUP←Post |
| **Message** | id, indexId, content, saved, distributed, seen | IN→Room, SENT←User |
| **Room** | id, lastMessageAt | PARTICIPANT←User, IN←Message |

### Supporting Entities (14)

Badge, Category, Tag, Report, Embed, Image, File, InviteCode, Location, SocialMedia, EmailAddress, Donations, Statistics, UserData

### Relationship Types (5)

| Type | Fields | Connects |
|---|---|---|
| **EMOTED** | emotion | User → Post |
| **FILED** | reasonCategory, reasonDescription, createdAt | User → Report target |
| **REVIEWED** | disable, closed, createdAt, updatedAt | Moderator → Report target |
| **MEMBER_OF** | role (pending/usual/admin/owner) | User → Group |
| **NOTIFIED** | reason, from, to, read, createdAt | Notification → User |

### Enums (11)

Visibility, UserRole, PostType, Emotion, GroupType, GroupMemberRole, GroupActionRadius, OnlineStatus, ShoutTypeEnum, EmailNotificationSettingsType, EmailNotificationSettingsName

---

## 4. Custom Directives

| Directive | Purpose | Usage |
|---|---|---|
| `@cypher(statement: String)` | Inline Cypher on fields (neo4j-graphql-js) | Computed fields: counts, aggregations, status checks |
| `@relation(name, from, to, direction)` | Neo4j relationship mapping | Structural relationships |
| `@neo4j_ignore` | Exclude field from Neo4j auto-gen | Custom resolver fields |

`@cypher` is used extensively for:
- User email (admin/self visibility)
- Follow/block/mute counts
- Post emotion/comment/shout counts
- Group member counts
- Room unread counts
- Related contributions

---

## 5. Query API (35+ queries)

### Authentication Required

| Query | Auth Level | Description |
|---|---|---|
| `currentUser` | Authenticated | Current logged-in user with full profile |
| `mutedUsers` | Authenticated | User's mute list |
| `blockedUsers` | Authenticated | User's block list |
| `notifications(read, orderBy)` | Authenticated | User notifications |
| `Donations` | Authenticated | Donation info |
| `userData(id)` | Authenticated | User data export |
| `Room(id, orderBy)` | Authenticated | Chat rooms |
| `Message(roomId)` | Authenticated | Chat messages |
| `UnreadRooms` | Authenticated | Unread room count |
| `Group(isMember, id, slug)` | Authenticated | Groups (visibility rules) |
| `GroupMembers(id)` | Member | Group member list |
| `GroupCount(isMember)` | Authenticated | Group count |

### Admin/Moderator

| Query | Auth Level |
|---|---|
| `availableRoles` | Admin |
| `statistics` | Admin |
| `PostsPinnedCounts` | Admin |
| `reports(orderBy, reviewed, closed)` | Moderator |

### Public

| Query | Description |
|---|---|
| `User(id, email, name, slug)` | User lookup (email filter: admin only) |
| `Post(id, slug, filter)` | Posts with visibility filtering |
| `profilePagePosts(filter)` | Profile page posts |
| `PostsEmotionsCountByEmotion` | Emotion counts |
| `Comment(...)` | Comments |
| `Category(...)` | Categories |
| `Tag(...)` | Tags |
| `searchPosts/Users/Groups/Hashtags` | Full-text search |
| `searchResults(query, limit)` | Combined multi-search |
| `embed(url)` | URL metadata (oEmbed) |
| `VerifyNonce(email, nonce)` | Email nonce verification |
| `queryLocations(place, lang)` | MapBox location search |
| `Badge` | All badges |
| `validateInviteCode(code)` | Invite code check |

---

## 6. Mutation API (60+ mutations)

### Authentication (6)

```graphql
login(email: String!, password: String!): String!  # Returns JWT
Signup(email: String!, locale: String!, inviteCode: String): EmailAddress
SignupVerification(nonce: String!, email: String!, name: String!, password: String!, ...): User
requestPasswordReset(email: String!, locale: String!): Boolean!
resetPassword(email: String!, nonce: String!, newPassword: String!): Boolean!
changePassword(oldPassword: String!, newPassword: String!): String!
```

### User Management (5)

UpdateUser, DeleteUser, switchUserRole, saveCategorySettings, updateOnlineStatus

### Social Interactions (8)

followUser, unfollowUser, muteUser, unmuteUser, blockUser, unblockUser, shout, unshout

### Posts (11)

CreatePost, UpdatePost, DeletePost, AddPostEmotions, RemovePostEmotions, pinPost, unpinPost, pinGroupPost, unpinGroupPost, pushPost, unpushPost, markTeaserAsViewed, toggleObservePost

### Comments (3)

CreateComment, UpdateComment, DeleteComment

### Groups (7)

CreateGroup, UpdateGroup, JoinGroup, LeaveGroup, ChangeGroupMemberRole, RemoveUserFromGroup, muteGroup, unmuteGroup

### Chat (3)

CreateRoom, CreateMessage, MarkMessagesAsSeen

### Moderation (2)

fileReport, review

### Badges (5)

setVerificationBadge, rewardTrophyBadge, revokeBadge, setTrophyBadgeSelected, resetTrophyBadgesSelected

### Other (8)

AddEmailAddress, VerifyEmailAddress, CreateSocialMedia, UpdateSocialMedia, DeleteSocialMedia, UpdateDonations, generatePersonalInviteCode, generateGroupInviteCode, invalidateInviteCode, redeemInviteCode

---

## 7. Subscriptions (3)

| Subscription | Event | Filter |
|---|---|---|
| `notificationAdded → NOTIFIED` | `NOTIFICATION_ADDED` | `payload.to.id === context.user.id` |
| `chatMessageAdded → Message` | `CHAT_MESSAGE_ADDED` | `payload.userId === context.user.id` |
| `roomCountUpdated → Int` | `ROOM_COUNT_UPDATED` | `payload.userId === context.user.id` |

### WebSocket Transport

**Dual-protocol** for backward compatibility:
- `graphql-ws` (modern, spec-compliant)
- `subscriptions-transport-ws` (legacy, for Nuxt 2 Apollo Client)

Route selection via `sec-websocket-protocol` HTTP header.

### PubSub Backend

- **Primary**: Redis via `graphql-redis-subscriptions` + `ioredis`
- **Fallback**: In-memory `PubSub` (graphql-subscriptions)
- Selection: If `REDIS_DOMAIN` env var is set → Redis, else → in-memory

---

## 8. Permissions System (graphql-shield)

### Default Policy: **DENY ALL**

Every query and mutation must be explicitly allowed.

### Permission Rules

| Rule | Logic |
|---|---|
| `isAuthenticated` | Valid JWT in context |
| `isAdmin` | `context.user.role === 'admin'` |
| `isModerator` | `context.user.role in ['admin', 'moderator']` |
| `onlyYourself` | `args.id === context.user.id` |
| `isMyOwn` | Resource created by current user |
| `isAuthor` | Post/comment author check |
| `isDeletingOwnAccount` | Deleting own account only |
| `noEmailFilter` | Prevent non-admin email queries |
| `isMySocialMedia` | Own social media entries only |
| `canCommentPost` | Post allows comments |
| `isMemberOfGroup` | Group membership check |
| `isAllowedTo*Group*` | 7 group-specific permission rules |
| `publicRegistration` | `CONFIG.PUBLIC_REGISTRATION === true` |
| `inviteRegistration` | `CONFIG.INVITE_REGISTRATION === true` |

### Field-Level Permissions

- `User.email` → admin or self only
- `Group.*` → public fields (slug, name, about, groupType, avatar) visible to all
- `InviteCode`, `Location`, `Report` → restricted fields

---

## 9. Middleware Pipeline (16 layers)

Applied in order via `graphql-middleware`:

| # | Middleware | Purpose |
|---|---|---|
| 1 | **sentry** | Error tracking/reporting |
| 2 | **permissions** | graphql-shield authorization |
| 3 | **xss** | HTML sanitization (cleanHtml on content) |
| 4 | **validation** | Input validation rules |
| 5 | **userInteractions** | Social interaction processing |
| 6 | **sluggify** | Auto-generate URL slugs |
| 7 | **languages** | Language detection on content |
| 8 | **excerpt** | Content excerpt generation |
| 9 | **login** | Login-specific processing |
| 10 | **notifications** | Notification creation triggers |
| 11 | **hashtags** | Hashtag extraction and linking |
| 12 | **softDelete** | Soft delete enforcement (filter deleted) |
| 13 | **includedFields** | Field inclusion logic |
| 14 | **orderBy** | Sort order processing |
| 15 | **chatMiddleware** | Chat-specific logic |
| 16 | **categories** | Category processing |

Middlewares can be disabled via `CONFIG.DISABLED_MIDDLEWARES` env var.

---

## 10. Search System

### Full-Text Indexes (Neo4j Lucene)

- `post_fulltext_search` — Post title + content
- `user_fulltext_search` — User name + about
- `tag_fulltext_search` — Tag id
- `group_fulltext_search` — Group name + about + description

### Query Weight System

| Match Type | Weight |
|---|---|
| Whole text exact | 8× |
| Each word exact | 4× |
| Some words exact | 2× |
| Prefix match | 1× |

### Multi-Search Prefixes

| Prefix | Target |
|---|---|
| `!` | Posts |
| `@` | Users |
| `#` | Hashtags |
| `&` | Groups |
| None | Combined results |

---

## 11. File Upload Interface

| Aspect | Detail |
|---|---|
| Scalar | `Upload` from `graphql-upload` |
| Express middleware | `graphql-upload-express` (multipart) |
| Storage | S3-compatible (MinIO in dev, any S3 in prod) |
| Image processing | Imagor proxy with HMAC signing |
| Buckets | `public/` (avatars, post images), `attachments/` (chat files) |

---

## 12. ActivityPub (Preparatory)

Fields exist on schema but no active federation:

| Field | Type |
|---|---|
| `User.actorId` | ActivityPub actor ID |
| `User.publicKey` | Signature verification key |
| `Post.activityId` | Activity identifier |
| `Post.objectId` | Object identifier |
| `Comment.activityId` | Activity identifier |

Proxy routes in webapp (`/.well-known/webfinger`, `/activitypub`) forward to backend. `SharedInboxEndpoint.gql.old` exists as deprecated type definition.

---

## 13. Resolver Patterns

### Generic Resolver Factory

```typescript
// Resolver.ts — generates resolvers from configuration
{
  hasOne:  { field: '<-[:WROTE]-(author:User)' },
  hasMany: { field: '-[:TAGGED]->(tag:Tag)' },
  count:   { field: '-[:EMOTED]->(post:Post) WHERE ...' },
  boolean: { field: 'MATCH (this)-[:FOLLOWS]->(target) ...' },
  undefinedToNull: ['about', 'locationName']
}
```

### Custom Error Types

- `UserInputError` (BAD_USER_INPUT) — invalid input validation
- `AuthenticationError` (UNAUTHENTICATED) — auth failure
- `ForbiddenError` (FORBIDDEN) — permission denied

---

## 14. Risk Assessment

| Risk | Severity | Impact |
|---|---|---|
| `neo4j-graphql-js` schema generation | **CRITICAL** | Deprecated library generates auto-queries; migration to `@neo4j/graphql` requires schema rewrite |
| No rate limiting | **HIGH** | GraphQL endpoint vulnerable to query complexity attacks |
| No query depth limiting | **HIGH** | Nested queries can exhaust backend resources |
| Dual WebSocket protocol | **MEDIUM** | Maintenance overhead; `subscriptions-transport-ws` is deprecated |
| 60+ mutations without batching | **LOW** | Normal for GraphQL; no DataLoader visible |
| `graphql-upload` | **LOW** | Single file upload per request; no chunked upload |
