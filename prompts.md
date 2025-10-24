# MCP Prompts - Vorschläge für SBB FDK Server

Dieses Dokument enthält Vorschläge für MCP Prompts, die für den SBB FDK MCP Server implementiert werden könnten. Diese Prompts sind **NICHT implementiert**, da die vorhandenen Tools bereits optimal für den Use-Case sind.

## Warum keine Prompts?

**Entscheidung:** Prompts werden NICHT implementiert, weil:

1. **Tools sind bereits optimal** - Alle benötigten Funktionen sind als Tools verfügbar
2. **Kein Mehrwert** - Prompts würden nur die vorhandenen Tools aufrufen
3. **Höhere Komplexität** - Zusätzliche Abstraktion ohne praktischen Nutzen
4. **User Control** - Tools geben der AI mehr Kontrolle über Workflow

## Vorgeschlagene Prompts (Referenz)

Falls in Zukunft Prompts gewünscht werden, hier sind sinnvolle Kandidaten:

### 1. `fdk_object_analysis`

**Beschreibung:** Führe eine detaillierte Analyse eines FDK-Objekts durch

**Parameter:**

- `object_id` (required): Die ID des zu analysierenden Objekts
- `focus` (optional): Fokusbereich (properties, relationships, metadata)
- `language` (optional): Sprache (de/fr/it/en)

**Workflow:**

1. Rufe sbb_fdk_get_object auf
2. Analysiere die Struktur und PropertySets
3. Identifiziere wichtige Eigenschaften
4. Gebe strukturierte Zusammenfassung

**Beispiel:**

```python
@mcp.prompt()
def fdk_object_analysis(object_id: str, focus: str = "all", language: str = "de"):
    return f"""Analysiere das FDK-Objekt {object_id}:

1. Verwende sbb_fdk_get_object(object_id="{object_id}", language="{language}")
2. Untersuche die folgenden Aspekte:
   - Grundlegende Metadaten (Name, Domain, Beschreibung)
   - PropertySets und ihre Struktur
   - Wichtige Properties mit Beispielwerten
   - Beziehungen zu anderen Objekten (componentRelationships, assemblyRelationships)
   - IFC-Zuweisungen und eBKP-Konzepte

3. Erstelle eine strukturierte Zusammenfassung mit:
   - Hauptzweck des Objekts
   - Wichtigste Properties (Top 5-10)
   - Besonderheiten oder Auffälligkeiten
   - Empfehlungen für die Verwendung

Fokus: {focus}
"""
```

---

### 2. `property_comparison`

**Beschreibung:** Vergleiche Properties zwischen mehreren FDK-Objekten

**Parameter:**

- `object_ids` (required): Liste von Objekt-IDs (Komma-getrennt)
- `property_focus` (optional): Spezifische Property-Namen zum Vergleichen
- `language` (optional): Sprache

**Workflow:**

1. Lade alle angegebenen Objekte
2. Extrahiere gemeinsame und unterschiedliche PropertySets
3. Vergleiche spezifische Properties
4. Erstelle Vergleichstabelle

---

### 3. `domain_exploration`

**Beschreibung:** Entdecke und verstehe eine Domain systematisch

**Parameter:**

- `domain_name` (required): Name der zu explorierenden Domain
- `depth` (optional): Tiefe der Analyse (quick, normal, deep)

**Workflow:**

1. Liste alle Objekte der Domain auf
2. Gruppiere nach ObjectGroups
3. Identifiziere häufige PropertySets
4. Erstelle Domain-Übersicht

**Beispiel:**

```python
@mcp.prompt()
def domain_exploration(domain_name: str, depth: str = "normal"):
    return f"""Exploriere die FDK-Domain "{domain_name}" systematisch:

1. Verwende sbb_fdk_list_objects(domain="{domain_name}", limit=100)
2. Analysiere die Objektstruktur:
   - Wie viele Objekte gibt es?
   - Welche ObjectGroups existieren?
   - Welche Subgroups gibt es?

3. Untersuche repräsentative Objekte:
   - Wähle 3-5 typische Objekte aus verschiedenen Gruppen
   - Analysiere ihre PropertySets
   - Identifiziere gemeinsame Muster

4. Erstelle Domain-Profil:
   - Hauptzweck der Domain
   - Typische Anwendungsfälle
   - Wichtigste Properties
   - Besondere Merkmale

Analysetiefe: {depth}
"""
```

---

### 4. `cache_health_check`

**Beschreibung:** Überprüfe Cache-Status und gebe Optimierungsempfehlungen

**Parameter:**

- Keine

**Workflow:**

1. Prüfe Cache-Statistiken
2. Analysiere Freshness
3. Empfehle Actions (refresh, download, update)

**Beispiel:**

```python
@mcp.prompt()
def cache_health_check():
    return """Führe einen Cache-Health-Check durch:

1. Verwende sbb_fdk_get_cache_stats()
2. Analysiere:
   - Ist der Cache fresh? (< 24h alt)
   - Wie viele Objekte sind gecacht?
   - Welche Release-Version ist gespeichert?

3. Prüfe Vollständigkeit:
   - Verwende sbb_fdk_list_domains()
   - Sind alle Domains vertreten?
   - Gibt es fehlende Objects?

4. Empfehlungen:
   - Falls nicht fresh: "Cache refresh empfohlen"
   - Falls Objekte fehlen: "Cache-Update mit sbb_fdk_update_cache"
   - Falls leer: "Vollständiger Download mit sbb_fdk_download_all_objects"
   - Falls alles OK: "Cache ist gesund"

Gebe einen übersichtlichen Health-Report.
"""
```

---

### 5. `bulk_download_plan`

**Beschreibung:** Erstelle einen optimalen Download-Plan mit Zeitabschätzung

**Parameter:**

- `domains` (optional): Spezifische Domains (Komma-getrennt)
- `parallel_downloads` (optional): Anzahl paralleler Downloads (1-20)

**Workflow:**

1. Analysiere was bereits gecacht ist
2. Berechne fehlende Objects
3. Schätze Download-Zeit
4. Erstelle Download-Plan

**Beispiel:**

```python
@mcp.prompt()
def bulk_download_plan(domains: str | None = None, parallel_downloads: int = 10):
    domains_list = domains.split(",") if domains else ["alle Domains"]

    return f"""Erstelle einen optimalen Download-Plan:

1. Analysiere aktuelle Situation:
   - Verwende sbb_fdk_get_cache_stats()
   - Verwende sbb_fdk_list_domains()
   - Berechne: Was ist bereits vorhanden?

2. Definiere Ziel:
   - Domains: {", ".join(domains_list)}
   - Parallelität: {parallel_downloads} gleichzeitige Downloads

3. Berechne Aufwand:
   - Anzahl zu ladender Objekte
   - Geschätzte Zeit (ca. 0.3s pro Objekt bei parallel=10)
   - Geschätzter Speicherbedarf

4. Empfehlung:
   - Falls nur wenige fehlen: "sbb_fdk_update_cache"
   - Falls viele fehlen: "sbb_fdk_download_all_objects"
   - Optimale Parameter angeben

5. Erstelle ausführbaren Plan mit konkreten Tool-Calls
"""
```

---

## Best Practices für Prompt-Design

Falls Prompts in Zukunft implementiert werden:

### 1. **User Control**

- Prompts sind User-controlled, nicht AI-controlled
- Explizite Aktivierung erforderlich

### 2. **Clear Parameters**

- Wenige, klare Parameter
- Gute Default-Werte
- Validierung in der Prompt-Definition

### 3. **Structured Output**

- Klare Struktur vorgeben
- Schritte nummerieren
- Erwartete Tool-Calls auflisten

### 4. **Reusability**

- Allgemein genug für verschiedene Kontexte
- Parametrisierbar für Anpassung

### 5. **Tool Integration**

- Prompts rufen vorhandene Tools auf
- Keine Duplikation von Tool-Logik

## Implementierungs-Beispiel (wenn gewünscht)

```python
# In server.py

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sbb_fdk_mcp")

@mcp.prompt()
async def fdk_object_analysis(
    object_id: str,
    focus: str = "all",
    language: str = "de"
) -> list[dict]:
    """Analysiere ein FDK-Objekt detailliert."""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""Analysiere das FDK-Objekt {object_id}:

1. Verwende sbb_fdk_get_object(object_id="{object_id}", language="{language}")
2. Untersuche: Metadaten, PropertySets, Properties, Relationships
3. Erstelle strukturierte Zusammenfassung

Fokus: {focus}
"""
            }
        }
    ]
```

## Fazit

Die vorhandenen **Tools** sind für den SBB FDK MCP Server optimal:

✅ **Tools bieten:**

- Direkte Aktionen
- Flexible Parameter
- Type-Safety mit Pydantic
- Klare Rückgabewerte

❌ **Prompts würden bieten:**

- Nur Template-Text
- Umweg über Tools
- Zusätzliche Komplexität
- Keinen praktischen Mehrwert

**Empfehlung:** Bei den Tools bleiben!
