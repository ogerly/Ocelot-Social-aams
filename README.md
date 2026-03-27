# Ocelot.Social — AAMS Fork

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/Ocelot-Social-Community/Ocelot-Social/blob/master/LICENSE.md)
[![Discord Channel](https://img.shields.io/discord/489522408076738561.svg)](https://discord.gg/AJSX9DCSUA)

> **Dieser Fork enthält keine Code-Änderungen.**  
> Hier wird [AAMS](https://github.com/DEVmatrose/AAMS) (Autonomous Agent Manifest Specification) auf das Ocelot-Social-Projekt angewendet — als Proof-of-Concept für KI-gestützte Projektdokumentation und Upgrade-Planung.

Für die **vollständige Projektdokumentation, Installation, Features und Screenshots** siehe das Original-Repository:  
👉 **[Ocelot-Social-Community/Ocelot-Social](https://github.com/Ocelot-Social-Community/Ocelot-Social)**

---

## Was ist hier passiert?

Wir haben AAMS auf das bestehende Ocelot-Social Repository ausgeführt. Dabei wurde **kein Quellcode verändert** — nur Dokumentation und Analysewerkzeuge hinzugefügt.

### Ergebnisse

| Artefakt | Beschreibung |
|---|---|
| **9 Whitepapers** (WP-001 – WP-009) | Tiefenanalyse aller Projekt-Layer: Architektur, Backend, Cypress, Deployment, Datenbank, Styleguide, Webapp, API-Interfaces, Ecosystem |
| **1 Diskussionspapier** (DP-001) | Supabase-Evaluation: Soll Neo4j durch PostgreSQL/Supabase ersetzt werden? Inkrementelle Migrationsstrategie |
| **3 Workpapers** | Versionscurrency (270 Dependencies analysiert), Upgrade-Plan (5 Phasen, 12–18 Wochen), Supabase-Strategie |
| **Upgrade-Simulator** | Python-Skript das Versionskompatibilität, Peer-Dependencies und Upgrade-Blockaden simuliert — ohne das System hochzufahren |
| **Diary + LTM-Index** | Chronologisches Entscheidungslog und Langzeitgedächtnis für Session-Kontinuität |

### Kernerkenntisse

- **2 kritische deprecated Packages** (`neo4j-graphql-js`, `neode`) blockieren die gesamte Upgrade-Kette
- **Webapp ist 2 Generationen zurück** (Vue 2, Nuxt 2, Apollo 2, graphql 14, ESLint 7)
- **packages/ui ist bereits modern** (Vite 7, Vue 3, Tailwind 4) — die Zielarchitektur existiert schon
- **Neo4j wird unter Wert genutzt** — keine Graph-spezifischen Features aktiv, alle Queries sind Standard-CRUD
- **472 Testdateien** existieren als Sicherheitsnetz für Upgrades

---

## Was ist AAMS?

**AAMS** (Autonomous Agent Manifest Specification) ist ein Standard dafür, wie KI-Agenten mit einem Repository arbeiten. Anstatt bei jeder Session von null anzufangen, baut AAMS ein strukturiertes Arbeitsgedächtnis auf:

```
WORKING/
├── WHITEPAPER/     ← Stabile Architektur-Wahrheit (9 Whitepapers + Diskussionspapiere)
├── WORKPAPER/      ← Aktive Analysen + geschlossenes Archiv
├── DIARY/          ← Chronologisches Entscheidungslog
├── MEMORY/         ← Langzeit-Kontext (LTM-Index)
└── TOOLS/          ← Projekt-spezifische Skripte
```

### Vorteile

- **Onboarding in 10 Minuten**: Neue Contributors lesen die Whitepapers und haben den vollen Projektüberblick — statt Wochen den Code zu durchforsten
- **Entscheidungs-Nachvollziehbarkeit**: Jede Architektur-Entscheidung ist im Diary dokumentiert — das institutionelle Gedächtnis verschwindet nicht mehr in Slack/Discord
- **Session-Kontinuität**: Jeder KI-Agent (oder Mensch) kann den LTM-Index lesen und dort weitermachen, wo der letzte aufgehört hat
- **Reproduzierbare Analysen**: Workpapers dokumentieren nicht nur Ergebnisse, sondern auch die Methodik und die gelesenen Dateien (File Protocol)
- **Zero Runtime Dependencies**: Alles ist Markdown — kein Build-Step, keine Datenbank, kein Tool-Lock-in

---

## Schnellstart

```bash
# Repository klonen
git clone https://github.com/YOUR-FORK/Ocelot-Social.git
cd Ocelot-Social

# AAMS-Dokumentation lesen
cat WORKING/WHITEPAPER/INDEX.md          # Übersicht aller Whitepapers
cat WORKING/DIARY/2026-03.md             # Entscheidungslog
cat WORKING/MEMORY/ltm-index.md          # Langzeit-Kontext

# Upgrade-Simulator ausführen
python WORKING/TOOLS/upgrade-simulator.py --offline --dry-run
python WORKING/TOOLS/upgrade-simulator.py --html report.html
```

Für **Installation, Docker Setup, Tests und Deployment** des eigentlichen Ocelot-Social:  
👉 [Original README](https://github.com/Ocelot-Social-Community/Ocelot-Social#readme) · [SUMMARY.md](./SUMMARY.md) · [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## Projektstruktur (Ocelot-Social)

| Verzeichnis | Beschreibung | Whitepaper |
|---|---|---|
| `backend/` | Node.js + Apollo Server 4 + GraphQL + Neo4j | [WP-002](WORKING/WHITEPAPER/WP-002-backend.md) |
| `webapp/` | Vue 2.7 + Nuxt 2.18 (SSR) + Apollo Client 2 | [WP-007](WORKING/WHITEPAPER/WP-007-webapp.md) |
| `cypress/` | E2E-Tests: Cypress 15 + Cucumber/Gherkin | [WP-003](WORKING/WHITEPAPER/WP-003-cypress.md) |
| `packages/ui/` | Shared UI-Library: Vue 3 + Vite 7 + Tailwind 4 | [WP-006](WORKING/WHITEPAPER/WP-006-styleguide.md) |
| `deployment/` | Docker Compose + Kubernetes/Helm | [WP-004](WORKING/WHITEPAPER/WP-004-deployment.md) |
| `neo4j/` | Graph-Datenbank (4.4 Community, EOL) | [WP-005](WORKING/WHITEPAPER/WP-005-database.md) |
| `WORKING/` | AAMS-Arbeitsverzeichnis (dieses Projekt) | — |

---

## Kontakt

- **Ocelot-Social Community**: [Discord](https://discord.gg/AJSX9DCSUA) · [hello@ocelot.social](mailto:hello@ocelot.social)
- **AAMS**: [github.com/DEVmatrose/AAMS](https://github.com/DEVmatrose/AAMS)

## Lizenz

[MIT](LICENSE.md) — siehe Original-Repository.
