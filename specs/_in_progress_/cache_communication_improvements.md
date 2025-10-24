# Cache Communication Improvements

**Status:** Analysis & Recommendations
**Date:** 2025-10-24
**Priority:** Medium

---

## Problem Statement

Claude AI muss besser darüber informiert werden, wann Operationen lange dauern können, weil Objekte zuerst heruntergeladen werden müssen. Aktuell:

✅ **Gut:** `fdk_get_cache_coverage` Tool existiert und hat gute Dokumentation
❌ **Problem:** Andere Tools verweisen nicht darauf, dass man dieses Tool zuerst nutzen sollte

---

## Aktuelle Situation

### Tool: `fdk_get_cache_coverage` ✅

**Status:** Sehr gut dokumentiert!

**Features:**
- Zeigt Cache-Coverage (wie viele Objekte cached sind)
- Schätzt Download-Zeit
- Gibt klare Empfehlungen

**Dokumentation:**
```
⚡ USE THIS BEFORE expensive operations to inform the user!

💡 PROACTIVE COMMUNICATION PATTERN:
1. Call this tool to check cache coverage
2. If download time > 10 seconds, inform the user!
3. Ask if they want to proceed
```

### Tools die Downloads auslösen können

#### 1. `fdk_advanced_search` 🔶
**Aktuell (Zeile 379):**
```
- Auto-downloads missing data transparently
```

**Problem:** Kein Hinweis auf `get_cache_coverage`

#### 2. `fdk_search_properties` 🔶
**Status:** Unbekannt - muss überprüft werden

#### 3. `fdk_get_object` 🔶
**Status:** Unbekannt - muss überprüft werden

#### 4. `fdk_download_all_objects` ✅
**Status:** Vermutlich gut dokumentiert (ist explizit ein Download-Tool)

#### 5. `fdk_update_cache` ✅
**Status:** Vermutlich gut dokumentiert (ist explizit ein Download-Tool)

---

## Empfohlene Verbesserungen

### Strategie 1: Cross-References hinzufügen ⭐

Füge zu allen Tools die Downloads auslösen können einen Hinweis hinzu:

```python
async def fdk_advanced_search(...):
    """Advanced search across ANY JSON field in FDK objects.

    ⚠️ PERFORMANCE NOTE:
    This tool auto-downloads missing object details. For large result sets,
    use fdk_get_cache_coverage FIRST to estimate download time and inform the user!

    💡 RECOMMENDED WORKFLOW:
    1. Call fdk_get_cache_coverage(domain_filter="YourDomain")
    2. If estimated_download_time > 10 seconds:
       → Inform user: "This will download X objects (~Y seconds). Proceed?"
    3. User confirms
    4. Run this search

    [Rest der Dokumentation...]
    """
```

### Strategie 2: Tool Annotations erweitern

Nutze MCP Tool Annotations, um Warnung anzuzeigen:

```python
@mcp.tool(
    name="fdk_advanced_search",
    annotations=ToolAnnotations(
        title="Advanced Search",
        readOnlyHint=False,  # Downloads data!
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
        performanceHint="May download objects if not cached. Use fdk_get_cache_coverage first!",  # Neu?
    ),
)
```

**Hinweis:** Prüfen ob `performanceHint` existiert oder custom annotation möglich ist.

### Strategie 3: Explizite Empfehlung im Prompt

Erweitere die Tool-Beschreibung mit klarem Workflow:

```python
"""
⚡ EFFICIENCY PATTERN (IMPORTANT):

BEFORE searching in PropertySets or detailed fields:
Step 1: Check cache coverage
    → fdk_get_cache_coverage(domain_filter="YourDomain")

Step 2: Evaluate estimated_download_time
    → If > 10 seconds: Inform user and ask for confirmation
    → Example: "This search needs to download 500 objects (~1 min). Continue?"

Step 3: Only then run the actual search
    → fdk_advanced_search(query="...", domain_filter="...")

WHY: First-time searches trigger downloads. Subsequent searches are instant!
"""
```

---

## Konkrete Änderungen

### Priorität 1: `fdk_advanced_search` erweitern

**Datei:** `src/fdk_mcp/server.py` (ca. Zeile 280-381)

**Aktuell:**
```python
Performance:
    - Searches entire catalog in seconds
    - Auto-downloads missing data transparently
    - Much faster than manual iteration!
```

**Neu:**
```python
⚡ PERFORMANCE & CACHING:
    - Searches entire catalog in seconds
    - Auto-downloads missing data if not cached
    - First search may take 30s-2min if many objects need download
    - Subsequent searches are instant!

💡 RECOMMENDED: Check cache first!
    Step 1: coverage = fdk_get_cache_coverage(domain_filter="YourDomain")
    Step 2: IF coverage.estimated_download_time > 10 seconds:
            → Inform user: "Will download X objects (~Y seconds). Proceed?"
    Step 3: User confirms → Run search

    This prevents surprising delays and improves UX!
```

### Priorität 2: `fdk_search_properties` erweitern

**Datei:** `src/fdk_mcp/server.py` (Property Search Tool)

**Hinzufügen:**
```python
⚠️ DOWNLOAD NOTE:
    This searches PropertySets which require object details.
    If objects aren't cached, they will be downloaded automatically.

    For large searches, use fdk_get_cache_coverage first to estimate time!
```

### Priorität 3: `fdk_get_object` erweitern

**Datei:** `src/fdk_mcp/server.py` (Get Object Tool)

**Hinzufügen:**
```python
⚡ CACHING:
    - Cached objects: <1ms response time
    - Uncached objects: ~100ms download time
    - Cache persists between sessions

    For bulk operations, consider fdk_update_cache to pre-download.
```

---

## Beispiel-Workflow (Ideal)

### User fragt:
> "Find all objects with PropertySet 'SBB-CFF-FFS_PO' in domain 'Hochbau'"

### Claude antwortet (NEU mit besserer Dokumentation):

```
Let me check the cache first to estimate how long this will take.

[Calls: fdk_get_cache_coverage(domain_filter="Hochbau")]

Cache Analysis:
- Total objects in Hochbau: 550
- Cached with details: 50 (9%)
- Need to download: 500 (91%)
- Estimated download time: ~1 minute

This search will download 500 objects (about 1 minute).
Would you like me to proceed?

[User: Yes]

Proceeding with download and search...
[Calls: fdk_advanced_search(...)]
```

### Claude antwortet (ALT - ohne Warnung):

```
[Calls: fdk_advanced_search(...)]
[Läuft 1 Minute ohne Feedback]
[User fragt sich: "Ist es abgestürzt?"]
```

---

## Testing Strategy

Nach Implementierung testen:

1. **Scenario 1: Leerer Cache**
   - User fragt nach Property-Suche
   - Claude sollte `get_cache_coverage` aufrufen
   - Claude sollte User warnen vor Download

2. **Scenario 2: Voller Cache**
   - User fragt nach Property-Suche
   - Claude kann direkt suchen (kein Download nötig)
   - Antwort kommt sofort

3. **Scenario 3: Teilweise gecacht**
   - User fragt nach domänen-spezifischer Suche
   - Claude nutzt `domain_filter` in coverage-check
   - Claude schätzt korrekte Download-Zeit

---

## Metrics für Erfolg

**Vorher:**
- User beschwert sich über lange Wartezeiten
- Keine Transparenz über Download-Prozess
- Claude lädt ohne Warnung herunter

**Nachher:**
- Claude checkt proaktiv Cache-Coverage
- User wird informiert über geschätzte Dauer
- User kann entscheiden ob fortfahren
- Transparenz verbessert UX

---

## Implementation Checklist

- [x] **Step 1:** `fdk_advanced_search` Dokumentation erweitern ✅ (2025-10-24)
- [x] **Step 2:** `fdk_search_properties` Dokumentation erweitern ✅ (2025-10-24)
- [x] **Step 3:** `fdk_get_object` Dokumentation erweitern ✅ (2025-10-24)
- [ ] **Step 4:** Test mit Claude: Trigger Scenarios testen
- [ ] **Step 5:** User Feedback sammeln
- [ ] **Step 6:** Iterieren basierend auf Feedback

## Implementation Details (2025-10-24)

### Changes Applied

**File:** `src/fdk_mcp/server.py`

1. **fdk_advanced_search** (Lines 377-401)
   - Added "⚡ PERFORMANCE & CACHING" section
   - Added "💡 RECOMMENDED" workflow with 3 steps
   - Explains first-time vs. subsequent search performance
   - Example user communication

2. **fdk_search_properties** (Lines 187-201)
   - Added "⚠️ DOWNLOAD NOTE"
   - Added "💡 RECOMMENDED" 3-step workflow
   - Added "⚡ PERFORMANCE" timing information
   - Clear distinction: cached vs. uncached performance

3. **fdk_get_object** (Lines 133-151)
   - Added "⚡ CACHING" section with timing info
   - Added "💡 FOR BULK OPERATIONS" guidance
   - Example workflow for bulk object retrieval
   - Updated examples with more details

**Test Results:**
- ✅ Server imports successfully
- ✅ 169/169 tests pass
- ✅ No breaking changes

---

## Geschätzter Aufwand

- **Dokumentation schreiben:** 30 Minuten
- **Testing:** 20 Minuten
- **Total:** ~1 Stunde

**Impact:** Hoch - verbessert User Experience signifikant!

---

## Alternative Lösung: Automatisches Checking

**Idee:** Tools könnten automatisch Coverage checken und User warnen.

**Vorteil:** Claude muss nicht daran denken
**Nachteil:** Mehr Overhead, komplexere Implementierung

**Beispiel-Code:**
```python
async def fdk_advanced_search(params, ctx):
    # Auto-check coverage if search involves PropertySets
    if needs_property_sets(params.search_fields):
        coverage = await check_coverage_quick()
        if coverage.download_time > 10:
            await ctx.warning(
                f"This search will download {coverage.missing_count} objects "
                f"(~{coverage.download_time}s). Consider using fdk_update_cache first."
            )

    # Continue with search...
```

**Entscheidung:** Erstmal mit Dokumentation starten, später auto-checking evaluieren.

---

**Nächste Schritte:**
1. Dokumentation erweitern (diese Datei als Basis)
2. PR erstellen mit Tool-Beschreibungs-Updates
3. Mit echtem Claude testen
4. User Feedback einholen

---

**Verantwortlich:** Elyo
**Review:** Nach Implementierung
**Related:** `specs/_in_progress_/fdk_tool_improvements.md`
