# Workpaper: Session 004 — Upgrade-Planung & Dokumentenmanagement

**Session**: 2026-03-27 (Session 4) | **Autor**: GitHub Copilot (Claude Opus 4.6) | **Status**: Geschlossen

---

## 1. Zweck

Reklassifizierung der Supabase-Evaluation zum Diskussionspapier und Erstellung eines vollständigen Upgrade-Plans mit Python-Simulationsskript.

## 2. File Protocol

| Datei | Operation | Ergebnis |
|---|---|---|
| `WORKING/WORKPAPER/2026-03-27-supabase-evaluation.md` | READ+MODIFY | Als SUPERSEDED markiert |
| `WORKING/WHITEPAPER/INDEX.md` | READ+MODIFY | DP-001 Eintrag hinzugefügt |
| `WORKING/WHITEPAPER/DP-001-supabase-evaluation.md` | CREATE | Diskussionspapier erstellt |
| `backend/package.json` | READ | 63 Deps + 20 DevDeps analysiert |
| `webapp/package.json` | READ | 45 Deps + 40 DevDeps analysiert |
| `packages/ui/package.json` | READ | 4 Deps + 33 DevDeps analysiert |
| `package.json` (Root) | READ | 17 DevDeps analysiert |
| `styleguide/package.json` | READ | 1 Dep + 47 DevDeps analysiert |
| `backend/jest.config.ts` | READ | 92% Coverage-Schwelle |
| `backend/test/setup.ts` | READ | Apollo Test-Setup |
| `webapp/jest.config.js` | READ | 83% Coverage-Schwelle |
| `webapp/test/` | READ | 4 Setup-Dateien |
| `cypress/cypress.config.js` | READ | Cucumber+Webpack Config |
| `docker-compose.test.yml` | READ | 6 Test-Services |
| `WORKING/WORKPAPER/2026-03-27-upgrade-plan.md` | CREATE | 15-Abschnitt Upgrade-Plan |
| `WORKING/TOOLS/upgrade-simulator.py` | CREATE | Python-Simulationsskript |
| `WORKING/DIARY/2026-03.md` | MODIFY | 2 Einträge hinzugefügt |
| `WORKING/MEMORY/ltm-index.md` | MODIFY | Entry 004 + 005 hinzugefügt |

## 3. Durchgeführte Arbeiten

### 3.1 Supabase-Evaluation → Diskussionspapier

- Workpaper `2026-03-27-supabase-evaluation.md` als SUPERSEDED markiert
- Neues Dokument `WORKING/WHITEPAPER/DP-001-supabase-evaluation.md` erstellt (Typ: Diskussionspapier)
- WHITEPAPER/INDEX.md um DP-001 Eintrag erweitert
- Diary-Eintrag dokumentiert

### 3.2 Full-Stack Upgrade-Plan

Deep-Scan aller 5 Layer:
- **Testinfrastruktur**: 472 Testdateien erfasst (71 Backend, 152 Webapp, 27 UI, 24 E2E Features + 137 Steps)
- **Abhängigkeitsketten**: 6 kritische Ketten identifiziert (GraphQL, Vue/Nuxt, Neo4j, Webpack, ESLint, Jest)
- **Cross-Layer-Konflikte**: graphql (16 vs 14), eslint (9 vs 7), vue (3 vs 2.7 vs 2.6)
- **5-Phasen-Upgrade-Plan**: Cleanup → Backend sicher → Webapp sicher → Datenbank → Frontend-Modernisierung
- **Zeitschätzung**: 12–18 Wochen Gesamtaufwand

### 3.3 Python-Simulationsskript

`WORKING/TOOLS/upgrade-simulator.py` erstellt und getestet:
- Liest alle 5 package.json (270 Pakete)
- Prüft bekannte Blockaden, Cross-Layer-Konflikte, Deprecated-Pakete
- Simuliert Upgrade-Phasen einzeln oder gesamt
- Generiert Konsolen-Report und HTML-Report mit Ampelfarben
- Modi: `--offline`, `--phase N`, `--package X --target Y`, `--html`, `--dry-run`
- Test-Ergebnis: 39 Prüfungen, 16 kritische Blocker, 18 Warnungen, Phase 1+2 bereit

## 4. Entscheidungen

| # | Entscheidung | Begründung |
|---|---|---|
| E1 | Supabase-Evaluation ist Diskussionspapier, kein Workpaper | Strategische Entscheidungsgrundlage für das Team, nicht Session-gebunden |
| E2 | Upgrade in 5 Phasen, nicht Big Bang | Phase 1+2 sofort startbar, Phase 3+4 parallel möglich |
| E3 | Python-Simulationsskript statt manueller Prüfung | Automatisiert 90% der Upgrade-Planung, reproduzierbar |
| E4 | mapbox-gl → maplibre-gl empfohlen | Lizenz: mapbox-gl v2+ proprietär, maplibre ist FOSS-Fork |
| E5 | Styleguide-Löschung empfohlen | 47 tote Dependencies, Tests "TODO", Funktionalität in packages/ui |

## 5. Nächste Schritte

1. Phase 0: Styleguide-Abhängigkeit prüfen und löschen
2. Phase 1: `jsonwebtoken` 8 → 9 als erstes Upgrade
3. DB-Entscheidung: Team-Diskussion auf Basis DP-001
4. Nuxt 3 Migrationsstrategie: Eigenes Workpaper
