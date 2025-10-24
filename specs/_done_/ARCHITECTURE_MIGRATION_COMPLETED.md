# Clean Architecture Migration - Verbleibende Aufgaben

## 📊 Status: Phase 2 abgeschlossen (40% der Gesamtmigration)

**Branch:** `feature/clean-architecture-plugin-system`

---

## ✅ Was bereits erledigt ist

### Phase 1: Domain Layer (100% ✅)

- **Verzeichnisstruktur:** Alle Ordner angelegt
  - `src/fdk_mcp/domain/entities/`
  - `src/fdk_mcp/domain/repositories/`
  - `src/fdk_mcp/use_cases/`
  - `src/fdk_mcp/adapters/`
  - `src/fdk_mcp/plugins/`
  - `src/fdk_mcp/infrastructure/`

- **Domain Entities (vendor-agnostisch):**
  - `domain/entities/catalog_object.py` - `CatalogObject` (Kern-Entität)
  - `domain/entities/property_set.py` - `PropertySet` & `Property`
  - `domain/entities/release_info.py` - `ReleaseInfo`

- **Repository Protocols:**
  - `domain/repositories/catalog_repository.py` - `CatalogRepository` & `CatalogResponse`
  - `domain/repositories/cache_repository.py` - `CacheRepository` & `CacheStats`

### Phase 2: Plugin System (100% ✅)

- **Base Plugin Interface:**
  - `plugins/base/plugin_interface.py` - `FdkPlugin` Protocol & `PluginMetadata`
  - `plugins/base/exceptions.py` - Plugin-Exceptions
  - **Wichtig:** Cache ist optional (`create_cache_repository() -> CacheRepository | None`)
  - **🇨🇭 Swiss Compromise:** Plugin entscheidet, ob Cache nötig ist!

- **SBB Plugin (vollständig):**
  - `plugins/sbb/sbb_models.py` - SBB-spezifische TypedDicts
  - `plugins/sbb/sbb_mapper.py` - SBB ↔ Domain Transformation
  - `plugins/sbb/sbb_api_client.py` - `SbbApiClient` implementiert `CatalogRepository`
  - `plugins/sbb/sbb_plugin.py` - `SbbFdkPlugin` Hauptklasse

---

## 🔄 Phase 3: Infrastructure Layer (TODO)

### 3.1 FileCacheRepository erstellen

**Datei:** `src/fdk_mcp/infrastructure/cache/file_cache.py`

**Basis:** Existierende `src/fdk_mcp/cache.py` als Vorlage

**Änderungen:**

1. **Imports anpassen** - Domain-Entitäten statt FDK-Models:

   ```python
   from ...domain.entities import CatalogObject, ReleaseInfo
   from ...domain.repositories import CacheRepository, CacheStats
   ```

2. **Constructor anpassen** - Konfigurierbare Pfade:

   ```python
   def __init__(self, cache_dir: Path, max_age_hours: int = 24):
       self.cache_dir = cache_dir
       self.max_age_hours = max_age_hours
       self.objects_dir = cache_dir / "objects"
       self.metadata_file = cache_dir / "metadata.json"
       self._ensure_dirs()
   ```

3. **Methoden-Signaturen** - Domain-Entitäten verwenden:
   - `get_cached_object(object_id: str) -> CatalogObject | None`
   - `save_object(object_id: str, obj: CatalogObject) -> None`
   - `list_cached_objects() -> list[CatalogObject]`

4. **Serialisierung** - `CatalogObject` → JSON:

   ```python
   def save_object(self, object_id: str, obj: CatalogObject) -> None:
       # Convert dataclass to dict
       obj_dict = {
           "id": obj.id,
           "name": obj.name,
           "domain": obj.domain,
           # ... alle anderen Felder
       }
       file_path = self.objects_dir / f"{object_id}.json"
       with open(file_path, "w", encoding="utf-8") as f:
           json.dump(obj_dict, f, indent=2, ensure_ascii=False)
   ```

5. **Deserialisierung** - JSON → `CatalogObject`:

   ```python
   def get_cached_object(self, object_id: str) -> CatalogObject | None:
       file_path = self.objects_dir / f"{object_id}.json"
       if not file_path.exists():
           return None

       with open(file_path, encoding="utf-8") as f:
           data = json.load(f)

       # Reconstruct domain object
       return CatalogObject(
           id=data["id"],
           name=data["name"],
           domain=data["domain"],
           # ... alle anderen Felder
       )
   ```

**Test:** Bestehende Cache-Tests als Vorlage verwenden und anpassen.

---

## 🎯 Phase 4: Use Cases erstellen (TODO)

### 4.1 Use Case Template

**Muster für alle Use Cases:**

```python
# use_cases/list_objects.py
from dataclasses import dataclass
from ...domain.entities import CatalogObject
from ...domain.repositories import CatalogRepository, CacheRepository

@dataclass
class ListObjectsRequest:
    domain_filter: str | None = None
    search_query: str | None = None
    language: str = "en"
    limit: int = 20
    offset: int = 0

@dataclass
class ListObjectsResponse:
    objects: list[CatalogObject]
    total: int

class ListObjectsUseCase:
    def __init__(
        self,
        catalog_repo: CatalogRepository,
        cache_repo: CacheRepository | None,  # Optional!
    ):
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: ListObjectsRequest) -> ListObjectsResponse:
        # 1. Ensure cache is fresh (if cache exists)
        if self.cache:
            # Cache-Logik
            pass

        # 2. Get objects from catalog
        response = await self.catalog.fetch_all_objects(request.language)
        objects = response.objects

        # 3. Apply filters
        if request.domain_filter:
            objects = [o for o in objects if o.domain.lower() == request.domain_filter.lower()]

        if request.search_query:
            query = request.search_query.lower()
            objects = [o for o in objects if query in o.name.lower()]

        # 4. Pagination
        total = len(objects)
        paginated = objects[request.offset:request.offset + request.limit]

        return ListObjectsResponse(objects=paginated, total=total)
```

### 4.2 Use Cases zu erstellen

**Basis:** Existierende `service.py` als Vorlage

**Liste der Use Cases:**

1. **`use_cases/list_objects.py`** - Liste/Suche Objekte
   - Entspricht: `FdkService.filter_objects()`
   - Request: `domain_filter`, `search_query`, `language`, `limit`, `offset`
   - Response: `objects`, `total`

2. **`use_cases/get_object.py`** - Hole spezifisches Objekt
   - Entspricht: `FdkService.get_object_details()`
   - Request: `object_id`, `language`
   - Response: `object` (CatalogObject mit PropertySets)
   - **Cache-Logik:** Prüfe Cache → API → Cache speichern

3. **`use_cases/search_properties.py`** - Suche Properties
   - Entspricht: `FdkService.search_properties()`
   - Request: `query`, `limit`
   - Response: `results` (Liste von Property-Matches mit Kontext)

4. **`use_cases/list_domains.py`** - Liste Domains
   - Entspricht: `FdkService.get_domains_summary()`
   - Request: keine
   - Response: `domains` (Dict[str, int])

5. **`use_cases/advanced_search.py`** - Erweiterte Suche
   - Entspricht: `FdkService.advanced_search()`
   - Request: `search_fields`, `query`, `domain_filter`, `match_mode`, `case_sensitive`
   - Response: `results`

6. **`use_cases/download_catalog.py`** - Vollständiger Download
   - Entspricht: `FdkService.download_all_objects()`
   - Request: `language`, `domain_filter`, `max_concurrent`
   - Response: `DownloadStats`

7. **`use_cases/update_cache.py`** - Cache aktualisieren
   - Entspricht: `FdkService.update_missing_objects()`
   - Request: `language`, `domain_filter`, `force_refresh`, `max_concurrent`
   - Response: `DownloadStats`

**Wichtig:** Alle Use Cases müssen mit `cache_repo: CacheRepository | None` umgehen!

---

## 🏗️ Phase 5: Dependency Injection (TODO)

### 5.1 Plugin Registry

**Datei:** `src/fdk_mcp/infrastructure/di/plugin_registry.py`

```python
from typing import Dict
from ...plugins.base import FdkPlugin, PluginNotFoundError

class PluginRegistry:
    """Central registry for FDK plugins."""

    def __init__(self):
        self._plugins: Dict[str, FdkPlugin] = {}

    def register(self, plugin: FdkPlugin) -> None:
        """Register a plugin."""
        self._plugins[plugin.metadata.name] = plugin

    def get_plugin(self, name: str) -> FdkPlugin:
        """Get plugin by name."""
        if name not in self._plugins:
            raise PluginNotFoundError(name)
        return self._plugins[name]

    def list_plugins(self) -> list[str]:
        """List all registered plugin names."""
        return list(self._plugins.keys())
```

### 5.2 DI Container

**Datei:** `src/fdk_mcp/infrastructure/di/container.py`

```python
import os
from pathlib import Path
from ...plugins.sbb import SbbFdkPlugin
from ...domain.repositories import CatalogRepository, CacheRepository
from ..di.plugin_registry import PluginRegistry

class Container:
    """Dependency Injection Container."""

    def __init__(self, plugin_name: str | None = None):
        # Setup plugin registry
        self.registry = PluginRegistry()
        self.registry.register(SbbFdkPlugin())
        # TODO: Register other plugins here

        # Get active plugin from env or parameter
        active_plugin_name = plugin_name or os.getenv("FDK_PLUGIN", "sbb")
        self.plugin = self.registry.get_plugin(active_plugin_name)

        # Create repositories
        config = self._load_config()
        self.catalog_repo = self.plugin.create_catalog_repository(config)
        self.cache_repo = self.plugin.create_cache_repository(config)  # Can be None!

    def _load_config(self) -> dict:
        """Load plugin configuration from environment/file."""
        return {
            "base_url": os.getenv("FDK_API_URL"),
            "cache_dir": os.getenv("FDK_CACHE_DIR"),
            "timeout": float(os.getenv("FDK_TIMEOUT", "30.0")),
        }

    def get_use_case(self, use_case_class):
        """Create use case instance with injected dependencies."""
        return use_case_class(
            catalog_repo=self.catalog_repo,
            cache_repo=self.cache_repo,  # Can be None!
        )
```

---

## 🌐 Phase 6: MCP Server Migration (TODO)

### 6.1 Server anpassen

**Datei:** `src/fdk_mcp/infrastructure/mcp/server.py` (neu) oder bestehende `server.py` anpassen

**Änderungen:**

1. **Container initialisieren:**

   ```python
   from ...infrastructure.di.container import Container

   # Initialize DI Container
   container = Container()
   ```

2. **Tool-Funktionen anpassen** - Beispiel `list_objects`:

   ```python
   from ...use_cases.list_objects import ListObjectsUseCase, ListObjectsRequest
   from ...adapters.presenters.markdown_presenter import MarkdownPresenter

   @mcp.tool(name="fdk_list_objects")
   async def list_objects(
       domain: str | None = None,
       search: str | None = None,
       language: str = "en",
       limit: int = 20,
       ctx: Context = None
   ) -> str:
       # Get use case from container
       use_case = container.get_use_case(ListObjectsUseCase)

       # Create request
       request = ListObjectsRequest(
           domain_filter=domain,
           search_query=search,
           language=language,
           limit=limit,
       )

       # Execute use case
       response = await use_case.execute(request)

       # Format response
       presenter = MarkdownPresenter()
       return presenter.format_object_list(response.objects, response.total)
   ```

3. **Alle Tools migrieren:**
   - `fdk_list_objects` → `ListObjectsUseCase`
   - `fdk_get_object` → `GetObjectUseCase`
   - `fdk_search_properties` → `SearchPropertiesUseCase`
   - `fdk_list_domains` → `ListDomainsUseCase`
   - `fdk_advanced_search` → `AdvancedSearchUseCase`
   - `fdk_download_all_objects` → `DownloadCatalogUseCase`
   - `fdk_update_cache` → `UpdateCacheUseCase`
   - `fdk_refresh_cache` → Einfacher API-Call
   - `fdk_get_cache_stats` → `cache_repo.get_cache_stats()`

### 6.2 Presenters erstellen

**Datei:** `src/fdk_mcp/adapters/presenters/markdown_presenter.py`

```python
from ...domain.entities import CatalogObject

class MarkdownPresenter:
    """Format domain objects as Markdown for MCP responses."""

    def format_object_list(self, objects: list[CatalogObject], total: int) -> str:
        lines = [f"# FDK Objects ({total} total)\n"]
        for obj in objects:
            lines.append(f"- **{obj.name}** ({obj.id}) - {obj.domain}")
        return "\n".join(lines)

    def format_object_detail(self, obj: CatalogObject) -> str:
        lines = [f"# {obj.name}\n"]
        lines.append(f"**ID**: {obj.id}")
        lines.append(f"**Domain**: {obj.domain}\n")

        if obj.description:
            lines.append(f"## Description\n{obj.description}\n")

        if obj.property_sets:
            lines.append(f"## Property Sets ({len(obj.property_sets)})\n")
            for pset in obj.property_sets:
                lines.append(f"### {pset.name}")
                for prop in pset.properties:
                    lines.append(f"- {prop.name}")
                lines.append("")

        return "\n".join(lines)
```

**Datei:** `src/fdk_mcp/adapters/presenters/json_presenter.py`

```python
import json
from dataclasses import asdict
from ...domain.entities import CatalogObject

class JsonPresenter:
    """Format domain objects as JSON for MCP responses."""

    def format_object(self, obj: CatalogObject) -> str:
        return json.dumps(asdict(obj), indent=2, ensure_ascii=False)

    def format_object_list(self, objects: list[CatalogObject], total: int, offset: int) -> str:
        return json.dumps({
            "total": total,
            "count": len(objects),
            "offset": offset,
            "data": [asdict(obj) for obj in objects]
        }, indent=2, ensure_ascii=False)
```

---

## 🧪 Phase 7: Tests anpassen (TODO)

### 7.1 Domain Entity Tests

**Datei:** `tests/domain/test_catalog_object.py` (neu)

```python
import pytest
from fdk_mcp.domain.entities import CatalogObject, Property, PropertySet

def test_catalog_object_creation():
    obj = CatalogObject(
        id="TEST_1",
        name="Test Object",
        domain="Test Domain",
    )
    assert obj.id == "TEST_1"
    assert obj.name == "Test Object"

def test_get_property_set():
    pset = PropertySet(id="ps1", name="TestSet", properties=[])
    obj = CatalogObject(
        id="TEST_1",
        name="Test",
        domain="Test",
        property_sets=[pset]
    )
    assert obj.get_property_set("TestSet") == pset
```

### 7.2 Plugin Tests

**Datei:** `tests/plugins/test_sbb_plugin.py` (neu)

```python
import pytest
from fdk_mcp.plugins.sbb import SbbFdkPlugin

def test_sbb_plugin_metadata():
    plugin = SbbFdkPlugin()
    assert plugin.metadata.name == "sbb"
    assert "de" in plugin.metadata.supported_languages

def test_create_catalog_repository():
    plugin = SbbFdkPlugin()
    repo = plugin.create_catalog_repository({})
    assert repo is not None
```

### 7.3 Use Case Tests

**Datei:** `tests/use_cases/test_list_objects.py` (neu)

Mock-basierte Tests mit Test Doubles:

```python
import pytest
from fdk_mcp.use_cases.list_objects import ListObjectsUseCase, ListObjectsRequest
from fdk_mcp.domain.entities import CatalogObject
from fdk_mcp.domain.repositories import CatalogResponse

class FakeCatalogRepository:
    """Test double for CatalogRepository."""

    async def fetch_all_objects(self, language: str):
        objects = [
            CatalogObject(id="1", name="Object 1", domain="Domain A"),
            CatalogObject(id="2", name="Object 2", domain="Domain B"),
        ]
        return CatalogResponse(objects=objects, total_count=2)

    def get_supported_languages(self):
        return ["en", "de"]

@pytest.mark.asyncio
async def test_list_objects_no_filter():
    repo = FakeCatalogRepository()
    use_case = ListObjectsUseCase(catalog_repo=repo, cache_repo=None)

    request = ListObjectsRequest(language="en", limit=10)
    response = await use_case.execute(request)

    assert response.total == 2
    assert len(response.objects) == 2
```

### 7.4 Integration Tests

Bestehende Integration-Tests anpassen auf neue Architektur.

---

## 📋 Checkliste für die Fortsetzung

### Sofort nach Context-Clear

1. [ ] `FileCacheRepository` in `infrastructure/cache/file_cache.py` erstellen
2. [ ] Use Cases aus `service.py` extrahieren (7 Use Cases)
3. [ ] `PluginRegistry` erstellen
4. [ ] `Container` (DI) erstellen
5. [ ] MCP Server auf Container umstellen
6. [ ] Presenters erstellen (Markdown & JSON)
7. [ ] Tests anpassen und erweitern
8. [ ] Alte Dateien als deprecated markieren oder löschen:
   - `src/fdk_mcp/service.py` → Use Cases
   - `src/fdk_mcp/cache.py` → `infrastructure/cache/file_cache.py`
   - `src/fdk_mcp/api_client.py` → `plugins/sbb/sbb_api_client.py`
   - `src/fdk_mcp/fdk_models.py` → `plugins/sbb/sbb_models.py`
   - `src/fdk_mcp/protocols.py` → `domain/repositories/`
9. [ ] Dokumentation aktualisieren (README.md)
10. [ ] Alle Tests grün bekommen
11. [ ] Final Commit & PR erstellen

---

## 🎯 Erwartetes Endergebnis

```
src/fdk_mcp/
├── domain/                    # ✅ FERTIG
│   ├── entities/              # ✅ CatalogObject, PropertySet, ReleaseInfo
│   └── repositories/          # ✅ Protocols
├── use_cases/                 # ⏳ TODO
│   ├── list_objects.py
│   ├── get_object.py
│   ├── search_properties.py
│   ├── list_domains.py
│   ├── advanced_search.py
│   ├── download_catalog.py
│   └── update_cache.py
├── adapters/                  # ⏳ TODO
│   └── presenters/
│       ├── markdown_presenter.py
│       └── json_presenter.py
├── plugins/                   # ✅ FERTIG
│   ├── base/                  # ✅ Plugin Interface
│   └── sbb/                   # ✅ SBB Plugin komplett
├── infrastructure/            # ⏳ TODO
│   ├── cache/
│   │   └── file_cache.py      # TODO
│   ├── di/
│   │   ├── plugin_registry.py # TODO
│   │   └── container.py       # TODO
│   └── mcp/
│       └── server.py          # TODO (oder bestehende anpassen)
└── [alte Dateien]             # Deprecated, später löschen
```

---

## 💡 Wichtige Design-Entscheidungen

1. **Swiss Compromise:** Cache ist optional im Plugin (`CacheRepository | None`)
2. **Protocol statt ABC:** Strukturelle Subtypisierung, keine explizite Vererbung
3. **Domain ist vendor-agnostisch:** Keine SBB-spezifischen Felder in Domain-Entitäten
4. **Use Cases sind die Controller:** Sie orchestrieren Domain-Logik
5. **Plugins sind austauschbar:** Neues FDK = neues Plugin, keine Core-Änderungen

---

## 📚 Referenzen

- Clean Architecture: `~/.claude/skills/clean-architecture/SKILL.md`
- SOLID Principles: `~/.claude/skills/solid-principles/SKILL.md`
- Existierende Tests: `tests/` als Vorlage

---

**Nächster Schritt:** Diese Datei committen, dann Punkt für Punkt abarbeiten! 🚀
