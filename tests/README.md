# FDK-SBB MCP Server - Test Suite

Umfassende Test-Suite für den SBB FDK MCP Server mit **119 Tests** nach pytest Best Practices.

## Test-Struktur

```
tests/
├── unit/                      # @pytest.mark.unit
│   ├── test_api_client.py    # 15 Tests - API-Client & Retry-Logik
│   ├── test_cache.py          # 17 Tests - Cache-Management
│   ├── test_utils.py          # 26 Tests - Helper-Funktionen
│   ├── test_models.py         # 23 Tests - Pydantic Validierung
│   └── test_service.py        # 18 Tests - Business Logic
├── integration/               # @pytest.mark.integration
│   └── test_server.py         # 20 Tests - MCP Server Tools
├── fixtures/                  # Test-Daten
│   └── sample_api_responses.json
└── conftest.py                # Pytest Config & Fixtures
```

## Test-Ausführung

### Alle Tests

```bash
# Alle Tests ausführen
uv run pytest

# Mit Coverage
uv run pytest --cov=src/fdk_mcp --cov-report=html
```

### Nach Markierung

```bash
# Nur Unit Tests (schnell, isoliert)
uv run pytest -m unit

# Nur Integration Tests
uv run pytest -m integration

# Unit + Integration
uv run pytest -m "unit or integration"

# Nur schnelle Tests (keine slow-markierten)
uv run pytest -m "unit and not slow"
```

### Spezifische Test-Dateien

```bash
# Nur API-Client Tests
uv run pytest tests/unit/test_api_client.py

# Nur Service Tests
uv run pytest tests/unit/test_service.py

# Nur Server Integration Tests
uv run pytest tests/integration/test_server.py
```

### Verbose Mode

```bash
# Detaillierte Ausgabe
uv run pytest -v

# Mit Test-Namen
uv run pytest -v --tb=short
```

## Test-Markierungen (pytest Best Practices)

- `@pytest.mark.unit` - Unit Tests (schnell, isoliert) - **Standard**
- `@pytest.mark.integration` - Integration Tests - **Standard**
- `@pytest.mark.slow` - Langsame Tests (optional)
- `@pytest.mark.e2e` - End-to-End Tests (optional)
- `@pytest.mark.asyncio` - Asynchrone Tests (pytest-asyncio)

## Coverage

### Coverage Report generieren

```bash
# HTML Report
uv run pytest --cov=src/fdk_mcp --cov-report=html

# Terminal Report
uv run pytest --cov=src/fdk_mcp --cov-report=term-missing

# XML Report (für CI/CD)
uv run pytest --cov=src/fdk_mcp --cov-report=xml
```

### Coverage anzeigen

```bash
# HTML Report öffnen
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

## Test-Kategorien

### ⚡ Unit Tests (99 Tests) - `@pytest.mark.unit`

#### test_api_client.py (15 Tests)

- ✅ Erfolgreiche API-Requests
- ✅ Retry-Logik (3 Versuche, exponentieller Backoff)
- ✅ Error-Handling (404, 403, 429, Timeout)
- ✅ Context-Logging (debug/warning)
- ✅ URL-Konstruktion

#### test_cache.py (17 Tests)

- ✅ Verzeichnis-Erstellung
- ✅ Cache-Freshness (24h-Prüfung)
- ✅ Objekt-Speicherung & -Abruf
- ✅ Metadata-Verwaltung
- ✅ Unicode-Handling
- ✅ File-Persistierung

#### test_utils.py (30 Tests)

- ✅ Error-Handling (alle HTTP-Status-Codes)
- ✅ Text-Truncation (25000 Zeichen)
- ✅ ProgressTracker (Statistiken, Speed, ETA)
- ✅ Markdown/JSON-Formatierung
- ✅ Summary-Generierung

#### test_models.py (29 Tests)

- ✅ Pydantic Input-Validierung
- ✅ Min/Max Length-Checks
- ✅ Pattern-Validierung (object_id, language)
- ✅ Field-Validators (Whitespace)
- ✅ Enum-Werte
- ✅ Extra-Fields-Rejection

#### test_service.py (18 Tests)

- ✅ Cache-Refresh-Logik
- ✅ Object-Details (Cache vs API)
- ✅ Filter-Funktionen (Domain/Query)
- ✅ Property-Suche
- ✅ Download-Logik (parallel)
- ✅ Update-Logik (incremental)

### 🔗 Integration Tests (20 Tests) - `@pytest.mark.integration`

#### test_server.py (20 Tests)

- ✅ sbb_fdk_list_objects (4 Tests)
- ✅ sbb_fdk_get_object (3 Tests)
- ✅ sbb_fdk_search_properties (2 Tests)
- ✅ sbb_fdk_list_domains (1 Test)
- ✅ sbb_fdk_refresh_cache (1 Test)
- ✅ sbb_fdk_get_cache_stats (1 Test)
- ✅ sbb_fdk_download_all_objects (3 Tests)
- ✅ sbb_fdk_update_cache (3 Tests)
- ✅ Error-Handling (2 Tests)
- ✅ Context-Logging (1 Test)

## Makefile Commands

```bash
# Tests ausführen
make test

# Mit Coverage
make test-coverage

# Alle Checks (lint + typecheck + test)
make check
```

## CI/CD Integration

### GitHub Actions Beispiel

```yaml
- name: Run Tests
  run: |
    uv sync
    uv run pytest -m "unit or integration" --cov=src/fdk_mcp --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Best Practices

1. **Neue Features**: Schreibe Tests BEVOR du Code implementierst (TDD)
2. **Bug Fixes**: Schreibe einen Test, der den Bug reproduziert, dann fixe ihn
3. **Refactoring**: Führe Tests nach jedem Refactoring aus
4. **Coverage**: Ziel ist >90% Coverage für kritischen Code
5. **Marks**: Markiere Tests korrekt (@pytest.mark.unit/@pytest.mark.integration)

## Troubleshooting

### Tests schlagen fehl

```bash
# Verbose Output für Details
uv run pytest -vv --tb=long

# Nur fehlgeschlagene Tests
uv run pytest --lf

# Mit pdb Debugger
uv run pytest --pdb
```

### Import-Fehler

```bash
# Dependencies neu installieren
uv sync --force

# Python-Path prüfen
uv run python -c "import sys; print(sys.path)"
```

### Async-Fehler

```bash
# Async-Mode prüfen
uv run pytest --asyncio-mode=auto
```

## Test-Coverage Ziele

| Modul      | Aktuell  | Ziel    |
| ---------- | -------- | ------- |
| api_client | ~95%     | 95%     |
| cache      | ~90%     | 95%     |
| utils      | ~95%     | 95%     |
| models     | ~100%    | 100%    |
| service    | ~85%     | 90%     |
| server     | ~80%     | 85%     |
| **Gesamt** | **~88%** | **90%** |

## Nächste Schritte

- [ ] E2E Tests gegen echte API (optional)
- [ ] Performance-Tests (Load Testing)
- [ ] Property-Based Testing (Hypothesis)
- [ ] Mutation Testing (mutmut)
