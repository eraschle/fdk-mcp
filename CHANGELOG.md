# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Literal types for sort and group fields with runtime validation
- Field validator for `group_by` to reject empty lists
- 4 new edge-case tests for `GroupObjectsInput` model
- Type hints (`dict[str, Any]`) in all model tests for better IDE support

### Changed
- `GroupObjectsInput` model now uses strict Literal types:
  - `sort_by: SortField | None` (was `str | None`)
  - `order: SortOrder` (was `str` with regex pattern)
  - `group_by: GroupField | list[GroupField] | None` (was `str | list[str] | None`)
- Removed regex pattern validation for `order` field (replaced by Literal type)

### Fixed
- Empty lists for `group_by` are now properly rejected at validation time

---

## [1.0.0] - 2025-10-20

### 🎉 Major Release: Clean Architecture Migration

This release represents a complete architectural rewrite following Clean Architecture principles.

### Added

#### Clean Architecture Layers
- **Domain Layer**
  - `CatalogObject` entity (vendor-agnostic)
  - `PropertySet` and `Property` entities
  - `ReleaseInfo` entity
  - `CatalogRepository` protocol
  - `CacheRepository` protocol

- **Use Cases Layer** (10 use cases)
  - `ListObjectsUseCase` - List and filter objects
  - `GetObjectUseCase` - Retrieve specific object
  - `SearchPropertiesUseCase` - Search properties
  - `ListDomainsUseCase` - List available domains
  - `AdvancedSearchUseCase` - Advanced JSON field search
  - `DownloadCatalogUseCase` - Bulk download
  - `UpdateCacheUseCase` - Smart cache updates
  - `GroupObjectsUseCase` - Group and sort objects
  - `GetCacheCoverageUseCase` - Cache statistics

- **Infrastructure Layer**
  - `Container` - Dependency Injection container
  - `PluginRegistry` - Central plugin management
  - `FileCacheRepository` - File-based cache implementation

- **Adapters Layer**
  - `MarkdownPresenter` - Format output as Markdown
  - `JsonPresenter` - Format output as JSON

- **Plugin System**
  - `FdkPlugin` protocol
  - `SbbFdkPlugin` - Complete SBB implementation
  - `SbbApiClient` - API client
  - `SbbMapper` - Data transformation

#### Testing
- **120+ new tests** following Clean Architecture
  - 35+ Domain tests
  - 40+ Use Case tests
  - 15+ Infrastructure tests
  - 20+ Adapter tests
  - 10+ Plugin tests
- **Fake repositories** for fast, isolated unit testing
- **Test fixtures** in `conftest_new_fixtures.py`
- **Total test suite**: 240+ tests

#### Documentation
- `CLEAN_ARCHITECTURE_TESTS.md` - Comprehensive test documentation
- `TEST_SUITE_SUMMARY.md` - Test migration summary
- `ARCHITECTURE_MIGRATION.md` - Migration guide (completed)

#### Features
- **Language support**: German, French, Italian, English
- **Caching**: Smart caching with freshness tracking
- **Pagination**: Configurable limits and offsets
- **Filtering**: Domain-based and search query filtering
- **Multiple output formats**: Markdown and JSON
- **Detail levels**: Concise and detailed views

### Changed

- **Complete rewrite** from monolithic service to layered architecture
- **Dependency injection** for better testability and flexibility
- **Protocol-based design** instead of abstract base classes
- **Plugin-based architecture** for vendor-agnostic implementation
- **Async/await** throughout the codebase
- **Type hints** everywhere with strict mypy compliance

### Removed

- Legacy service layer (`service.py` - replaced by use cases)
- Direct API client usage (`api_client.py` - now in SBB plugin)
- Old model definitions (`fdk_models.py` - replaced by domain entities)

### Migration Notes

**Breaking Changes:**
- Complete API rewrite - old service layer removed
- Import paths changed to follow Clean Architecture
- Configuration now uses DI container

**Migration Path:**
```python
# Old (v0.x)
from fdk_mcp.service import FdkService
service = FdkService()
result = service.filter_objects(domain="Hochbau")

# New (v1.0)
from fdk_mcp.infrastructure.di.container import Container
from fdk_mcp.use_cases.list_objects import ListObjectsUseCase, ListObjectsRequest

container = Container()
use_case = container.get_use_case(ListObjectsUseCase)
request = ListObjectsRequest(domain_filter="Hochbau")
result = await use_case.execute(request)
```

---

## [0.2.0] - 2024-XX-XX (Pre-Architecture)

### Added
- Initial MCP server implementation
- SBB FDK API integration
- Basic caching functionality
- 9 MCP tools for catalog interaction

### Features
- `sbb_fdk_list_objects` - List catalog objects
- `sbb_fdk_get_object` - Get object details
- `sbb_fdk_search_properties` - Search properties
- `sbb_fdk_list_domains` - List domains
- `sbb_fdk_advanced_search` - Advanced search
- `sbb_fdk_download_all_objects` - Bulk download
- `sbb_fdk_update_cache` - Cache management
- `sbb_fdk_refresh_cache` - Force refresh
- `sbb_fdk_get_cache_stats` - Cache statistics

---

## [0.1.0] - 2024-XX-XX

### Added
- Initial project setup
- Basic FDK API client
- Simple object listing
- File-based caching

---

## Version History Summary

- **v1.0.0** (2025-10-20): Clean Architecture migration, 120+ new tests, plugin system
- **v0.2.0** (2024-XX-XX): MCP server implementation, 9 tools
- **v0.1.0** (2024-XX-XX): Initial release

---

## Development Notes

### Testing Strategy
- **Unit tests**: Fast, isolated, use fake repositories
- **Integration tests**: Test real workflows (planned)
- **Property-based tests**: Hypothesis (planned)

### Code Quality
- **Type checking**: mypy with strict mode
- **Linting**: ruff
- **Formatting**: black (via ruff)
- **Testing**: pytest with asyncio support

### Release Process
1. Update CHANGELOG.md
2. Update version in `pyproject.toml`
3. Run full test suite: `uv run pytest`
4. Create git tag: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
5. Push tags: `git push --tags`
6. Create GitHub release

---

**Note**: This CHANGELOG follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
