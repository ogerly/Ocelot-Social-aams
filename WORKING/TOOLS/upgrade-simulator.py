#!/usr/bin/env python3
"""
Ocelot-Social Upgrade-Simulator
================================
Simuliert Paket-Upgrades ohne das System hochzufahren.
Prüft Versionskompatibilität, Peer-Dependencies und bekannte Blockaden.

Verwendung:
    python upgrade-simulator.py                     # Vollständiger Report
    python upgrade-simulator.py --phase 1           # Nur Phase 1 simulieren
    python upgrade-simulator.py --package jsonwebtoken --target 9.0.0  # Einzelpaket
    python upgrade-simulator.py --dry-run           # Alle Phasen durchspielen
    python upgrade-simulator.py --offline           # Ohne npm-Registry (nur lokale Regeln)
    python upgrade-simulator.py --html report.html  # HTML-Report generieren

Voraussetzungen:
    pip install requests semver
"""

import json
import os
import re
import sys
import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

# Optionale Abhängigkeiten
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ============================================================
# Konfiguration
# ============================================================

# Projekt-Root relativ zum Skript-Standort
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # WORKING/TOOLS/ -> ROOT

# Package.json Pfade
PACKAGE_JSONS = {
    "root": PROJECT_ROOT / "package.json",
    "backend": PROJECT_ROOT / "backend" / "package.json",
    "webapp": PROJECT_ROOT / "webapp" / "package.json",
    "ui": PROJECT_ROOT / "packages" / "ui" / "package.json",
    "styleguide": PROJECT_ROOT / "styleguide" / "package.json",
}

# ============================================================
# Datenmodelle
# ============================================================

class Severity(Enum):
    OK = "OK"
    INFO = "INFO"
    WARNING = "WARNUNG"
    ERROR = "FEHLER"
    CRITICAL = "KRITISCH"

class UpgradePhase(Enum):
    PHASE_0 = "Phase 0: Cleanup"
    PHASE_1 = "Phase 1: Backend sicher"
    PHASE_2 = "Phase 2: Webapp sicher"
    PHASE_3 = "Phase 3: Datenbank"
    PHASE_4 = "Phase 4: Frontend-Modernisierung"
    PHASE_5 = "Phase 5: Konsolidierung"

@dataclass
class PackageInfo:
    name: str
    current_version: str
    layer: str
    is_dev: bool = False
    latest_version: Optional[str] = None
    peer_dependencies: dict = field(default_factory=dict)

@dataclass
class UpgradeCheck:
    package: str
    layer: str
    current: str
    target: str
    severity: Severity
    message: str
    blocked_by: list = field(default_factory=list)
    phase: Optional[UpgradePhase] = None

@dataclass
class ConflictReport:
    checks: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    blockers: list = field(default_factory=list)

# ============================================================
# Bekannte Abhängigkeitsketten (manuell gepflegt)
# ============================================================

KNOWN_BLOCKERS = {
    # Paket: [(blockiert_durch, Grund)]
    "neo4j-driver@5": [
        ("neo4j-graphql-js", "neo4j-graphql-js 2.x unterstützt nur neo4j-driver 4.x")
    ],
    "graphql@16:webapp": [
        ("apollo-client@2", "Apollo Client 2 erfordert graphql <15")
    ],
    "vue@3:webapp": [
        ("nuxt@2", "Nuxt 2 ist für Vue 2. Vue 3 erfordert Nuxt 3")
    ],
    "nuxt@3": [
        ("apollo-client@2", "Erst auf @apollo/client 3.x upgraden"),
    ],
    "tiptap@2": [
        ("vue@2:webapp", "tiptap 2 erfordert Vue 3")
    ],
    "@storybook/vue@10": [
        ("vue@2:webapp", "Storybook 10 dropped Vue 2 Support")
    ],
    "v-tooltip@5": [
        ("vue@2:webapp", "v-tooltip 5.x erfordert Vue 3")
    ],
}

# Pakete die in mehreren Layern vorkommen (mit erwarteten Versionen)
CROSS_LAYER_PACKAGES = {
    "graphql": {
        "backend": "^16.13.1",
        "webapp": "14.7.0",  # Force-Resolution!
    },
    "eslint": {
        "backend": "^9.27.0",
        "webapp": "^7.28.0",
        "ui": "^9.39.2",
    },
    "vue": {
        "webapp": "~2.7.16",
        "ui": "^3.5.29",
        "styleguide": "^2.6.10",
    },
}

# Upgrade-Zuordnung zu Phasen
PHASE_ASSIGNMENTS = {
    UpgradePhase.PHASE_0: [
        ("styleguide", "*", "LÖSCHEN"),
    ],
    UpgradePhase.PHASE_1: [
        ("backend", "jsonwebtoken", "9"),
        ("backend", "@sentry/node", "8"),
        ("backend", "express", "5"),
        ("backend", "uuid", "11"),
        ("backend", "graphql-upload", "16"),
        ("backend", "subscriptions-transport-ws", "ENTFERNEN"),
        ("backend", "typescript", "5.9"),
    ],
    UpgradePhase.PHASE_2: [
        ("webapp", "sass", "1.97"),
        ("webapp", "date-fns", "4"),
        ("webapp", "core-js", "3"),
        ("webapp", "cropperjs", "2"),
        ("webapp", "eslint", "9"),
    ],
    UpgradePhase.PHASE_3: [
        ("backend", "neo4j-graphql-js", "ERSETZEN:@neo4j/graphql@6"),
        ("backend", "neode", "ENTFERNEN"),
        ("backend", "neo4j-driver", "5"),
    ],
    UpgradePhase.PHASE_4: [
        ("webapp", "apollo-client", "ERSETZEN:@apollo/client@3"),
        ("webapp", "graphql", "16"),
        ("webapp", "nuxt", "3"),
        ("webapp", "vue", "3.5"),
        ("webapp", "tiptap", "ERSETZEN:@tiptap/vue-3@2"),
        ("webapp", "@storybook/vue", "10"),
        ("webapp", "mapbox-gl", "ERSETZEN:maplibre-gl@4"),
    ],
}

# ============================================================
# Hilfsfunktionen
# ============================================================

def parse_semver(version_str: str) -> tuple:
    """Extrahiert Major.Minor.Patch aus einer Versionsangabe."""
    clean = re.sub(r'^[~^>=<]*', '', version_str.strip())
    clean = clean.split('-')[0]  # Pre-Release entfernen
    parts = clean.split('.')
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except ValueError:
        return (0, 0, 0)

def version_gap(current: str, latest: str) -> str:
    """Berechnet die Art der Versionslücke."""
    c = parse_semver(current)
    l = parse_semver(latest)
    if c[0] < l[0]:
        diff = l[0] - c[0]
        return f"{diff} Major-Version(en) zurück"
    elif c[1] < l[1]:
        diff = l[1] - c[1]
        return f"{diff} Minor-Version(en) zurück"
    elif c[2] < l[2]:
        return "Patch-Update verfügbar"
    else:
        return "Aktuell ✅"

def is_major_upgrade(current: str, target: str) -> bool:
    """Prüft ob es sich um ein Major-Upgrade handelt."""
    c = parse_semver(current)
    t = parse_semver(target)
    return t[0] > c[0]

def load_package_json(path: Path) -> dict:
    """Lädt eine package.json Datei."""
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_npm_info(package_name: str) -> Optional[dict]:
    """Holt Paketinfo von der npm-Registry."""
    if not HAS_REQUESTS:
        return None
    try:
        url = f"https://registry.npmjs.org/{package_name}/latest"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except (requests.RequestException, json.JSONDecodeError):
        pass
    return None

# ============================================================
# Kern-Logik
# ============================================================

class UpgradeSimulator:
    def __init__(self, offline: bool = False):
        self.offline = offline
        self.packages: dict[str, list[PackageInfo]] = {}
        self.checks: list[UpgradeCheck] = []
        self.npm_cache: dict[str, dict] = {}

    def load_all_packages(self):
        """Lädt alle package.json Dateien und sammelt Paketinformationen."""
        print("📦 Lade Paketinformationen...")
        for layer, path in PACKAGE_JSONS.items():
            pkg = load_package_json(path)
            if not pkg:
                print(f"  ⚠️  {layer}: Datei nicht gefunden ({path})")
                continue

            self.packages[layer] = []
            # Dependencies
            for name, version in pkg.get("dependencies", {}).items():
                self.packages[layer].append(PackageInfo(
                    name=name, current_version=version, layer=layer, is_dev=False
                ))
            # DevDependencies
            for name, version in pkg.get("devDependencies", {}).items():
                self.packages[layer].append(PackageInfo(
                    name=name, current_version=version, layer=layer, is_dev=True
                ))

            dep_count = len(pkg.get("dependencies", {}))
            dev_count = len(pkg.get("devDependencies", {}))
            print(f"  ✅ {layer}: {dep_count} deps + {dev_count} devDeps")

    def fetch_latest_versions(self, packages_to_check: Optional[list] = None):
        """Holt aktuelle Versionen von npm (wenn online)."""
        if self.offline:
            print("📡 Offline-Modus — überspringe npm-Registry-Abfragen")
            return

        if not HAS_REQUESTS:
            print("📡 requests-Modul nicht installiert — überspringe npm-Abfragen")
            print("   Installieren mit: pip install requests")
            return

        all_packages = set()
        for layer_packages in self.packages.values():
            for pkg in layer_packages:
                if packages_to_check is None or pkg.name in packages_to_check:
                    all_packages.add(pkg.name)

        print(f"\n📡 Frage npm-Registry für {len(all_packages)} Pakete ab...")
        for i, name in enumerate(sorted(all_packages)):
            if name in self.npm_cache:
                continue
            info = get_npm_info(name)
            if info:
                self.npm_cache[name] = info
            if (i + 1) % 20 == 0:
                print(f"   ... {i + 1}/{len(all_packages)} abgefragt")

        print(f"   ✅ {len(self.npm_cache)} Pakete erfolgreich abgefragt")

        # Latest-Versionen zuweisen
        for layer_packages in self.packages.values():
            for pkg in layer_packages:
                if pkg.name in self.npm_cache:
                    pkg.latest_version = self.npm_cache[pkg.name].get("version")
                    pkg.peer_dependencies = self.npm_cache[pkg.name].get("peerDependencies", {})

    def check_known_blockers(self):
        """Prüft bekannte Abhängigkeitsketten und Blockaden."""
        print("\n🔗 Prüfe bekannte Abhängigkeitsketten...")

        for blocker_key, blocks in KNOWN_BLOCKERS.items():
            parts = blocker_key.split(":")
            pkg_version = parts[0]
            layer_filter = parts[1] if len(parts) > 1 else None

            pkg_name, target_major = pkg_version.rsplit("@", 1)

            for blocked_by, reason in blocks:
                self.checks.append(UpgradeCheck(
                    package=pkg_name,
                    layer=layer_filter or "alle",
                    current="?",
                    target=f">= {target_major}",
                    severity=Severity.CRITICAL,
                    message=f"BLOCKIERT: {reason}",
                    blocked_by=[blocked_by],
                ))

    def check_cross_layer_conflicts(self):
        """Prüft Versionskonflikte zwischen Layern."""
        print("🔄 Prüfe Cross-Layer-Konflikte...")

        for pkg_name, layer_versions in CROSS_LAYER_PACKAGES.items():
            versions_found = {}
            for layer, expected in layer_versions.items():
                if layer in self.packages:
                    for pkg in self.packages[layer]:
                        if pkg.name == pkg_name:
                            versions_found[layer] = pkg.current_version
                            break

            if len(versions_found) > 1:
                unique_majors = set()
                for v in versions_found.values():
                    unique_majors.add(parse_semver(v)[0])

                if len(unique_majors) > 1:
                    layers_str = ", ".join(f"{l}: {v}" for l, v in versions_found.items())
                    self.checks.append(UpgradeCheck(
                        package=pkg_name,
                        layer="cross-layer",
                        current=str(versions_found),
                        target="vereinheitlichen",
                        severity=Severity.WARNING,
                        message=f"Versionskonflikt zwischen Layern: {layers_str}",
                    ))

    def check_deprecated_packages(self):
        """Prüft auf bekannte deprecated/unmaintained Pakete."""
        print("⚠️  Prüfe deprecated/unmaintained Pakete...")

        DEPRECATED = {
            "neo4j-graphql-js": ("DEPRECATED seit 2021", Severity.CRITICAL),
            "neode": ("UNMAINTAINED seit 2020", Severity.CRITICAL),
            "subscriptions-transport-ws": ("DEPRECATED, ersetzt durch graphql-ws", Severity.WARNING),
            "apollo-client": ("EOL v2, ersetzt durch @apollo/client 3+", Severity.CRITICAL),
            "apollo-cache-inmemory": ("EOL v1, Teil von Apollo Client v2", Severity.CRITICAL),
            "core-js": ("v2 unmaintained, v3 ist aktuell", Severity.WARNING),
        }

        for layer_name, layer_packages in self.packages.items():
            for pkg in layer_packages:
                if pkg.name in DEPRECATED:
                    reason, severity = DEPRECATED[pkg.name]
                    self.checks.append(UpgradeCheck(
                        package=pkg.name,
                        layer=layer_name,
                        current=pkg.current_version,
                        target="ersetzen/entfernen",
                        severity=severity,
                        message=reason,
                    ))

    def check_peer_dependencies(self):
        """Prüft Peer-Dependency-Verletzungen."""
        if self.offline:
            return

        print("🔍 Prüfe Peer-Dependencies...")

        for layer_name, layer_packages in self.packages.items():
            # Erstelle Index der installierten Versionen in diesem Layer
            installed = {}
            for pkg in layer_packages:
                installed[pkg.name] = pkg.current_version

            # Prüfe Peer-Dependencies
            for pkg in layer_packages:
                for peer_name, peer_range in pkg.peer_dependencies.items():
                    if peer_name in installed:
                        # Vereinfachte Prüfung: Major-Version muss passen
                        installed_major = parse_semver(installed[peer_name])[0]
                        peer_major = parse_semver(peer_range)[0]
                        if installed_major < peer_major:
                            self.checks.append(UpgradeCheck(
                                package=pkg.name,
                                layer=layer_name,
                                current=installed[peer_name],
                                target=peer_range,
                                severity=Severity.WARNING,
                                message=f"Peer-Dependency-Verletzung: {pkg.name} erfordert {peer_name} {peer_range}, installiert ist {installed[peer_name]}",
                            ))

    def simulate_phase(self, phase: UpgradePhase) -> list[UpgradeCheck]:
        """Simuliert eine Upgrade-Phase und gibt Ergebnisse zurück."""
        results = []
        assignments = PHASE_ASSIGNMENTS.get(phase, [])

        for layer, pkg_name, target in assignments:
            # Finde das Paket
            current_version = "?"
            if layer in self.packages:
                for pkg in self.packages[layer]:
                    if pkg.name == pkg_name:
                        current_version = pkg.current_version
                        break

            # Prüfe Blockaden
            blockers = []
            for blocker_key, blocks in KNOWN_BLOCKERS.items():
                parts = blocker_key.split(":")
                bpkg = parts[0]
                blayer = parts[1] if len(parts) > 1 else None

                if f"{pkg_name}@{target.split('.')[0]}" == bpkg or bpkg.startswith(f"{pkg_name}@"):
                    if blayer is None or blayer == layer:
                        for blocked_by, reason in blocks:
                            blockers.append(f"{blocked_by}: {reason}")

            if target.startswith("ENTFERNEN"):
                severity = Severity.INFO
                msg = f"Paket entfernen"
            elif target.startswith("ERSETZEN:"):
                replacement = target.split(":", 1)[1]
                severity = Severity.WARNING
                msg = f"Ersetzen durch {replacement}"
            elif target.startswith("LÖSCHEN"):
                severity = Severity.INFO
                msg = f"Layer/Verzeichnis entfernen"
            elif blockers:
                severity = Severity.CRITICAL
                msg = f"BLOCKIERT: {'; '.join(blockers)}"
            elif is_major_upgrade(current_version, target):
                severity = Severity.WARNING
                msg = f"Major-Upgrade — Breaking Changes möglich"
            else:
                severity = Severity.OK
                msg = f"Sicheres Upgrade"

            results.append(UpgradeCheck(
                package=pkg_name,
                layer=layer,
                current=current_version,
                target=target,
                severity=severity,
                message=msg,
                blocked_by=blockers,
                phase=phase,
            ))

        return results

    def run_full_simulation(self) -> ConflictReport:
        """Führt die vollständige Simulation durch."""
        report = ConflictReport()

        self.load_all_packages()
        self.fetch_latest_versions()
        self.check_known_blockers()
        self.check_cross_layer_conflicts()
        self.check_deprecated_packages()
        self.check_peer_dependencies()

        # Phasen simulieren
        print("\n🚀 Simuliere Upgrade-Phasen...")
        for phase in UpgradePhase:
            phase_results = self.simulate_phase(phase)
            report.checks.extend(phase_results)

        # Allgemeine Checks hinzufügen
        report.checks.extend(self.checks)

        # Kategorisieren
        for check in report.checks:
            if check.severity == Severity.CRITICAL:
                report.blockers.append(check)
            elif check.severity == Severity.WARNING:
                report.warnings.append(check)

        return report

    def simulate_single_package(self, package: str, target: str) -> list[UpgradeCheck]:
        """Simuliert das Upgrade eines einzelnen Pakets."""
        results = []

        # Finde das Paket in allen Layern
        for layer_name, layer_packages in self.packages.items():
            for pkg in layer_packages:
                if pkg.name == package:
                    # Prüfe Blockers
                    blockers = []
                    for blocker_key, blocks in KNOWN_BLOCKERS.items():
                        parts = blocker_key.split(":")
                        bpkg = parts[0]
                        blayer = parts[1] if len(parts) > 1 else None

                        target_major = parse_semver(target)[0]
                        if f"{package}@{target_major}" == bpkg:
                            if blayer is None or blayer == layer_name:
                                for blocked_by, reason in blocks:
                                    blockers.append(f"{blocked_by}: {reason}")

                    severity = Severity.CRITICAL if blockers else (
                        Severity.WARNING if is_major_upgrade(pkg.current_version, target)
                        else Severity.OK
                    )

                    results.append(UpgradeCheck(
                        package=package,
                        layer=layer_name,
                        current=pkg.current_version,
                        target=target,
                        severity=severity,
                        message=f"BLOCKIERT: {'; '.join(blockers)}" if blockers else "Upgrade möglich",
                        blocked_by=blockers,
                    ))

        return results

# ============================================================
# Ausgabe-Formatierung
# ============================================================

SEVERITY_EMOJI = {
    Severity.OK: "✅",
    Severity.INFO: "ℹ️ ",
    Severity.WARNING: "⚠️ ",
    Severity.ERROR: "❌",
    Severity.CRITICAL: "🔴",
}

SEVERITY_COLOR = {
    Severity.OK: "#28a745",
    Severity.INFO: "#17a2b8",
    Severity.WARNING: "#ffc107",
    Severity.ERROR: "#dc3545",
    Severity.CRITICAL: "#8b0000",
}

def print_report(report: ConflictReport):
    """Gibt den Report auf der Konsole aus."""
    print("\n" + "=" * 70)
    print("  OCELOT-SOCIAL UPGRADE-SIMULATION — ERGEBNISBERICHT")
    print("=" * 70)

    # Zusammenfassung
    total = len(report.checks)
    ok = sum(1 for c in report.checks if c.severity == Severity.OK)
    info = sum(1 for c in report.checks if c.severity == Severity.INFO)
    warn = sum(1 for c in report.checks if c.severity == Severity.WARNING)
    crit = sum(1 for c in report.checks if c.severity == Severity.CRITICAL)

    print(f"\n📊 Zusammenfassung: {total} Prüfungen")
    print(f"   ✅ OK: {ok}  |  ℹ️  Info: {info}  |  ⚠️  Warnung: {warn}  |  🔴 Kritisch: {crit}")

    # Kritische Blocker
    if report.blockers:
        print(f"\n{'─' * 70}")
        print("🔴 KRITISCHE BLOCKER")
        print(f"{'─' * 70}")
        for check in report.blockers:
            print(f"\n  {SEVERITY_EMOJI[check.severity]} {check.package} ({check.layer})")
            print(f"     Aktuell: {check.current} → Ziel: {check.target}")
            print(f"     {check.message}")
            if check.blocked_by:
                for blocker in check.blocked_by:
                    print(f"     └─ Blockiert durch: {blocker}")

    # Warnungen
    if report.warnings:
        print(f"\n{'─' * 70}")
        print("⚠️  WARNUNGEN")
        print(f"{'─' * 70}")
        for check in report.warnings:
            print(f"\n  {SEVERITY_EMOJI[check.severity]} {check.package} ({check.layer})")
            print(f"     Aktuell: {check.current} → Ziel: {check.target}")
            print(f"     {check.message}")

    # Phasen-Übersicht
    print(f"\n{'─' * 70}")
    print("📋 PHASEN-ÜBERSICHT")
    print(f"{'─' * 70}")

    for phase in UpgradePhase:
        phase_checks = [c for c in report.checks if c.phase == phase]
        if not phase_checks:
            continue

        phase_ok = sum(1 for c in phase_checks if c.severity in (Severity.OK, Severity.INFO))
        phase_blocked = sum(1 for c in phase_checks if c.severity == Severity.CRITICAL)
        phase_warn = sum(1 for c in phase_checks if c.severity == Severity.WARNING)

        status = "✅ BEREIT" if phase_blocked == 0 else f"🔴 {phase_blocked} BLOCKER"
        print(f"\n  {phase.value}: {status}")

        for check in phase_checks:
            emoji = SEVERITY_EMOJI[check.severity]
            print(f"    {emoji} {check.package}: {check.current} → {check.target} — {check.message}")

    print(f"\n{'=' * 70}")


def generate_html_report(report: ConflictReport, output_path: str):
    """Generiert einen HTML-Report."""
    html = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Ocelot-Social Upgrade-Simulation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 2rem; background: #f5f5f5; }
        h1 { margin-bottom: 1rem; color: #333; }
        h2 { margin: 2rem 0 1rem; color: #555; border-bottom: 2px solid #ddd; padding-bottom: 0.5rem; }
        .summary { display: flex; gap: 1rem; margin: 1rem 0 2rem; }
        .stat { padding: 1rem 2rem; border-radius: 8px; color: white; font-size: 1.2rem; }
        .stat-ok { background: #28a745; }
        .stat-info { background: #17a2b8; }
        .stat-warn { background: #ffc107; color: #333; }
        .stat-crit { background: #dc3545; }
        .check { padding: 1rem; margin: 0.5rem 0; border-radius: 6px; border-left: 4px solid; background: white; }
        .check-ok { border-color: #28a745; }
        .check-info { border-color: #17a2b8; }
        .check-warn { border-color: #ffc107; }
        .check-crit { border-color: #dc3545; background: #fff5f5; }
        .pkg-name { font-weight: bold; font-size: 1.1rem; }
        .pkg-layer { color: #888; font-size: 0.9rem; }
        .pkg-version { color: #666; }
        .pkg-message { margin-top: 0.3rem; }
        .blocker { color: #dc3545; font-style: italic; }
        .phase { margin: 1.5rem 0; padding: 1rem; background: white; border-radius: 8px; }
        .phase-header { display: flex; align-items: center; gap: 0.5rem; }
        .phase-status { padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; color: white; }
        .phase-ready { background: #28a745; }
        .phase-blocked { background: #dc3545; }
    </style>
</head>
<body>
    <h1>🐆 Ocelot-Social Upgrade-Simulation</h1>
"""

    # Zusammenfassung
    total = len(report.checks)
    ok = sum(1 for c in report.checks if c.severity == Severity.OK)
    info = sum(1 for c in report.checks if c.severity == Severity.INFO)
    warn = sum(1 for c in report.checks if c.severity == Severity.WARNING)
    crit = sum(1 for c in report.checks if c.severity == Severity.CRITICAL)

    html += f"""
    <div class="summary">
        <div class="stat stat-ok">✅ OK: {ok}</div>
        <div class="stat stat-info">ℹ️ Info: {info}</div>
        <div class="stat stat-warn">⚠️ Warnung: {warn}</div>
        <div class="stat stat-crit">🔴 Kritisch: {crit}</div>
    </div>
"""

    # Kritische Blocker
    if report.blockers:
        html += "<h2>🔴 Kritische Blocker</h2>\n"
        for check in report.blockers:
            html += f"""
    <div class="check check-crit">
        <span class="pkg-name">{check.package}</span>
        <span class="pkg-layer">({check.layer})</span><br>
        <span class="pkg-version">{check.current} → {check.target}</span>
        <div class="pkg-message">{check.message}</div>
"""
            for b in check.blocked_by:
                html += f'        <div class="blocker">└─ Blockiert durch: {b}</div>\n'
            html += "    </div>\n"

    # Phasen
    html += "<h2>📋 Phasen-Übersicht</h2>\n"
    for phase in UpgradePhase:
        phase_checks = [c for c in report.checks if c.phase == phase]
        if not phase_checks:
            continue

        phase_blocked = sum(1 for c in phase_checks if c.severity == Severity.CRITICAL)
        status_class = "phase-blocked" if phase_blocked > 0 else "phase-ready"
        status_text = f"{phase_blocked} Blocker" if phase_blocked > 0 else "Bereit"

        html += f"""
    <div class="phase">
        <div class="phase-header">
            <h3>{phase.value}</h3>
            <span class="phase-status {status_class}">{status_text}</span>
        </div>
"""
        for check in phase_checks:
            sev_class = f"check-{check.severity.name.lower()}"
            if check.severity == Severity.CRITICAL:
                sev_class = "check-crit"
            elif check.severity == Severity.WARNING:
                sev_class = "check-warn"
            elif check.severity == Severity.INFO:
                sev_class = "check-info"
            else:
                sev_class = "check-ok"

            html += f"""
        <div class="check {sev_class}">
            <span class="pkg-name">{check.package}</span>
            <span class="pkg-layer">({check.layer})</span>
            <span class="pkg-version"> — {check.current} → {check.target}</span>
            <div class="pkg-message">{check.message}</div>
        </div>
"""
        html += "    </div>\n"

    html += """
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n📄 HTML-Report generiert: {output_path}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Ocelot-Social Upgrade-Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python upgrade-simulator.py                              Vollständiger Report
  python upgrade-simulator.py --phase 1                    Nur Phase 1 simulieren
  python upgrade-simulator.py --package jsonwebtoken --target 9.0.0
  python upgrade-simulator.py --offline                    Ohne npm-Registry
  python upgrade-simulator.py --html report.html           HTML-Report
  python upgrade-simulator.py --dry-run                    Alle Phasen durchspielen
        """,
    )

    parser.add_argument("--offline", action="store_true",
                        help="Ohne npm-Registry-Abfragen (nur lokale Regeln)")
    parser.add_argument("--phase", type=int, choices=[0, 1, 2, 3, 4, 5],
                        help="Nur eine bestimmte Phase simulieren")
    parser.add_argument("--package", type=str,
                        help="Einzelnes Paket simulieren")
    parser.add_argument("--target", type=str,
                        help="Zielversion für --package")
    parser.add_argument("--html", type=str, metavar="DATEI",
                        help="HTML-Report in Datei schreiben")
    parser.add_argument("--dry-run", action="store_true",
                        help="Alle Phasen durchspielen und Report anzeigen")

    args = parser.parse_args()

    simulator = UpgradeSimulator(offline=args.offline)
    simulator.load_all_packages()

    # Einzelpaket-Modus
    if args.package:
        if not args.target:
            print("❌ --target ist erforderlich bei --package")
            sys.exit(1)

        simulator.fetch_latest_versions([args.package])
        results = simulator.simulate_single_package(args.package, args.target)

        print(f"\n📦 Simulation: {args.package} → {args.target}")
        print("─" * 50)
        for check in results:
            emoji = SEVERITY_EMOJI[check.severity]
            print(f"  {emoji} Layer: {check.layer}")
            print(f"     Aktuell: {check.current}")
            print(f"     {check.message}")
            if check.blocked_by:
                for b in check.blocked_by:
                    print(f"     └─ {b}")
        return

    # Phasen-Modus
    if args.phase is not None:
        phase = list(UpgradePhase)[args.phase]
        results = simulator.simulate_phase(phase)
        print(f"\n📋 Simulation: {phase.value}")
        print("─" * 50)
        for check in results:
            emoji = SEVERITY_EMOJI[check.severity]
            print(f"  {emoji} {check.package} ({check.layer}): {check.current} → {check.target}")
            print(f"     {check.message}")
        return

    # Vollständiger Report
    if not args.offline:
        simulator.fetch_latest_versions()

    report = simulator.run_full_simulation()
    print_report(report)

    if args.html:
        generate_html_report(report, args.html)


if __name__ == "__main__":
    main()
