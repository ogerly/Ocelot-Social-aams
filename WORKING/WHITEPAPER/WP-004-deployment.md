# WP-004 — Deployment & Infrastructure Analysis

**Created**: 2026-03-27 | **Status**: Active | **Author**: GitHub Copilot (AAMS Bootstrap)

---

## 1. Overview

Deployment spans four layers: Docker Compose (local dev/test), Container Registry (GHCR), Kubernetes (production), and CI/CD (GitHub Actions + release-please).

---

## 2. Docker Compose Architecture

### Four Compose Configurations

| File | Purpose | Loaded by default |
|---|---|---|
| `docker-compose.yml` | Production build | Explicit `-f` only |
| `docker-compose.override.yml` | Development (auto-merge) | Yes (Docker default) |
| `docker-compose.base.yml` | Base images only | Explicit `-f` only |
| `docker-compose.test.yml` | Test environment | Explicit `-f` only |

### Service Topology

#### Production (`docker-compose.yml`)

| Service | Image | Port | Depends on |
|---|---|---|---|
| webapp | `ghcr.io/.../webapp:${OCELOT_VERSION}` | 3000 | backend |
| backend | `ghcr.io/.../backend:${OCELOT_VERSION}` | 4000 | neo4j |
| neo4j | `ghcr.io/.../neo4j:community` | 7687 | — |
| maintenance | `ghcr.io/.../maintenance:${OCELOT_VERSION}` | 3001 | — |
| ui | `ghcr.io/.../ui:${OCELOT_VERSION}` | 6006 | — |

#### Development (`docker-compose.override.yml` adds)

| Service | Purpose | Port |
|---|---|---|
| mailserver (Maildev) | Email testing | 1080 (web), 1025 (SMTP) |
| minio | S3-compatible storage | 9000, 9001 (console) |
| minio-mc | MinIO client (bucket setup) | — |
| imagor | Image processing proxy | 8000 |

Dev overrides mount source volumes for hot-reload:
- `./webapp:/app` + `./packages/ui:/packages/ui`
- `./backend:/app`

#### Test (`docker-compose.test.yml`)

Same as dev but with `NODE_ENV=test`, coverage volume mounts, and no source mounts.

---

## 3. Container Build Strategy

### Multi-Stage Builds

Dockerfiles use multi-stage targets:

| Target | Purpose |
|---|---|
| `base` | Dependencies installed, no source |
| `development` | Source mounted, dev tools, hot-reload |
| `test` | Source copied, test deps, coverage output |
| `production` | Built artifacts only, minimal image |

### Container Registry

All images published to GitHub Container Registry:
```
ghcr.io/ocelot-social-community/ocelot-social/{service}:{tag}
```

Services: `webapp`, `backend`, `neo4j`, `maintenance`, `ui`

---

## 4. Kubernetes / Helm

### Two Helm Charts

#### `ocelot-social` (Main Application)

```yaml
apiVersion: v2
name: ocelot-social
version: 0.1.0
appVersion: "3.15.1"
```

**Templates:**
- `backend/` — StatefulSet + PVC (10Gi) + Service + Secret
- `webapp/` — Deployment + Service + ConfigMap + Secret
- `maintenance/` — Deployment + Service
- `imagor/` — Deployment + Service + Secret
- `ingress.yaml` — Ingress with cert-manager TLS
- `acme-issuer.yaml` — Let's Encrypt certificate issuer
- `configmap.yaml` — Shared configuration

**Defaults:**
- Domain: `stage.ocelot.social`
- Backend storage: 10Gi PVC
- Image pull policy: `IfNotPresent`
- Imagor: `shumc/imagor:1.5.4`

#### `ocelot-neo4j` (Database)

```yaml
apiVersion: v2
name: ocelot-neo4j
version: 0.1.0
appVersion: "3.15.1"
```

**Templates:**
- `neo4j/` — StatefulSet + PVC (5Gi data + 10Gi backups) + Service + ConfigMap + Secret

**Neo4j Configuration:**
- `NEO4J_AUTH=none`
- Bolt thread pool max: 400
- APOC + algo procedures unrestricted
- Format migration and upgrade allowed

---

## 5. Helmfile

```
deployment/helm/helmfile/
├── helmfile.yaml.gotmpl      ← Helmfile template
├── values/ocelot.yaml        ← Environment values
└── secrets/ocelot.yaml       ← Encrypted secrets (SOPS/age)
```

---

## 6. Environment Configuration

### Key Deployment Environment Variables

| Category | Variables |
|---|---|
| Database | `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` |
| SMTP | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_DKIM_*` |
| S3 | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT`, `AWS_REGION`, `AWS_BUCKET` |
| Security | `JWT_SECRET`, `IMAGOR_SECRET` |
| URLs | `CLIENT_URI`, `GRAPHQL_URI`, `WEBSOCKETS_URI` |
| Features | `PUBLIC_REGISTRATION`, `INVITE_REGISTRATION`, `CATEGORIES_ACTIVE` |
| Monitoring | `SENTRY_DSN_BACKEND`, `SENTRY_DSN_WEBAPP` |

---

## 7. Staging & Release

- **Staging**: `stage.ocelot.social`
- **Release automation**: `release-please-config.json`
- **Release script**: `scripts/release.sh`
- **Version format**: semver (`3.15.1`)
- **CHANGELOG**: Auto-generated from conventional commits

---

## 8. Observations

| Issue | Severity | Detail |
|---|---|---|
| Neo4j Community (no TLS) | **MEDIUM** | Enterprise features needed for production security |
| `NEO4J_AUTH=none` everywhere | **HIGH** | Auth disabled even in staging defaults |
| Helm chart version 0.1.0 | **LOW** | Charts not independently versioned |
| No health checks in compose | **MEDIUM** | No `healthcheck` directives for service readiness |
| MinIO `readonly-policy.json` | **INFO** | Public-read bucket policy for dev |
| Imagor 1.5.4 | **LOW** | Check for updates |
