# FDK MCP Tools - Verbesserungsvorschläge für Tool-Beschreibungen

## Kontext & Problemstellung

### Ausgangssituation

In einer Analyse-Session haben wir untersucht, welche Domains im SBB FDK Katalog 100% Abdeckung des PropertySets "SBB-CFF-FFS_PO" haben.

### Beobachtetes Problem

Claude hat zunächst einen **ineffizienten Ansatz** gewählt:

1. Globale Suche mit `limit=200` → 200 von 1416 Objekten zurück
2. Output war viel zu lang (mehrere Seiten Markdown)
3. Überlegung, Python-Script zu schreiben um zu iterieren
4. Erst nach Nachdenken: **Besserer Ansatz entdeckt**

### Die effiziente Lösung

```python
# Für jede Domain einzeln:
result = advanced_search(
    query="SBB-CFF-FFS_PO",
    domain_filter=domain,
    limit=1  # ← Nur Metadaten holen!
)
count = result['total']  # ← Zählung ohne alle Daten zu fetchen
```

**Resultat:** Nur 17 Tool-Calls statt tausende von Objekten zu verarbeiten!

### Kernproblem

Claude hat nicht sofort erkannt, dass:

- Das `total` Feld im Response die Gesamtzahl enthält
- `limit=1` ausreicht um zu zählen
- Die Tools bereits die benötigte Funktionalität bieten

---

## Warum passiert das?

### Psychologische Faktoren

1. **Iteratives Denken**: "Ich brauche alle Daten" → Erst später: "Moment, nur Counts!"
2. **Tool-Discovery**: Muss erst Response sehen um `total` zu entdecken
3. **Gewohnheit**: Von anderen APIs gewohnt, Daten erst zu fetchen um zu zählen
4. **Kognitive Last**: Bei komplexen Aufgaben nicht an Optimierung gedacht

### Design-Problem

Die Tool-Beschreibungen erklären nicht deutlich genug:

- Welche Felder im Response verfügbar sind
- Wie man effizient zählt/aggregiert
- Best Practices für häufige Use-Cases
- Wann man welches Tool verwendet

---

## Lösungsansätze

### 1. Explizite Hinweise in Tool-Beschreibungen

```
IMPORTANT: Before writing custom code to iterate or aggregate data,
ALWAYS check if the tool already provides this functionality.
```

### 2. Konkrete Beispiele für Use-Cases

```
EXAMPLE - Counting objects per domain:
  list_objects(domain="Hochbau", limit=1)
  → Returns: {"total": 550, "count": 1, ...}
  → Use 'total' field for count!
```

### 3. Response-Struktur dokumentieren

```
RESPONSE STRUCTURE:
{
  "total": 1416,      ← Total matches (always present)
  "count": 200,       ← Items in this response
  "data": [...]       ← Actual objects (only if limit > 0)
}
```

### 4. Efficiency Patterns hervorheben

Mit Symbolen (💡⚡⚠️✓✗) für schnelles Scannen

### 5. DO/DON'T Listen

Klare Guidance was zu tun und zu vermeiden ist

---

## Detaillierte Tool-Verbesserungen

### Tool 1: sbb_fdk_list_objects

**Aktuell:**

```
Search and filter objects from the SBB FDK catalog with pagination.
Use this when exploring available objects or searching by criteria.
```

**Verbessert:**

```
Search and filter objects from the SBB FDK catalog with pagination.
Use this when exploring available objects or searching by criteria.

💡 EFFICIENCY TIPS:
- To count objects in a domain: Use limit=1 and read 'total' from response
- To check if objects exist: Use limit=1, check if total > 0
- To browse: Use limit=20 (default) with pagination
- Only use high limits (50-100) when you actually need all the data

EXAMPLE - Counting objects per domain:
  list_objects(domain="Hochbau", limit=1)
  → Returns: {"total": 550, "count": 1, ...}
  → Use 'total' field, not 'count'!

PARAMETERS:
- domain: Filter by domain name
- search: Search term for names
- limit: Max results (1-100, default 20)
- offset: Skip results (default 0)
- detail: concise or detailed
- response_format: markdown or json
```

---

### Tool 2: sbb_fdk_get_object

**Aktuell:**

```
Retrieve full object information including PropertySets,
Properties, relationships, and metadata.
```

**Verbessert:**

```
Retrieve full object information including PropertySets,
Properties, relationships, and metadata.

⚠️ PERFORMANCE NOTE:
This returns complete object details (~5-20KB per object).
For bulk operations, consider:
- Use sbb_fdk_advanced_search to filter first
- Use sbb_fdk_list_objects to get overview first
- Only call get_object for specific objects you need to inspect

WHEN TO USE:
✓ Inspecting a specific object's complete properties
✓ Getting detailed PropertySet values
✓ Analyzing relationships of 1-5 objects
✗ Iterating through hundreds of objects (use search instead)

EXAMPLE:
  get_object(object_id="OBJ_FB_1", language="de")
  → Returns complete object with all PropertySets and Properties

PARAMETERS:
- object_id: Object ID (e.g., 'OBJ_BR_1') [REQUIRED]
- language: Language code (de/fr/it/en, default: de)
- response_format: markdown or json
```

---

### Tool 3: sbb_fdk_search_properties

**Aktuell:**

```
Find properties by name across the entire catalog,
showing context (object, PropertySet) for each match.
```

**Verbessert:**

```
Find properties by name across the entire catalog,
showing context (object, PropertySet) for each match.

USE CASES:
✓ "Which objects have property 'Breite'?"
✓ "Find all temperature-related properties"
✓ "What PropertySets contain 'Material'?"

💡 SEARCH STRATEGY:
- Start with specific terms ("Temperatur")
- Broaden if needed ("Temp")
- Use limit to control results (default: 20)

NOTE: Searches across ALL 1687 objects. For domain-specific
searches, use sbb_fdk_advanced_search with domain_filter.

EXAMPLE:
  search_properties(query="Breite", limit=20)
  → Returns properties named "Breite" with their context

PARAMETERS:
- query: Search term (min 1 char) [REQUIRED]
- limit: Max results (1-100, default: 20)
- response_format: markdown or json
```

---

### Tool 4: sbb_fdk_advanced_search ⭐

**Aktuell:**

```
Advanced search across ANY JSON field in FDK objects.

IMPORTANT: Use this tool instead of writing Python loops or custom search code!
This tool efficiently searches across all data with automatic detail loading.
```

**Verbessert:**

```
Advanced search across ANY JSON field in FDK objects.

🚀 IMPORTANT: Use this tool instead of writing Python loops or custom search code!
This tool efficiently searches across all data with automatic detail loading.

⚡ EFFICIENCY PATTERNS:

1️⃣ COUNTING (most efficient):
   advanced_search(query="X", domain_filter="Y", limit=1)
   → Read response['total'] for count
   → Example: "How many objects in Hochbau have PropertySet X?"

2️⃣ EXISTENCE CHECK:
   advanced_search(query="X", limit=1)
   → Check if response['total'] > 0

3️⃣ AGGREGATION BY DOMAIN:
   for domain in domains:
       result = advanced_search(query="X", domain_filter=domain, limit=1)
       counts[domain] = result['total']
   → Example: "Which domains have PropertySet X?"

4️⃣ ACTUAL DATA NEEDED:
   advanced_search(query="X", limit=50)
   → Only use high limits when you need the actual data

❌ DON'T:
- Fetch limit=200 just to count: len(results)
- Write loops to process results: Use limit=1 + 'total' field
- Make multiple large queries: Use domain_filter to narrow down

✅ DO:
- Use limit=1 for counting/checking
- Use domain_filter to scope searches
- Use response['total'] for aggregations
- Only fetch data you actually need

RESPONSE STRUCTURE:
{
  "total": 1416,      ← Total matches (always present)
  "count": 200,       ← Items in this response
  "data": [...]       ← Actual objects (only if limit > 0)
}

SEARCH FIELDS:
- "all": All searchable fields
- "propertySets": PropertySet names
- "properties": Property names and values
- "ifcClassAssignments": IFC classes
- "ebkpConcepts": eBKP codes
- "aksCode": AKS codes
- "componentRelationships": Component relations
- "assemblyRelationships": Assembly relations
- "domainModel": Domain information
- "nameObjectGroup": Object group names
- "nameSubgroup": Subgroup names

PARAMETERS:
- query: Search term [REQUIRED]
- search_fields: Which fields to search (default: ["all"])
- domain_filter: Optional domain restriction
- match_mode: contains/equals/starts_with/ends_with (default: contains)
- case_sensitive: Case-sensitive search (default: False)
- limit: Max results (1-200, default: 50)
- response_format: markdown or json
```

---

### Tool 5: sbb_fdk_download_all_objects

**Aktuell:**

```
Downloads complete detail data for FDK objects with parallel processing,
including propertySets, relationships, and full metadata.
This enables fast local searches using ripgrep/grep.
```

**Verbessert:**

```
Downloads complete detail data for FDK objects with parallel processing,
including propertySets, relationships, and full metadata.
This enables fast local searches using ripgrep/grep.

⚠️ HEAVY OPERATION WARNING:
- Downloads ~100MB of data
- Takes 2-3 minutes for all objects
- Useful for offline analysis or local searches

BEFORE YOU CALL THIS:
Ask yourself: "Do I really need ALL objects with ALL details?"

Consider these alternatives first:
- sbb_fdk_advanced_search: For targeted queries
- sbb_fdk_list_objects: For overviews
- sbb_fdk_update_cache: For incremental updates

WHEN TO USE:
✓ Setting up for extensive offline analysis
✓ Building local database/index
✓ Need complete data for >100 objects
✗ Just counting/checking (use advanced_search instead)
✗ Analyzing <20 objects (use get_object instead)

TIP: Use domain_filter to download only relevant domains
Example: domain_filter="Hochbau" (~50MB instead of 100MB)

PARAMETERS:
- language: Language code (de/fr/it/en, default: de)
- domain_filter: Optional domain filter (e.g., "Hochbau", "Brücken")
- max_concurrent: Max parallel requests (default: 10, range: 1-20)
- response_format: markdown or json

PERFORMANCE:
- All 1687 objects: ~2-3 minutes (parallel)
- Single domain: <1 minute
- Requires ~100MB disk space for all
```

---

### Tool 6: sbb_fdk_update_cache

**Aktuell:**

```
Intelligently updates cache by downloading only:
- New objects not yet cached
- Summary-only objects (without propertySets)
- All objects if force_refresh=True
```

**Verbessert:**

```
Intelligently updates cache by downloading only:
- New objects not yet cached
- Summary-only objects (without propertySets)
- All objects if force_refresh=True

💡 SMART UPDATE STRATEGY:
This tool is MUCH faster than download_all_objects if cache exists,
because it only downloads what's missing.

WORKFLOW:
1. First run: Downloads everything (like download_all_objects)
2. Subsequent runs: Only downloads new/incomplete objects
3. With force_refresh=True: Re-downloads everything

USE CASES:
✓ Daily/weekly cache refresh
✓ After catalog updates
✓ When unsure if cache is current
✗ First-time setup (use download_all_objects for clarity)

EXAMPLE WORKFLOW:
1. Initial setup:
   download_all_objects(language="de")

2. Regular updates:
   update_cache(language="de")
   → Only downloads new/changed objects

3. Force refresh:
   update_cache(language="de", force_refresh=True)
   → Re-downloads everything

PARAMETERS:
- language: Language code (de/fr/it/en, default: de)
- domain_filter: Update only specific domain
- force_refresh: Re-download all objects (default: False)
- max_concurrent: Speed control (1-20, default: 10)
- response_format: markdown or json

PERFORMANCE:
- Much faster than full download if cache exists
- Only downloads what's missing
- Safe to run regularly
- Parallel processing for speed
```

---

### Tool 7: sbb_fdk_list_domains

**Aktuell:**

```
List all domains with object counts.
Get overview of catalog organization by domain.
```

**Verbessert:**

```
List all domains with object counts.
Get overview of catalog organization by domain,
showing how many objects exist in each category.

USE CASES:
✓ Get overview of catalog structure
✓ Find which domains have most objects
✓ Understand domain distribution
✓ Plan domain-specific analysis

EXAMPLE OUTPUT:
- Hochbau: 550 objects (32.6%)
- Energie: 302 objects (17.9%)
- Sicherungsanlagen: 134 objects (7.9%)
...

💡 TIP: Use this before domain-specific searches to understand
the catalog structure and decide which domains to focus on.

RETURNS:
- List of all 17 domains
- Object count per domain
- Percentage distribution
- Total catalog size (1687 objects)

NO PARAMETERS REQUIRED
```

---

### Tool 8: sbb_fdk_refresh_cache

**Aktuell:**

```
Force cache refresh from API.
Manually trigger cache update from the FDK API.
Normally cache auto-refreshes every 24 hours.
```

**Verbessert:**

```
Force cache refresh from API.
Manually trigger cache update from the FDK API.
Normally cache auto-refreshes every 24 hours.

⚠️ USE SPARINGLY:
The cache automatically refreshes every 24 hours.
Only use this tool if:
- You know the catalog was just updated
- The cache seems stale/corrupted
- Testing cache functionality

DIFFERENCE FROM update_cache:
- refresh_cache: Reloads summary data (fast, <1 second)
- update_cache: Downloads missing detail objects (slower, minutes)

WORKFLOW:
1. Cache loads automatically on first use
2. Auto-refreshes every 24 hours
3. Call refresh_cache only if needed
4. Call update_cache to get detail objects

💡 TIP: You usually don't need to call this manually.
The cache management is automatic.

NO PARAMETERS REQUIRED

RETURNS:
Cache update status with timestamp and object count
```

---

### Tool 9: sbb_fdk_get_cache_stats

**Aktuell:**

```
Get cache statistics and status.
View cache metadata including last update time,
object count, and freshness status.
```

**Verbessert:**

```
Get cache statistics and status.
View cache metadata including last update time,
object count, and freshness status.

USE CASES:
✓ Check when cache was last updated
✓ Verify cache is working
✓ Debug cache issues
✓ See cache size and coverage

EXAMPLE OUTPUT:
{
  "last_update": "2025-01-20T14:30:00Z",
  "object_count": 1687,
  "cache_age_hours": 2.5,
  "is_fresh": true,
  "detail_objects": 1416,
  "summary_only": 271
}

💡 TIP: Use this to understand cache state before deciding
whether to call update_cache or refresh_cache.

NO PARAMETERS REQUIRED

RETURNS:
- Last update timestamp
- Total object count
- Cache age in hours
- Freshness status
- Detail vs summary object counts
```

---

## Design-Prinzipien für Tool-Beschreibungen

### 1. Visuelle Hierarchie

```
🚀 Wichtigste Information zuerst
💡 Tipps und Best Practices
⚠️ Warnungen
✓ Was man tun sollte
✗ Was man vermeiden sollte
```

### 2. Struktur

1. **Kurze Beschreibung** (1-2 Sätze)
2. **Use Cases** (Wann verwenden?)
3. **Efficiency Tips** (Wie optimal nutzen?)
4. **Examples** (Konkrete Beispiele)
5. **Parameters** (Was kann man einstellen?)
6. **Response Structure** (Was kommt zurück?)

### 3. Konkrete Beispiele

Nicht: "Use limit parameter to control results"
Sondern: "Use limit=1 to count: response['total']"

### 4. Vergleiche und Abgrenzungen

"This tool vs. that tool" Abschnitte
"When to use X vs. Y"

### 5. Performance-Hinweise

Explizit erwähnen wenn etwas:

- Schnell ist (< 1 Sekunde)
- Zeit braucht (Minuten)
- Viel Daten lädt (MB)

---

## Implementierungs-Checkliste

Für jedes Tool prüfen:

- [ ] Efficiency Tips vorhanden?
- [ ] Response-Struktur dokumentiert?
- [ ] Konkrete Beispiele mit echten Werten?
- [ ] DO/DON'T Liste?
- [ ] Use Cases klar beschrieben?
- [ ] Abgrenzung zu ähnlichen Tools?
- [ ] Performance-Charakteristik erwähnt?
- [ ] Visuelle Marker (Symbole) verwendet?
- [ ] Parameter vollständig dokumentiert?
- [ ] Häufige Fehler/Antipatterns erwähnt?

---

## Messung des Erfolgs

### Vorher (aktuelles Verhalten)

- Ineffiziente erste Versuche
- Trial-and-error bei Tool-Auswahl
- Unnötige Daten-Downloads
- Umweg über Python-Scripts

### Nachher (gewünschtes Verhalten)

- Direkter Griff zum richtigen Tool
- Effiziente Parameter-Wahl (limit=1 für Counts)
- Nutzung von Response-Metadaten (total field)
- Weniger Tool-Calls, bessere Performance

### Metriken

- Anzahl Tool-Calls für typische Aufgaben
- Datenmenge die transferiert wird
- Zeit bis zur korrekten Lösung
- Häufigkeit von "Umwegen" über Code

---

## Nächste Schritte

1. **Tool-Beschreibungen aktualisieren**
   - Jedes Tool einzeln durchgehen
   - Neue Struktur anwenden
   - Beispiele aus echten Use-Cases

2. **Testen mit Claude**
   - Typische Aufgaben stellen
   - Beobachten welche Tools gewählt werden
   - Parameter-Wahl prüfen

3. **Iterieren**
   - Feedback sammeln
   - Schwachstellen identifizieren
   - Beschreibungen verbessern

4. **Dokumentation**
   - Separate "Best Practices" Sektion?
   - Tutorial-Dokument?
   - Häufige Patterns dokumentieren?

---

## Konkrete Use-Case Beispiele

### Use-Case 1: "Welche Domains haben PropertySet X?"

```python
# Ineffizient (alt):
all_results = advanced_search(query="X", limit=200)  # Zu viele Daten!
# ... dann manuell gruppieren nach Domain

# Effizient (neu mit besserer Doku):
domains = list_domains()
for domain in domains:
    result = advanced_search(
        query="X",
        domain_filter=domain,
        limit=1  # Nur Metadaten!
    )
    print(f"{domain}: {result['total']} objects")
```

### Use-Case 2: "Hat Domain X das PropertySet Y?"

```python
# Ineffizient:
objects = list_objects(domain="X", limit=100)
has_pset = any("Y" in obj.propertysets for obj in objects)

# Effizient:
result = advanced_search(
    query="Y",
    domain_filter="X",
    search_fields=["propertySets"],
    limit=1
)
has_pset = result['total'] > 0
```

### Use-Case 3: "Zähle alle Objekte mit Property Z"

```python
# Ineffizient:
all_objects = download_all_objects()  # 100MB, 2-3 Minuten!
count = sum(1 for obj in all_objects if has_property(obj, "Z"))

# Effizient:
result = advanced_search(
    query="Z",
    search_fields=["properties"],
    limit=1
)
count = result['total']  # 1 Sekunde!
```

---

## Lessons Learned

### Was funktioniert

- **Visuelle Marker** (💡⚡⚠️) werden schnell gescannt
- **Konkrete Beispiele** mit echten Werten sind besser als abstrakte Beschreibungen
- **DO/DON'T Listen** geben klare Guidance
- **Response-Struktur** zeigen hilft Response zu verstehen

### Was nicht funktioniert

- Nur abstrakte Beschreibungen
- Fehlende Beispiele
- Keine Performance-Hinweise
- Versteckte wichtige Features (wie 'total' field)

### Prinzipien

1. **Show, don't tell**: Beispiele > Erklärungen
2. **Performance matters**: Explizit machen was schnell/langsam ist
3. **Patterns > Features**: Zeigen wie man Tools kombiniert
4. **Fail fast**: Warn vor ineffizienten Patterns

---

## Anhang: Original-Ergebnisse der Analyse

### Domains mit SBB-CFF-FFS_PO PropertySet

| Domain                   | Mit PSet | Total  | Abdeckung |
| ------------------------ | -------- | ------ | --------- |
| **Fahrbahn** ✓           | **55**   | **55** | **100%**  |
| **Naturgefahren** ✓      | **36**   | **36** | **100%**  |
| Telecom                  | 68       | 69     | 98.6%     |
| Brücken                  | 52       | 54     | 96.3%     |
| Werkleitungen            | 88       | 91     | 96.7%     |
| Kunstbauten              | 62       | 63     | 98.4%     |
| Sicherungsanlagen        | 120      | 134    | 89.6%     |
| Energie                  | 266      | 302    | 88.1%     |
| Fahrstrom                | 107      | 124    | 86.3%     |
| Geologie                 | 12       | 14     | 85.7%     |
| Tunnel                   | 71       | 87     | 81.6%     |
| Hochbau                  | 432      | 550    | 78.5%     |
| Strasse                  | 11       | 18     | 61.1%     |
| Kabelanlagen             | 36       | 59     | 61.0%     |
| Linienführung/Geomatik   | 0        | 16     | 0%        |
| Lichtraumprofil          | 0        | 12     | 0%        |
| Fachbereich übergreifend | 0        | 3      | 0%        |

**Nur 2 Domains haben 100% Abdeckung!**

Diese Analyse wurde mit 17 effizienten Tool-Calls erreicht (je einer pro Domain mit limit=1).
