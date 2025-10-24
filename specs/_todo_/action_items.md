# FDK MCP - Verbleibende Aufgaben & Roadmap

**Stand:** 2025-10-24
**Status:** Clean Architecture Migration abgeschlossen, Polishing-Phase

---

## ✅ Kürzlich abgeschlossen

- ✅ Clean Architecture Migration (Phase 1-7 komplett)
- ✅ Domain Layer: Entities, Repositories, Protocols
- ✅ Use Cases: Alle 10 Use Cases implementiert
- ✅ Infrastructure: DI Container, Plugin Registry, File Cache
- ✅ Adapters: Presenters (Markdown & JSON)
- ✅ Plugin System: SBB Plugin vollständig
- ✅ Test Suite: 169 Tests (Domain, Use Cases, Infrastructure, Adapters, Plugins)
- ✅ Literal Types: SortField, SortOrder, GroupField mit Validierung

---

## 🔥 Priorität 1: MCP Tool-Beschreibungen verbessern

**Datei:** `specs/_in_progress_/fdk_tool_improvements.md`

**Problem:** Tool-Beschreibungen erklären nicht optimal:
- Response-Strukturen (z.B. `total` field)
- Efficiency Patterns (z.B. `limit=1` für Counts)
- Best Practices für häufige Use-Cases
- Wann welches Tool zu verwenden ist

**Aufgaben:**

### 1. Server Tool-Beschreibungen erweitern

**Datei:** `src/fdk_mcp/server.py`

Für jedes Tool hinzufügen:

```python
# Beispiel für fdk_advanced_search
"""
Advanced search across ANY JSON field in FDK objects.

⚡ EFFICIENCY PATTERNS:
1️⃣ COUNTING (most efficient):
   advanced_search(query="X", domain_filter="Y", limit=1)
   → Read response['total'] for count

2️⃣ EXISTENCE CHECK:
   advanced_search(query="X", limit=1)
   → Check if response['total'] > 0

✅ DO:
- Use limit=1 for counting/checking
- Use domain_filter to scope searches
- Use response['total'] for aggregations

❌ DON'T:
- Fetch limit=200 just to count
- Write loops to process results

RESPONSE STRUCTURE:
{
  "total": 1416,      ← Total matches (always present)
  "count": 200,       ← Items in this response
  "data": [...]       ← Actual objects
}
"""
```

**Zu aktualisierende Tools:**
- [x] `fdk_list_objects`
- [x] `fdk_get_object`
- [x] `fdk_search_properties`
- [x] `fdk_advanced_search` ⭐ (wichtigste)
- [x] `fdk_download_all_objects`
- [x] `fdk_update_cache`
- [x] `fdk_list_domains`
- [x] `fdk_refresh_cache`
- [x] `fdk_get_cache_stats`
- [x] `fdk_group_objects` (neu)

**Geschätzter Aufwand:** 2-3 Stunden
**Impact:** Hoch - verbessert Claude's Tool-Wahl signifikant

---

## 📚 Priorität 2: Dokumentation aktualisieren

### 2.1 README.md modernisieren

**Datei:** `README.md`

**Zu ergänzen:**

1. **Clean Architecture Section:**
   ```markdown
   ## Architecture

   This project follows Clean Architecture principles:
   - **Domain Layer**: Entities, Repository Protocols
   - **Use Cases**: Business logic orchestration
   - **Adapters**: Presenters (Markdown, JSON)
   - **Infrastructure**: DI Container, File Cache, Plugin System
   - **Plugins**: Vendor-specific implementations (SBB)
   ```

2. **Installation aktualisieren:**
   - uv-basierte Installation dokumentieren
   - Python 3.11+ Requirement
   - Environment Variables

3. **Usage Examples erweitern:**
   - Beispiele für alle Tools
   - Efficiency Patterns zeigen
   - Best Practices

4. **Plugin Development Guide:**
   - Wie man ein neues FDK-Plugin erstellt
   - Plugin Interface dokumentieren

**Geschätzter Aufwand:** 3-4 Stunden
**Impact:** Mittel - verbessert Onboarding

### 2.2 API Documentation

**Neue Datei:** `docs/API.md`

Vollständige API-Dokumentation:
- Alle Tools mit Parametern
- Response-Formate
- Error-Handling
- Rate Limiting

**Geschätzter Aufwand:** 4-5 Stunden
**Impact:** Mittel

---

## 🧹 Priorität 3: Code Cleanup

### 3.1 Legacy-Dateien entfernen

**Zu prüfen und ggf. löschen:**

```bash
# Diese Dateien wurden durch Clean Architecture ersetzt:
src/fdk_mcp/service.py        # → use_cases/*
src/fdk_mcp/api_client.py     # → plugins/sbb/sbb_api_client.py
src/fdk_mcp/fdk_models.py     # → plugins/sbb/sbb_models.py
src/fdk_mcp/protocols.py      # → domain/repositories/*
```

**Vorgehen:**
1. Git-History prüfen
2. Referenzen suchen: `grep -r "from fdk_mcp.service import"`
3. Falls keine Referenzen: Löschen
4. Falls Referenzen: Deprecation-Warning hinzufügen

**Geschätzter Aufwand:** 1-2 Stunden
**Impact:** Niedrig - Code-Qualität

### 3.2 Import Cleanup

**Aufgabe:** Ungenutzte Imports entfernen

```bash
# Mit ruff:
uv run ruff check --select F401 src/
uv run ruff check --fix --select F401 src/
```

**Geschätzter Aufwand:** 30 Minuten
**Impact:** Niedrig

### 3.3 Type Hints vervollständigen

**Aufgabe:** Alle `# type: ignore` Kommentare analysieren und beheben

```bash
# Finden:
grep -r "type: ignore" src/

# Beheben mit strict mypy:
uv run mypy src/fdk_mcp --strict
```

**Geschätzter Aufwand:** 2-3 Stunden
**Impact:** Mittel - Code-Qualität

---

## 🚀 Priorität 4: Performance-Optimierungen

### 4.1 Caching verbessern

**Ideen:**
- LRU Cache für häufig abgerufene Objekte
- Batch-Loading für PropertySets
- Parallel fetching optimieren

**Datei:** `src/fdk_mcp/infrastructure/cache/file_cache.py`

**Geschätzter Aufwand:** 3-4 Stunden
**Impact:** Mittel - bei großen Katalogen

### 4.2 Response-Größe optimieren

**Problem:** Manche Responses sind sehr groß (>100KB)

**Lösungen:**
- Truncation für lange Listen
- Pagination forcieren
- Lazy-Loading für Details

**Geschätzter Aufwand:** 2-3 Stunden
**Impact:** Niedrig-Mittel

---

## 🔌 Priorität 5: Plugin-Ökosystem erweitern

### 5.1 Generic FDK Plugin

**Idee:** Ein generisches Plugin für FDK-Systeme mit ähnlicher Struktur

**Neue Datei:** `src/fdk_mcp/plugins/generic/generic_plugin.py`

**Features:**
- Konfigurierbare API-Endpoints
- Flexibles Field-Mapping
- Custom Transformations

**Geschätzter Aufwand:** 8-10 Stunden
**Impact:** Hoch - Wiederverwendbarkeit

### 5.2 Plugin Registry erweitern

**Ideen:**
- Auto-Discovery von Plugins
- Plugin Dependencies
- Plugin Versioning

**Geschätzter Aufwand:** 4-5 Stunden
**Impact:** Mittel

---

## 🧪 Priorität 6: Testing

### 6.1 Property-Based Testing

**Tool:** Hypothesis

**Tests hinzufügen für:**
- CatalogObject Validierung
- Property Transformationen
- Search Algorithms

**Geschätzter Aufwand:** 3-4 Stunden
**Impact:** Mittel - findet Edge Cases

### 6.2 Mutation Testing

**Tool:** mutmut

**Aufgabe:** Test-Qualität prüfen

```bash
uv run mutmut run
uv run mutmut results
```

**Geschätzter Aufwand:** 2-3 Stunden
**Impact:** Niedrig - Test-Verbesserung

### 6.3 Integration Tests erweitern

**Fehlende Tests:**
- End-to-End Workflows
- Error Recovery
- Cache Invalidation

**Geschätzter Aufwand:** 4-5 Stunden
**Impact:** Mittel

---

## 📊 Priorität 7: Monitoring & Observability

### 7.1 Logging verbessern

**Framework:** structlog

**Aufgaben:**
- Strukturiertes Logging
- Log Levels konfigurierbar
- Performance Metrics

**Geschätzter Aufwand:** 2-3 Stunden
**Impact:** Mittel

### 7.2 Metrics

**Tool:** prometheus_client

**Metrics:**
- Tool-Aufrufe
- Response Times
- Cache Hit/Miss Rate
- Error Rates

**Geschätzter Aufwand:** 3-4 Stunden
**Impact:** Niedrig-Mittel

---

## 🌐 Priorität 8: Internationalisierung

### 8.1 Multi-Language Support

**Status:** Teilweise vorhanden (de, fr, it, en)

**Zu verbessern:**
- Fehler-Messages übersetzen
- Tool-Beschreibungen mehrsprachig
- Locale-aware Formatting

**Geschätzter Aufwand:** 4-5 Stunden
**Impact:** Niedrig

---

## 📦 Priorität 9: Distribution

### 9.1 PyPI Package

**Aufgabe:** Package auf PyPI veröffentlichen

**TODO:**
- setup.py/pyproject.toml finalisieren
- Versioning Strategy
- Release Workflow (GitHub Actions)

**Geschätzter Aufwand:** 3-4 Stunden
**Impact:** Mittel

### 9.2 Docker Image

**Aufgabe:** Docker Image bereitstellen

**Neue Datei:** `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv pip install -e .
CMD ["python", "-m", "fdk_mcp.server"]
```

**Geschätzter Aufwand:** 2-3 Stunden
**Impact:** Niedrig

---

## 🎯 Roadmap-Timeline

### Sprint 1 (Woche 1-2) - Polish & Documentation
- [x] Tool-Beschreibungen verbessern (Prio 1)
- [x] README aktualisieren (Prio 2.1)
- [x] Code Cleanup (Prio 3)

### Sprint 2 (Woche 3-4) - Performance & Testing
- [ ] Caching optimieren (Prio 4.1)
- [ ] Property-Based Tests (Prio 6.1)
- [ ] Integration Tests (Prio 6.3)

### Sprint 3 (Woche 5-6) - Ecosystem
- [ ] Generic Plugin (Prio 5.1)
- [ ] API Documentation (Prio 2.2)
- [ ] Logging verbessern (Prio 7.1)

### Sprint 4 (Woche 7-8) - Distribution
- [ ] PyPI Package (Prio 9.1)
- [ ] Docker Image (Prio 9.2)
- [ ] Release 1.0.0

---

## 📋 Quick Wins (< 1 Stunde)

Diese Aufgaben können schnell erledigt werden:

1. **Import Cleanup** (30 min)
   ```bash
   uv run ruff check --fix --select F401 src/
   ```

2. **Type Hints für neue Literale exportieren** (15 min)
   - `__all__` in `models.py` aktualisieren

3. **Git-Tags für Releases** (10 min)
   ```bash
   git tag -a v1.0.0 -m "Clean Architecture Release"
   git push --tags
   ```

4. **CONTRIBUTORS.md erstellen** (20 min)

5. **GitHub Issues Templates** (30 min)

---

## 💡 Future Ideas (Backlog)

- GraphQL API für FDK Katalog
- Web UI (React + TanStack Query)
- CLI Tool zusätzlich zum MCP Server
- Batch Operations API
- Advanced Analytics (Statistics über Katalog)
- Export zu verschiedenen Formaten (CSV, Excel, PDF)
- Diff-Tool für Katalog-Versionen
- Notification System für Katalog-Updates

---

**Letzte Aktualisierung:** 2025-10-24
**Verantwortlich:** Elyo
**Review-Datum:** 2025-11-24
