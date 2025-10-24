# SBB FDK MCP Server

<div align="center">

Model Context Protocol (MCP) Server für Fachdatenkatalog (FDK)

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.18+-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

## 📋 Übersicht

Dieser MCP-Server ermöglicht es Claude (Desktop & Code), auf den SBB Fachdatenkatalog zuzugreifen und diesen zu durchsuchen. Der Server implementiert intelligentes Caching, umfassende Suchfunktionen und bietet sowohl JSON- als auch Markdown-Ausgaben.

### ✨ Features

- 🗄️ **Smart Caching**: Lokaler JSON-Cache mit 24h Auto-Refresh
- 🔍 **9 Leistungsstarke Tools**: Umfassende Such- und Abfragefunktionen inkl. Advanced Search
- 📊 **Dual-Format**: JSON für APIs, Markdown für Menschen
- 🏗️ **Clean Architecture**: Modulares Design mit SOLID-Prinzipien
- ⚡ **Python 3.13+**: Moderne Type Hints und Union-Operatoren
- 🔄 **Retry-Logik**: Robuste API-Kommunikation mit exponentieller Backoff
- 🌐 **Multi-Language**: Unterstützung für DE, FR, IT, EN
- 📈 **Real-time Progress**: MCP-basierte Progress Notifications für Downloads
- 📝 **Comprehensive Logging**: Vollständiges Logging über MCP Context
- 🚀 **Parallel Downloads**: Bis zu 20x schnellerer Download mit Concurrency
- 🎯 **Type-Safe**: TypedDict für vollständige Type Safety ohne Runtime Overhead

---

## 📦 Installation

### Voraussetzungen

- **Python 3.13+** ([Download](https://www.python.org/downloads/))
- **uv** Package Manager ([Installation](https://github.com/astral-sh/uv))

### Server Installation

#### MCP Server Konfigurieren

##### Mit UV

```json
{
  "mcpServers": {
    "sbb-fdk": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\workspace\\elyo\\ai\\projects\\fdk-sbb\\src",
        "run",
        "sbb_fdk_mcp"
      ]
    }
  }
}
```

##### Mit UVX

```json
{
  "mcpServers": {
    "sbb-fdk": {
      "command": "uvx",
      "args": [
        "--directory",
        "C:\\workspace\\elyo\\ai\\projects\\fdk-sbb\\src",
        "sbb_fdk_mcp"
      ]
    }
  }
}
```

```bash
# Repository klonen oder entpacken
cd C:\workspace\elyo\ai\projects\fdk-sbb

# Dependencies installieren mit uv
uv sync

# Server testen
uv run python test_server.py
```

---

## 🔌 Integration mit Claude

### Option 1: Claude Desktop (macOS & Windows)

#### Schritt 1: Konfigurationsdatei öffnen

**macOS:**

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**

```powershell
code $env:APPDATA\Claude\claude_desktop_config.json
```

#### Schritt 2: Server konfigurieren

Fügen Sie folgende Konfiguration hinzu:

```json
{
  "mcpServers": {
    "sbb-fdk": {
      "command": "uv",
      "args": [
      "--directory",
      "C:\\workspace\\elyo\\ai\\projects\\fdk-sbb\\src"
        "run",
        "sbb_fdk_mcp"
      ]
    }
  }
}
```

**Hinweis:** Passen Sie den `cwd`-Pfad an Ihre Installation an!

#### Schritt 3: Claude Desktop neu starten

Starten Sie Claude Desktop neu, damit die Änderungen wirksam werden.

---

### Option 2: Claude Code (VS Code Extension)

#### Schritt 1: Konfigurationsdatei erstellen/bearbeiten

**macOS/Linux:**

```bash
code ~/.claude/config.json
```

**Windows:**

```powershell
code $env:USERPROFILE\.claude\config.json
```

#### Schritt 2: Server konfigurieren

```json
{
  "mcpServers": {
    "sbb-fdk": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\workspace\\elyo\\ai\\projects\\fdk-sbb\\src",
        "run",
        "sbb_fdk_mcp"
      ]
    },
    // Alternative mit uvx
    "sbb-fdk": {
      "command": "uvx",
      "args": [
        "--directory",
        "C:\\workspace\\elyo\\ai\\projects\\fdk-sbb\\src",
        "sbb_fdk_mcp"
      ]
    }
  }
}
```

#### Schritt 3: VS Code neu laden

Führen Sie in VS Code den Befehl aus:

Developer: Reload Window

oder drücken Sie `Ctrl+R` (Windows/Linux) / `Cmd+R` (macOS)

---

## 🛠️ Verfügbare Tools

### 1. `sbb_fdk_list_objects`

Liste und durchsuche FDK-Objekte mit Filtern und Pagination.

**Parameter:**

- `domain` (optional): Filter nach Domain (z.B. "Brücken", "Energie")
- `search` (optional): Suchbegriff für Objektnamen
- `limit` (optional): Max. Anzahl Ergebnisse (1-100, Standard: 20)
- `offset` (optional): Überspringe Ergebnisse für Pagination (Standard: 0)
- `detail` (optional): "concise" oder "detailed" (Standard: concise)
- `response_format` (optional): "markdown" oder "json" (Standard: markdown)

**Beispiele:**

Zeige mir alle Brücken-Objekte
Liste die ersten 50 Energie-Objekte
Suche nach "Stütze" im FDK-Katalog

---

### 2. `sbb_fdk_get_object`

Erhalte vollständige Details zu einem spezifischen FDK-Objekt.

**Parameter:**

- `object_id` (erforderlich): Objekt-ID (z.B. "OBJ_BR_1")
- `language` (optional): Sprachcode (de/fr/it/en, Standard: de)
- `response_format` (optional): "markdown" oder "json" (Standard: markdown)

**Beispiele:**

Zeige Details für Objekt OBJ_BR_1
Gib mir OBJ_EN_1 auf Französisch

---

### 3. `sbb_fdk_search_properties`

Durchsuche Properties über den gesamten Katalog.

**Parameter:**

- `query` (erforderlich): Suchbegriff für Property-Namen
- `limit` (optional): Max. Anzahl Ergebnisse (1-100, Standard: 20)
- `response_format` (optional): "markdown" oder "json" (Standard: markdown)

**Beispiele:**

Finde alle Properties mit "Breite"
Suche nach Material-Properties

---

### 4. `sbb_fdk_advanced_search` ✨ NEU

Erweiterte Suche über **beliebige JSON-Felder** mit flexiblen Match-Modi.

**Parameter:**

- `search_fields` (optional): Liste von Feldern zum Durchsuchen (Standard: ["all"])
  - Optionen: "all", "propertySets", "properties", "ifcClassAssignments", "ebkpConcepts", "aksCode", "componentRelationships", "assemblyRelationships", "domainModel", "nameObjectGroup", "nameSubgroup", "description", "name"
- `query` (erforderlich): Suchbegriff
- `domain_filter` (optional): Nur in bestimmter Domain suchen
- `match_mode` (optional): Art des Matchings (Standard: "contains")
  - "contains": Enthält den Suchbegriff
  - "equals": Exakte Übereinstimmung
  - "starts_with": Beginnt mit
  - "ends_with": Endet mit
- `case_sensitive` (optional): Groß-/Kleinschreibung beachten (Standard: false)
- `limit` (optional): Max. Anzahl Ergebnisse (1-200, Standard: 50)
- `response_format` (optional): "markdown" oder "json" (Standard: markdown)

**Features:**

- 🔍 **Rekursive Suche**: Durchsucht verschachtelte JSON-Strukturen
- 🚀 **Auto-Download**: Lädt Detail-Objekte transparent nach wenn benötigt
- 🎯 **Flexible Matching**: Verschiedene Match-Modi für präzise Suchen
- ⚡ **Performant**: Sucht gesamten Katalog in Sekunden

**Beispiele:**

```
Finde PropertySet "Pset_WallCommon"
  → search_fields=["propertySets"], query="Pset_WallCommon"

Suche nach IFC-Klasse "IfcWall" in Hochbau
  → search_fields=["ifcClassAssignments"], query="IfcWall", domain_filter="Hochbau"

Finde alle eBKP-Codes mit "C3"
  → search_fields=["ebkpConcepts"], query="C3"

Suche überall nach "Stütze"
  → search_fields=["all"], query="Stütze"

Exakte Suche nach PropertySet
  → search_fields=["propertySets"], query="Pset_WallCommon", match_mode="equals"

PropertySets die mit "Pset_" beginnen
  → search_fields=["propertySets"], query="Pset_", match_mode="starts_with"
```

**WICHTIG für AI:**

- ❌ **NICHT** eigenen Python-Code schreiben zum Suchen/Filtern!
- ✅ **Nutze dieses Tool** - es ist 100x schneller und effizienter!
- Das Tool lädt automatisch benötigte Daten herunter

---

### 5. `sbb_fdk_list_domains`

Liste alle Domains mit Objekt-Anzahl.

**Beispiele:**

Zeige mir eine Übersicht aller FDK-Domains
Welche Domains gibt es im Katalog?

---

### 6. `sbb_fdk_refresh_cache`

Erzwinge Cache-Aktualisierung von der API.

**Beispiele:**

Aktualisiere den FDK-Cache
Lade die neuesten Daten vom FDK

---

### 7. `sbb_fdk_get_cache_stats`

Zeige Cache-Statistiken und Status.

**Beispiele:**

Wie ist der Cache-Status?
Wann wurde der Cache zuletzt aktualisiert?

---

### 8. `sbb_fdk_download_all_objects` ✨ NEU

Lade alle Detail-Objekte vom API herunter (mit paralleler Verarbeitung).

**Parameter:**

- `language` (optional): Sprachcode (de/fr/it/en, Standard: de)
- `domain_filter` (optional): Nur Objekte einer Domain (z.B. "Hochbau", "Brücken")
- `max_concurrent` (optional): Anzahl paralleler Downloads (1-20, Standard: 10)
- `response_format` (optional): "markdown" oder "json" (Standard: markdown)

**Features:**

- ⚡ **Parallel Processing**: 10-20 gleichzeitige Downloads
- 📈 **Real-time Progress**: Live-Updates via MCP Notifications
- 🎯 **Domain Filtering**: Nur gewünschte Domains laden
- 🔄 **Retry Logic**: 3x Retry mit exponentieller Backoff
- ⏱️ **Performance**: ~2-3 Minuten für alle 1687 Objekte

**Beispiele:**

```
Lade alle FDK-Objekte herunter
Lade nur Hochbau-Objekte mit 15 parallelen Downloads
Downloade alle Brücken-Objekte auf Französisch
```

---

### 9. `sbb_fdk_update_cache` ✨ NEU

Aktualisiere fehlende oder veraltete Objekte im Cache (intelligent & parallel).

**Parameter:**

- `language` (optional): Sprachcode (de/fr/it/en, Standard: de)
- `domain_filter` (optional): Nur Objekte einer Domain
- `force_refresh` (optional): Alle Objekte neu laden (Standard: false)
- `max_concurrent` (optional): Anzahl paralleler Downloads (1-20, Standard: 10)
- `response_format` (optional): "markdown" oder "json" (Standard: markdown)

**Features:**

- 🧠 **Smart Update**: Lädt nur fehlende/unvollständige Objekte
- ⚡ **Viel schneller** als Full-Download wenn Cache existiert
- 📈 **Progress Tracking**: Live-Updates während des Updates
- 🔄 **Safe to run**: Kann regelmäßig ausgeführt werden

**Beispiele:**

```
Aktualisiere den Cache mit fehlenden Objekten
Force-refresh alle Energie-Objekte
Update nur Hochbau-Objekte
```

---

## 💡 Verwendungsbeispiele

### In Claude Desktop / Claude Code

```
👤 User: Zeige mir alle Brücken-Objekte im FDK-Katalog

🤖 Claude: Ich verwende das Tool sbb_fdk_list_objects mit domain="Brücken"...
[Ergebnisse werden angezeigt]

👤 User: Gib mir Details zu OBJ_BR_1

🤖 Claude: Ich hole die Details mit sbb_fdk_get_object...
[Details werden angezeigt]

👤 User: Welche Properties gibt es zum Thema "Breite"?

🤖 Claude: Ich suche mit sbb_fdk_search_properties...
[Properties werden angezeigt]

👤 User: Lade alle Hochbau-Objekte herunter

🤖 Claude: Ich starte den Download mit sbb_fdk_download_all_objects...
📈 Progress: 10/54 (18.5%) | 3.1 obj/sec | ETA: 0m 14s | Domain: Hochbau
📈 Progress: 20/54 (37.0%) | 3.2 obj/sec | ETA: 0m 11s | Domain: Hochbau
...
✅ Download completed: 54/54 successful in 0m 17s
```

---

## 🚀 Performance & Features

### Download Performance

| Scenario                | Objects | Time     | Speed        | Mode            |
| ----------------------- | ------- | -------- | ------------ | --------------- |
| Full Download           | 1687    | ~2-3 min | ~10-12 obj/s | Parallel (10)   |
| Single Domain (Brücken) | 54      | ~17s     | ~3.1 obj/s   | Parallel (10)   |
| Sequential (Old)        | 1687    | ~10 min  | ~2.8 obj/s   | Single-threaded |
| Max Parallel (20)       | 1687    | ~90s     | ~18 obj/s    | Parallel (20)   |

### Real-time Progress Tracking

Alle Download-Tools senden **Echtzeit-Updates** via MCP Notifications:

```
📈 10/1687 (0.6%) | 3.2 obj/sec | ETA: 8m 42s | Domain: Brücken
📈 20/1687 (1.2%) | 3.1 obj/sec | ETA: 8m 55s | Domain: Energie
📈 30/1687 (1.8%) | 3.0 obj/sec | ETA: 9m 12s | Domain: Hochbau
...
```

### Comprehensive Logging

Der Server logged alle wichtigen Events via MCP Context:

- **DEBUG**: Cache-Hits, API-Request-Details
- **INFO**: Tool-Starts, erfolgreiche Downloads, Cache-Updates
- **WARNING**: API-Retries, Cache-Miss, Timeouts
- **ERROR**: API-Fehler, Validierungsfehler, Download-Failures

Logs sind in Claude Desktop/Code sichtbar und können für Debugging verwendet werden.

---

## 🏗️ Architektur

```
fdk-sbb/
├── src/sbb_fdk_mcp/
│   ├── __init__.py       # Package-Initialisierung
│   ├── __main__.py       # Entry Point
│   ├── server.py         # MCP Tools (8 Tools mit Context & Logging)
│   ├── service.py        # Business Logic (mit Progress Tracking)
│   ├── api_client.py     # HTTP Client mit Retry & Logging
│   ├── cache.py          # JSON File Cache
│   ├── utils.py          # Formatierung & ProgressTracker
│   ├── models.py         # Pydantic Input Models
│   ├── types.py          # TypedDict Definitions (NEW)
│   └── constants.py      # Konfiguration
├── cache/                # Auto-generiertes Cache-Verzeichnis
│   ├── objects/          # Gecachte FDK-Objekte als JSON
│   └── metadata.json     # Cache-Metadaten (mit Release Info)
├── tests/                # Test-Verzeichnis
├── prompts.md            # Prompt-Vorschläge (Dokumentation)
├── pyproject.toml        # uv Projektkonfiguration
├── pyrightconfig.json    # Pyright Type Checker Konfiguration
├── ruff.toml             # Ruff Linter & Formatter Konfiguration
├── .editorconfig         # Editor-Konfiguration
├── Makefile              # Entwickler-Befehle
├── README.md             # Diese Datei
├── .gitignore            # Git Ignore-Regeln
└── test_server.py        # Schneller Verifikationstest
```

### Komponenten-Beschreibung

- **server.py**: Implementiert alle 8 MCP-Tools mit Context-Injection & Logging
- **service.py**: Business Logic mit MCP Context für Progress & Logging
- **api_client.py**: HTTP-Client mit Retry-Logik & optionalem Context-Logging
- **cache.py**: JSON-Cache mit Release-Info & Metadaten
- **utils.py**: Formatierung, ProgressTracker für Download-Statistiken
- **models.py**: Pydantic-Modelle für strikte Input-Validierung
- **types.py**: TypedDict Definitionen für API-Responses & Cache-Strukturen
- **constants.py**: Zentrale Konfigurationskonstanten

---

## 🧪 Entwicklung & Testing

### Quick Start

```bash
# Schnelltest
uv run python test_server.py

# Alle Checks ausführen
make check
```

### Development Commands

Das Projekt verwendet **Makefile** für einfache Entwicklung:

```bash
# Dependencies installieren
make install

# Code Linting (ruff)
make lint

# Code Formatierung (ruff)
make format

# Type Checking (pyright)
make typecheck

# Alle Checks (lint + typecheck)
make check

# Tests ausführen
make test

# Server starten
make run

# Cache aufräumen
make clean
```

### Manuelle Commands

```bash
# Ruff Linting
uv run ruff check src/
uv run ruff check --fix src/    # Auto-fix

# Ruff Formatierung
uv run ruff format src/
uv run ruff format --check src/ # Nur Check

# Pyright Type Checking
uv run pyright src/

# Tests
uv run pytest
```

### Code-Qualitätsmetriken

✅ **Vollständige Type Safety** mit TypedDict (ohne Runtime Overhead)
✅ **MCP Context Integration** für Logging & Progress
✅ **Parallel Processing** mit asyncio.Semaphore
✅ **Max. 120 Zeichen pro Zeile**
✅ **Vollständige Type Hints** mit Python 3.13 Syntax
✅ **Clean Code Prinzipien** durchgängig angewendet
✅ **Pyright Strict Mode** - 0 Fehler, 0 Warnings
✅ **Ruff Linting** - Alle Checks bestanden

---

## 🔧 Troubleshooting

### Problem: Server startet nicht

**Lösung:**

```bash
# Prüfen Sie Python-Version
python --version  # Sollte 3.13+ sein

# uv neu installieren
pip install --upgrade uv

# Dependencies neu installieren
cd fdk-sbb
uv sync --force
```

### Problem: Cache wird nicht erstellt

**Lösung:**

```bash
# Verzeichnisse manuell erstellen
mkdir -p cache/objects

# Berechtigungen prüfen (Linux/macOS)
chmod -R 755 cache
```

### Problem: API-Verbindungsfehler

**Lösung:**

- Prüfen Sie Ihre Internetverbindung
- Die API unter `https://bim-fdk-api.app.sbb.ch` sollte erreichbar sein
- Der Server nutzt automatisch den Cache bei API-Ausfällen

### Problem: Claude erkennt Server nicht

**Lösung:**

1. Prüfen Sie den `cwd`-Pfad in der Konfiguration
2. Stellen Sie sicher, dass `uv` im PATH ist
3. Starten Sie Claude neu
4. Überprüfen Sie die Logs in Claude

**Logs anzeigen:**

- **Claude Desktop**: `Help → View Logs`
- **Claude Code**: VS Code Output Panel → "Claude Code"

---

## 📊 API Referenz

### SBB FDK API

**Base URL:** `https://bim-fdk-api.app.sbb.ch`

**Endpoints:**

- `GET /objects?language={lang}` - Liste aller Objekte
- `GET /objects/{id}?language={lang}` - Objekt-Details

**Unterstützte Sprachen:** `de`, `fr`, `it`, `en`

---

## 🤝 Beitragen

Beiträge sind willkommen! Bitte beachten Sie:

1. Code-Qualitätsstandards einhalten
2. Tests für neue Features schreiben
3. Dokumentation aktualisieren
4. Pull Requests mit klarer Beschreibung erstellen

---

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei für Details.

---

## 👨‍💻 Autor

Erstellt mit Claude Code unter Verwendung von:

- **Python 3.13**
- **MCP SDK 1.18+**
- **FastMCP Framework**
- **Pydantic 2.12+**
- **HTTPX 0.28+**

---

## 🔗 Weiterführende Links

- [Model Context Protocol Dokumentation](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [Claude Code Extension](https://marketplace.visualstudio.com/items?itemName=Anthropic.claude-code)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [SBB FDK API](https://bim-fdk-api.app.sbb.ch/)

---

<div align="center">

**Gebaut mit ❤️ für die SBB Community**

</div>
