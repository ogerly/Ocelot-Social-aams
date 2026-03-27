# ~~Workpaper: Supabase Evaluation — Neo4j → Supabase Migration Assessment~~

> **SUPERSEDED** — Dieses Dokument wurde am 2026-03-27 als Diskussionspapier reklassifiziert.  
> Aktuelle Version: [`WORKING/WHITEPAPER/DP-001-supabase-evaluation.md`](../WHITEPAPER/DP-001-supabase-evaluation.md)

**Session**: 2026-03-27 | **Author**: GitHub Copilot | **Type**: ~~Evaluation~~ → Diskussionspapier (DP-001)

---

## 1. Purpose

Evaluate replacing the current Neo4j 4.4 + neo4j-graphql-js + Neode stack with **Supabase** (PostgreSQL-based backend-as-a-service). Assess feasibility, effort, benefits, risks, and architectural impact.

## 2. File Protocol

| File | Operation |
|---|---|
| WP-005-database.md | READ — Current database architecture |
| WP-002-backend.md | READ — Backend architecture |
| WP-008-api-interfaces.md | READ — GraphQL API surface |
| WP-007-webapp.md | READ — Frontend data consumption |

---

## 3. Current State: Neo4j Stack

### What We Have

| Component | Version | Status |
|---|---|---|
| **Neo4j** | 4.4 Community | EOL (Dec 2023) |
| **neo4j-graphql-js** | 2.11.5 | Deprecated (2021) |
| **neode** | 0.4.9 | Unmaintained (2020) |
| **neo4j-driver** | 4.4.11 | EOL |
| APOC plugin | 4.4.0.17 | EOL with Neo4j 4.4 |

### What It Does

- 18 data entity types (User, Post, Comment, Group, Message, Room, etc.)
- ~15 relationship types (WROTE, FOLLOWS, BLOCKED, MEMBER_OF, EMOTED, etc.)
- Full-text search (Neo4j Lucene indexes)
- `@cypher` directives for computed fields
- Auto-generated CRUD via `neo4j-graphql-js`
- Migration system via `migrate` package
- APOC for platform statistics (`apoc.meta.stats()`)

### What Neo4j Gives Us (Graph Advantages)

1. Social graph traversals (friends-of-friends, recommendations) in O(1) per hop
2. Relationship-first queries (`-[:FOLLOWS]->`, `-[:BLOCKED]->`) natural to express
3. Variable-length path queries (e.g., mutual connections)
4. Schema-free relationship properties (EMOTED with emotion type, MEMBER_OF with role)

### What Neo4j Costs Us (Current Pains)

1. **Two deprecated libraries** lock entire upgrade chain
2. **No clustering** (Community Edition)
3. **No managed hosting options** (unlike PostgreSQL)
4. **Small talent pool** — Cypher expertise rare
5. **No auth** in all environments (NEO4J_AUTH=none)
6. **No automated backups**
7. **Complex migration** from 4.4 to 5.x even staying with Neo4j

---

## 4. Supabase Evaluation

### What Is Supabase?

Open-source Firebase alternative built on PostgreSQL. Provides:

| Feature | Detail |
|---|---|
| **Database** | PostgreSQL (any version, currently 17.x) |
| **Auth** | JWT-based auth with Row Level Security (RLS) |
| **Storage** | S3-compatible object storage |
| **Realtime** | WebSocket-based realtime subscriptions (Postgres Changes) |
| **Edge Functions** | Deno-based serverless functions |
| **Auto-API** | PostgREST (REST) + pg_graphql (GraphQL) |
| **Dashboard** | Admin UI for database, auth, storage, logs |

### Supabase vs Current Stack Mapping

| Current Component | Supabase Equivalent | Fit |
|---|---|---|
| Neo4j graph database | PostgreSQL (relational) | ⚠️ Data model transformation required |
| neo4j-graphql-js (auto GraphQL) | pg_graphql (auto GraphQL from Postgres schema) | ✅ Similar concept |
| Neode ORM | Prisma / Drizzle / raw SQL | ✅ Better ecosystem |
| Neo4j Lucene search | PostgreSQL full-text search (tsvector) | ✅ Comparable |
| WS subscriptions (graphql-ws) | Supabase Realtime (Postgres Changes) | ✅ Better |
| JWT auth (custom) | Supabase Auth (GoTrue) | ✅ Much better |
| MinIO / S3 storage | Supabase Storage | ✅ Integrated |
| Redis PubSub | Supabase Realtime | ✅ Eliminates Redis |
| APOC statistics | PostgreSQL aggregate queries | ✅ Native |
| Custom email (nodemailer) | Supabase Auth emails + custom | ⚠️ Partial coverage |
| graphql-shield permissions | PostgreSQL Row Level Security (RLS) | ✅ Database-level security |

---

## 5. Data Model Transformation

### Graph → Relational Mapping

The social graph data model translates to relational tables + junction tables:

#### Direct Mapping (Entities → Tables)

| Neo4j Node | PostgreSQL Table | Notes |
|---|---|---|
| User | `users` | Standard table |
| Post | `posts` | Standard table |
| Comment | `comments` | `post_id` FK |
| Group | `groups` | Standard table |
| Message | `messages` | `room_id` FK |
| Room | `rooms` | Standard table |
| Tag | `tags` | Standard table |
| Category | `categories` | Standard table |
| Badge | `badges` | Standard table |
| Report | `reports` | Polymorphic target |
| Image | `images` | Standard table |
| File | `files` | Standard table |
| InviteCode | `invite_codes` | Standard table |
| Location | `locations` | PostGIS extension available |
| SocialMedia | `social_media` | `user_id` FK |
| EmailAddress | `email_addresses` | `user_id` FK |
| Donations | `donations` | Standard table |
| Migration | `migrations` | Standard table |

#### Relationship → Junction Table Mapping

| Neo4j Relationship | PostgreSQL | Notes |
|---|---|---|
| User-[:WROTE]->Post | `posts.author_id` FK | Simple FK |
| User-[:WROTE]->Comment | `comments.author_id` FK | Simple FK |
| User-[:FOLLOWS]->User | `user_follows` (follower_id, followed_id) | Junction table |
| User-[:BLOCKED]->User | `user_blocks` (blocker_id, blocked_id) | Junction table |
| User-[:MUTED]->User | `user_mutes` (muter_id, muted_id) | Junction table |
| User-[:SHOUTED]->Post | `post_shouts` (user_id, post_id) | Junction table |
| User-[:EMOTED]->Post | `post_emotions` (user_id, post_id, emotion) | Junction + property |
| Post-[:TAGGED]->Tag | `post_tags` (post_id, tag_id) | Junction table |
| Post-[:IN]->Category | `post_categories` (post_id, category_id) | Junction table |
| Post-[:IN_GROUP]->Group | `posts.group_id` FK | Simple FK |
| User-[:MEMBER_OF]->Group | `group_members` (user_id, group_id, role) | Junction + property |
| User-[:PARTICIPANT]->Room | `room_participants` (user_id, room_id) | Junction table |
| Report-[:FILED]->Target | `reports` (reporter_id, target_type, target_id, reason) | Polymorphic |
| Report-[:REVIEWED]->Mod | `report_reviews` (report_id, moderator_id, decision) | Junction + properties |
| Notification-[:NOTIFIED]->User | `notifications` (user_id, reason, from_id, read) | Standard table |
| User-[:AVATAR_IMAGE]->Image | `users.avatar_image_id` FK | Simple FK |

**Assessment**: All 15 relationship types translate cleanly to either foreign keys (1:N) or junction tables (M:N with optional properties). No variable-length path queries are actually used in production.

---

## 6. Graph Advantage Analysis

**Critical question**: Does this application actually need a graph database?

### Features That Benefit From Graph

| Feature | Currently Used? | Complexity |
|---|---|---|
| Friends-of-friends recommendations | ❌ Not implemented | Would be better in graph |
| Mutual connections display | ❌ Not implemented | Possible in SQL with joins |
| Social graph visualization | ❌ Not implemented | Possible with any DB |
| Shortest path between users | ❌ Not implemented | Graph-native |
| Community detection | ❌ Not implemented | Graph-native |

### Features That Work Equally Well in SQL

| Feature | Status | SQL Approach |
|---|---|---|
| User follow/block/mute | ✅ Active | Junction tables with indexes |
| Post feed with filters | ✅ Active | JOIN + WHERE + ORDER BY |
| Group membership | ✅ Active | Junction table with role column |
| Chat rooms | ✅ Active | Standard relational model |
| Full-text search | ✅ Active | PostgreSQL tsvector/tsquery |
| Content moderation | ✅ Active | Standard queries |
| Pagination | ✅ Active | OFFSET/LIMIT or cursor |
| Aggregations (counts) | ✅ Active | COUNT(*) with GROUP BY |

### Verdict

**The application does not currently use any graph-specific features.** All active queries are standard CRUD + junction table lookups + full-text search — patterns that PostgreSQL handles natively and efficiently.

The graph advantage would only materialize if the platform implements social recommendation algorithms, path-based queries, or community detection — none of which are on the current roadmap.

**However**: ActivityPub/Fediverse integration is an *explicit* project goal (README, schema fields). ActivityPub is fundamentally a graph protocol. This must influence the architecture decision — see Section 11.

---

## 7. Supabase Benefits

### Immediate Wins

| Benefit | Impact |
|---|---|
| **Managed hosting** | Supabase Cloud or self-hosted with Docker |
| **Built-in auth** | Replaces custom JWT + bcrypt + email verification |
| **Row Level Security** | Database-level authorization replaces graphql-shield |
| **Realtime subscriptions** | Postgres Changes replaces Redis PubSub + WebSocket protocol |
| **Auto-generated API** | pg_graphql generates GraphQL from schema (CRUD only — see caveat in Section 11) |
| **Storage** | Integrated S3-compatible storage (replaces MinIO) |
| **Dashboard** | Admin UI for database, auth, storage, logs |
| **Backups** | Point-in-time recovery (managed), pg_dump (self-hosted) |
| **Ecosystem** | PostgreSQL has the largest ecosystem of any database |
| **Talent pool** | PostgreSQL/SQL expertise is universal |

### Architecture Simplification

```
BEFORE (6 services):
  Neo4j + MinIO + Imagor + Redis + Maildev + App Server

AFTER (3 services):
  Supabase (PostgreSQL + Auth + Storage + Realtime) + Imagor + App Server
```

### Cost Reduction (Self-Hosted)

- Removes Neo4j Community (custom Docker) → PostgreSQL (standard)
- Removes MinIO → Supabase Storage
- Removes Redis → Supabase Realtime
- Single Docker Compose for Supabase (or Supabase Cloud free tier for dev)

---

## 8. Supabase Risks & Challenges

### Migration Effort

| Task | Effort | Risk |
|---|---|---|
| Design PostgreSQL schema (18 tables + 14 junction tables) | **HIGH** | Data model decisions are foundational |
| Rewrite all resolvers from Cypher to SQL/Prisma | **VERY HIGH** | 40+ resolver files, each with Cypher queries |
| Replace neo4j-graphql-js auto-generation with pg_graphql or custom | **HIGH** | Different augmentation model |
| Replace Neode models with Prisma/Drizzle models | **MEDIUM** | Better tooling available |
| Migrate graphql-shield rules to RLS policies | **HIGH** | Different authorization model |
| Data migration (Neo4j → PostgreSQL) | **MEDIUM** | Write export/import scripts |
| Replace custom auth with Supabase Auth | **HIGH** | JWT format changes, session handling |
| Update all Cypress E2E tests | **HIGH** | API changes propagate to tests |
| Update webapp GraphQL operations (if schema changes) | **MEDIUM** | Depends on how much schema changes |

### Technical Risks

| Risk | Severity | Mitigation |
|---|---|---|
| **Schema design errors** | HIGH | Thorough design phase, prototype first |
| **Performance regression** | MEDIUM | PostgreSQL is well-optimized for these patterns; benchmark key queries |
| **RLS complexity** | MEDIUM | Start simple, iterate |
| **pg_graphql limitations** | MEDIUM | Can fall back to custom resolvers |
| **Vendor lock-in (Supabase Cloud)** | LOW | Self-hosted option exists; PostgreSQL is portable |
| **Supabase stability** | LOW | PostgreSQL underneath is rock-solid |
| **Migration data loss** | LOW | Test migration scripts thoroughly, keep Neo4j running during transition |

### What We Lose

| Capability | Impact |
|---|---|
| Native graph traversals | LOW — not currently used |
| @cypher directives | MEDIUM — need to rewrite as SQL views/functions |
| Cypher as query language | LOW — team can learn SQL (more common) |
| Future graph features (recommendations, paths) | **HIGH** — ActivityPub is a graph protocol; needs mitigation (see Apache AGE in Section 11) |

### Data Migration Realities

**Die Datenmigration ist der härteste Teil.** Neo4j-Export ist nicht trivial:
- Slug-Uniqueness muss sichergestellt sein (Neo4j erlaubt Duplikate ohne Constraint)
- Relationship-IDs existieren in Neo4j nicht als Integer — neue Surrogate Keys nötig
- Soft-deleted Nodes haben inkonsistente Relationship-States
- Timestamps als Strings (`toString(datetime())`) müssen nach `timestamptz` konvertiert werden
- Embed/Image-Referenzen müssen von S3-Keys auf Supabase Storage Paths remapped werden

**Empfehlung**: Export-Skripte als eigenen Milestone planen, nicht als Nebenaufgabe.

---

## 9. Alternative: Stay with Neo4j (Upgrade Path)

If staying with Neo4j, the upgrade path is:

| Step | Effort | Risk |
|---|---|---|
| Replace `neo4j-graphql-js` → `@neo4j/graphql` 6.x | **VERY HIGH** | Schema format changes, resolver patterns change |
| Replace `neode` → direct Cypher or `@neo4j/graphql` OGM | **HIGH** | All 18 model files rewritten |
| Upgrade `neo4j-driver` 4.4 → 5.x | **MEDIUM** | API changes |
| Upgrade Neo4j 4.4 → 5.x | **MEDIUM** | Config changes, APOC changes |
| Test entire application | **HIGH** | Regression testing |

**Estimated effort**: Similar to Supabase migration, but:
- You still end up with a niche database (smaller ecosystem)
- You still need MinIO, Redis, custom auth
- You don't gain auth, storage, realtime, managed hosting

---

## 10. Comparison Matrix

| Criterion | Stay Neo4j (Upgrade) | Switch to Supabase | Winner |
|---|---|---|---|
| Migration effort | VERY HIGH | VERY HIGH | **Tie** |
| Post-migration maintenance | Higher (niche stack) | Lower (standard stack) | **Supabase** |
| Managed hosting | ❌ Neo4j Aura only (expensive) | ✅ Supabase Cloud (free tier) | **Supabase** |
| Auth system | Custom (keep current) | Built-in (Supabase Auth) | **Supabase** |
| Object storage | Still need MinIO | Built-in (Supabase Storage) | **Supabase** |
| Realtime | Still need Redis + WS | Built-in (Supabase Realtime) | **Supabase** |
| Ecosystem | Niche | Massive (PostgreSQL) | **Supabase** |
| Talent pool | Small (Cypher) | Huge (SQL) | **Supabase** |
| Graph features | ✅ Native | ❌ Requires workarounds | **Neo4j** |
| ActivityPub federation | Cypher-based (native fit) | SQL-based (needs Apache AGE or workaround) | **Neo4j** |
| Performance (current patterns) | Good | Better (indexing, joins) | **Supabase** |
| Backup/recovery | Manual | Automated (PITR) | **Supabase** |
| Monitoring | Manual | Built-in dashboard | **Supabase** |
| Community (FOSS) | Neo4j Community | PostgreSQL + Supabase | **Supabase** |

**Score**: Neo4j wins 2 criteria (graph features + ActivityPub), Supabase wins 10, 1 tie.

---

## 11. Recommendation — Pragmatische Einschätzung

### **Ja zu Supabase, aber mit klaren Augen**

Neo4j wird unter seinem Wert eingesetzt. Die tatsächlichen Abfragepatterns — Follows, Posts, Kommentare, Tags — sind klassisches relationales Modell. Niemand macht Freunde-von-Freunden-Empfehlungen oder komplexe Graphtraversals. Neo4j zahlt den vollen Preis (Hosting, Expertise, Betrieb) für Features, die nicht genutzt werden.

Rationale:
1. **Operativer Gewinn ist enorm** — Auth, Storage, Realtime, Backups out-of-the-box. Statt 4+ Services habt ihr einen.
2. **SQL ist universeller** — neue Contributors kennen PostgreSQL. Cypher ist eine Hürde, die potenzielle Helfer abschreckt.
3. **RLS ist mächtig** — das Rollen-/Moderationsmodell lässt sich direkt in der Datenbank abbilden, nicht im Application Layer.
4. **Effort vergleichbar** — Resolver-Rewrite ist so oder so nötig (neo4j-graphql-js ist tot).

### Kritische Einschränkungen

**1. ActivityPub ist das eigentliche Zukunftsziel.**
Im README steht explizit, dass Ocelot-Social sich ins Fediverse integrieren will. ActivityPub ist ein Graph-Protokoll. Wenn das ernst gemeint ist, könnte der Schritt weg von Neo4j mittelfristig schmerzen.

**Mitigation: Apache AGE** — Graph-Extension für PostgreSQL. Damit könnt ihr Supabase nutzen UND native Graphtraversal haben — beides in einer Datenbank. Noch jung, aber vielversprechend. Auf dem Radar behalten.

**2. pg_graphql reicht NICHT für das bestehende Schema.**
pg_graphql ist gut für CRUD, aber nicht für Business-Logik. Das bestehende GraphQL-API hat Custom Resolver, Authentifizierungslogik, komplexe Mutationen (60+). 

**Empfehlung**: Bestehendes Node/Apollo-Backend behalten, nur den Datenbankzugriff von `neo4j-driver` auf Supabase-Client (oder Prisma/Drizzle) umstellen. Das ist der realistische Migrationspfad — kein Architekturwechsel des API-Layers.

**3. Die Datenmigration ist der härteste Teil.**
Neo4j-Export ist nicht trivial. Slugs, Relationship-Integrität, Timestamp-Konvertierung, S3-Path-Remapping — unterschätzt das nicht (siehe Section 8).

### Migrationsstrategie: Inkrementell, nicht Big Bang

| Schritt | Was | Risiko | Gewinn |
|---|---|---|---|
| **1. Auth & Storage zuerst** | MinIO → Supabase Storage, Custom JWT → Supabase Auth. Backend bleibt auf Neo4j. | **GERING** | Sofortiger operativer Gewinn, Redis entfällt |
| **2. PostgreSQL parallel aufbauen** | Schema anlegen, Daten spiegeln, Queries testen. Kein Cutover. | **GERING** | Validierung ohne Risiko |
| **3. Backend umstellen** | GraphQL-Resolver umschreiben, Neo4j-Queries durch SQL ersetzen. Cypress-Tests als Validierung. | **HOCH** | Kern-Migration |
| **4. Neo4j abschalten** | Erst wenn Schritt 3 stabil ist und alle E2E-Tests grün sind. | **GERING** | Cleanup |

**Warum diese Reihenfolge?**
- Schritt 1 liefert *sofort* Wert ohne die Datenbank anzufassen
- Schritt 2 ermöglicht parallelen Betrieb — kein Big-Bang-Risiko
- Schritt 3 ist der harte Teil, aber zu dem Zeitpunkt sind Auth+Storage bereits migriert
- Schritt 4 passiert nur, wenn alles funktioniert

### Aufwandsschätzung (revidiert)

| Phase | Aufwand | Team |
|---|---|---|
| Schritt 1 (Auth + Storage) | 2–3 Wochen | 1 Entwickler |
| Schritt 2 (Schema + Parallelbetrieb) | 2–3 Wochen | 1 Entwickler |
| Schritt 3 (Resolver-Migration) | 6–8 Wochen | 1–2 Entwickler |
| Schritt 4 (Cleanup + Cutover) | 1 Woche | 1 Entwickler |
| **Gesamt** | **12–16 Wochen** | — |

### Verhältnis zu Vue 3 / Nuxt 3 Migration

Beide Migrationen sind weitgehend unabhängig und können parallel laufen:
- **Database-Team**: Supabase-Migration (Schritte 1–4)
- **Frontend-Team**: Vue 3 / Nuxt 3 Migration

Voraussetzung: GraphQL-Schema bleibt stabil (Resolver-Internals ändern sich, aber die API-Oberfläche bleibt gleich).

---

## 12. Decisions Required

- [ ] **Go/No-Go**: Supabase migration vs Neo4j upgrade
- [ ] **Hosting model**: Supabase Cloud vs self-hosted Docker
- [ ] **ORM choice**: Prisma vs Drizzle vs Supabase JS Client
- [ ] **GraphQL approach**: Bestehendes Apollo Server behalten (empfohlen) oder pg_graphql?
- [ ] **Apache AGE**: Jetzt evaluieren oder erst bei ActivityPub-Bedarf?
- [ ] **Timeline**: Parallel mit Vue 3 Migration oder sequentiell?

---

## 13. Next Steps

1. **Spike: Supabase Auth** — Integration mit bestehendem JWT-Flow testen (Schritt 1 validieren)
2. **Spike: Supabase Storage** — MinIO-Ersatz testen, Imagor-Kompatibilität prüfen
3. **PostgreSQL Schema-Prototyp** — Top 5 Entities (User, Post, Comment, Group, Room) + Junction Tables
4. **Spike: Prisma/Drizzle** — Apollo Resolver mit SQL-ORM statt neo4j-driver (Schritt 3 validieren)
5. **Performance Benchmark** — Schlüssel-Queries: Feed, Search, Notifications im Vergleich
6. **Apache AGE Evaluation** — Graph-Queries auf PostgreSQL testen (ActivityPub-Vorbereitung)

---

## 14. Zusammenfassung

> **Supabase ist der richtige Schritt, aber der Migrationspfad muss inkrementell sein — nicht als Big Bang.**
> 
> Auth + Storage zuerst (sofortiger Gewinn, geringes Risiko). PostgreSQL parallel aufbauen. Backend Schritt für Schritt umstellen. Neo4j erst abschalten, wenn alles grün ist.
> 
> Die Fediverse-Ambitionen müssen die Architekturentscheidung beeinflussen, bevor ihr committet. Apache AGE auf dem Radar behalten.
