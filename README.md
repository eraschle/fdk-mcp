# FDK MCP Server

Ein MCP (Model Context Protocol) Server für den Zugriff auf FDK (Fach-Daten-Katalog) Objekte der SBB.

## Übersicht

Dieser MCP Server ermöglicht AI-Systemen den strukturierten Zugriff auf FDK-Daten sowohl aus lokalen JSON-Dateien als auch über die SBB FDK API. Er bietet umfassende Funktionen für das Suchen, Analysieren und Verwalten von FDK-Objekten.

## Features

- **Lokale JSON-Datei Unterstützung**: Lädt FDK-Objekte aus lokalen JSON-Dateien
- **API Fallback**: Optionaler Zugriff auf die SBB FDK API für fehlende Objekte
- **Referenz-Analyse**: Analysiert Beziehungen zwischen FDK-Objekten
- **Flexible Suche**: Suche nach Name, Domain, Objekttyp
- **Caching**: Intelligentes Caching für API-Anfragen
- **Acht MCP Tools** für verschiedene Anwendungsfälle

## Installation

```bash
# Klonen des Repositories
git clone <repository-url>
cd fdk_mcp

# Installation der Abhängigkeiten mit UV
uv sync

# Test der Installation
uv run python test_server.py
```

## Verfügbare MCP Tools

### 1. `get_fdk_object`
Ruft ein spezifisches FDK-Objekt anhand seiner ID ab.

```json
{
  "object_id": "OBJ_FB_1"
}
```

### 2. `search_fdk_objects`
Sucht nach FDK-Objekten basierend auf verschiedenen Kriterien.

```json
{
  "name_pattern": "Wand",
  "domain": "Hochbau",
  "object_type": "HB",
  "limit": 10
}
```

### 3. `extract_object_id`
Extrahiert die FDK-Objekt-ID aus einem Dateinamen.

```json
{
  "filename": "OBJ_BR_1_Ansicht.png"
}
```

### 4. `analyze_references`
Analysiert Referenz-Beziehungen für ein FDK-Objekt.

```json
{
  "object_id": "OBJ_FB_1",
  "max_depth": 3
}
```

### 5. `get_reference_network`
Erstellt ein Netzwerk von Referenz-Beziehungen.

```json
{
  "start_object_id": "OBJ_FB_1",
  "max_depth": 2
}
```

### 6. `get_domains`
Gibt alle verfügbaren FDK-Domains zurück.

### 7. `get_object_types`
Gibt alle verfügbaren FDK-Objekttypen zurück.

### 8. `get_all_objects`
Gibt alle geladenen FDK-Objekte zurück.

```json
{
  "summary_only": true
}
```

## Konfiguration

Der Server kann über die `FDKServerConfig` Klasse konfiguriert werden:

```python
config = FDKServerConfig(
    data_directory="data/sample",
    api_base_url="https://bim-fdk-api.app.sbb.ch",
    api_language="de",
    cache_ttl_seconds=3600,
    enable_api_fallback=True,
    max_search_results=100,
    log_level="INFO"
)
```

## Datenstruktur

Das System unterstützt FDK-Objekte mit folgender Struktur:

- **ID**: Eindeutige Objekt-ID (z.B. `OBJ_FB_1`)
- **Name**: Objektname (z.B. "Gleisrost")
- **Domain**: Fachbereich (z.B. "Fahrbahn")
- **Beschreibung**: Detaillierte Objektbeschreibung
- **Beziehungen**: Komponent- und Assembly-Beziehungen

## Verwendung

### Als MCP Server starten

```bash
uv run python main.py
```

### Für Tests

```bash
uv run python test_server.py
```

### Programmtische Verwendung

```python
from src.fdk_mcp import FDKDataProvider, FDKServerConfig

config = FDKServerConfig(data_directory="data/sample")
provider = FDKDataProvider(config)

await provider.initialize()
objects = await provider.get_all_objects()
```

## Unterstützte Domains

Das System arbeitet mit folgenden FDK-Domains:

- **FB** (Fahrbahn): Gleisbau-Objekte
- **BR** (Brücken): Brückenbau-Objekte  
- **HB** (Hochbau): Hochbau-Objekte
- **EN** (Energie): Energie-Objekte

## Entwicklung

### Linting und Type Checking

```bash
uv run ruff check .
uv run pyright .
```

### Tests ausführen

```bash
uv run python test_server.py
```

## Lizenz

[Lizenz-Information hier einfügen]