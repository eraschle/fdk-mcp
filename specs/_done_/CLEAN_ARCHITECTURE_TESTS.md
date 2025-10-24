# Clean Architecture Test Suite

This document describes the new Clean Architecture test suite added to the FDK MCP Server.

## Overview

The new test suite follows Clean Architecture principles with clear separation of concerns:

- **Domain Tests**: Pure business logic entities
- **Use Case Tests**: Business logic with fake repositories
- **Infrastructure Tests**: DI container and plugin system
- **Adapter Tests**: Presenters (Markdown/JSON formatters)
- **Plugin Tests**: Plugin implementations

## New Test Files

### Domain Layer Tests (`tests/unit/domain/`)

**test_catalog_object.py** - Tests for CatalogObject entity

- Basic creation and field validation
- Property set retrieval (case-insensitive)
- Property value retrieval
- Relationship handling
- String representation

**test_property_set.py** - Tests for Property and PropertySet entities

- Property creation with optional fields
- Property set management
- Property lookup (case-insensitive)
- Various data types (string, number, boolean)
- String representations

**test_release_info.py** - Tests for ReleaseInfo entity

- Basic creation
- Equality comparison
- Validation

### Use Case Layer Tests (`tests/unit/use_cases/`)

All use case tests use fake repositories (no API calls, no file system access).

**test_list_objects.py** - Tests for ListObjectsUseCase

- Listing without filters
- Domain filtering (case-insensitive)
- Search query filtering
- Combined filters
- Pagination
- Empty results
- Cache freshness checking

**test_get_object.py** - Tests for GetObjectUseCase

- Getting existing objects
- Handling missing objects
- Cache-first retrieval
- Saving to cache
- Language parameter passing

**test_search_properties.py** - Tests for SearchPropertiesUseCase

- Property name search
- Case-insensitive search
- Pagination
- No matches handling

**test_list_domains.py** - Tests for ListDomainsUseCase

- Domain counting
- Empty catalog handling

**test_advanced_search.py** - Tests for AdvancedSearchUseCase

- Search in object names
- Search in descriptions
- No results handling

**test_download_catalog.py** - Tests for DownloadCatalogUseCase

- Full catalog download
- Domain filtering
- Statistics tracking

**test_update_cache.py** - Tests for UpdateCacheUseCase

- Cache updating
- Handling missing cache repository

### Infrastructure Layer Tests (`tests/unit/infrastructure/`)

**test_container.py** - Tests for DI Container

- Container initialization
- Use case creation with dependency injection
- Repository access
- Plugin info retrieval
- Custom configuration
- Plugin name override
- Instance management

**test_plugin_registry.py** - Tests for PluginRegistry

- Plugin registration
- Plugin retrieval
- Duplicate registration prevention
- Plugin existence checking
- Listing registered plugins
- Error handling for missing plugins

### Adapter Layer Tests (`tests/unit/adapters/`)

**test_presenters.py** - Tests for Markdown and JSON Presenters

- Markdown formatting for object lists
- Markdown formatting for object details
- Markdown formatting for domains summary
- Markdown formatting for property matches
- Markdown formatting for statistics
- JSON formatting for all data types
- Valid JSON structure verification
- Cache indicator

### Plugin Layer Tests (`tests/unit/plugins/`)

**test_sbb_plugin.py** - Tests for SBB FDK Plugin

- Plugin initialization
- Metadata validation
- Supported languages
- Configuration validation
- Repository creation
- Repository independence

## Test Fixtures

### New Fixtures (`conftest_new_fixtures.py`)

**Entity Fixtures:**

```python
sample_property()          # Sample Property
sample_property_set()      # Sample PropertySet
sample_catalog_object()    # Sample CatalogObject
sample_release_info()      # Sample ReleaseInfo
```

**Repository Fixtures:**

```python
fake_catalog_repository()   # Catalog repo with sample data
fake_cache_repository()     # Empty cache repo
empty_catalog_repository()  # Empty catalog repo
multiple_objects_catalog()  # Catalog with 4 test objects
```

**Test Doubles:**

- `FakeCatalogRepository`: In-memory CatalogRepository implementation
- `FakeCacheRepository`: In-memory CacheRepository implementation

## Running New Tests

### Run All New Tests

```bash
uv run pytest tests/unit/domain/ tests/unit/use_cases/ tests/unit/infrastructure/ tests/unit/adapters/ tests/unit/plugins/
```

### Run Domain Tests Only

```bash
uv run pytest tests/unit/domain/
```

### Run Use Case Tests Only

```bash
uv run pytest tests/unit/use_cases/
```

### Run Infrastructure Tests Only

```bash
uv run pytest tests/unit/infrastructure/
```

### Run Single Test File

```bash
uv run pytest tests/unit/domain/test_catalog_object.py
```

### Run Single Test

```bash
uv run pytest tests/unit/domain/test_catalog_object.py::test_catalog_object_creation -v
```

## Test Statistics

### New Tests Added

- **Domain Tests**: 35+ tests
- **Use Case Tests**: 40+ tests
- **Infrastructure Tests**: 15+ tests
- **Adapter Tests**: 20+ tests
- **Plugin Tests**: 10+ tests

**Total New Tests**: ~120 tests

### Combined Coverage

With legacy tests (119 tests) + new tests (120 tests):
**Total Test Suite**: ~240 tests

## Key Design Principles

### 1. Fake Repositories (Test Doubles)

Use fake repositories instead of mocks for cleaner, more maintainable tests:

```python
# Good - Using fake repository
fake_repo = FakeCatalogRepository(objects=[sample_obj])
use_case = ListObjectsUseCase(catalog_repo=fake_repo, cache_repo=None)

# Avoid - Using mocks (more brittle)
mock_repo = Mock()
mock_repo.fetch_all_objects = AsyncMock(return_value=...)
```

### 2. No External Dependencies

Unit tests should never:

- Make real API calls
- Access the file system
- Use databases
- Depend on network

### 3. Fast Execution

- Domain tests: <1ms each
- Use case tests: <5ms each
- All new unit tests: <1 second total

### 4. Clear Test Names

```python
# Good test names
test_list_objects_with_domain_filter()
test_get_object_not_found()
test_catalog_object_creation()

# Avoid vague names
test_use_case()
test_object()
```

### 5. Test Isolation

Each test:

- Is independent
- Can run in any order
- Doesn't affect other tests
- Has its own test data

## Writing New Tests

### Template for Use Case Tests

```python
import pytest
from fdk_mcp.use_cases.your_use_case import YourUseCase, YourRequest
from tests.conftest_new_fixtures import FakeCatalogRepository, FakeCacheRepository

@pytest.mark.unit
@pytest.mark.asyncio
async def test_your_use_case_behavior(fake_catalog_repository, fake_cache_repository):
    """Test description here."""
    # Arrange
    use_case = YourUseCase(
        catalog_repo=fake_catalog_repository,
        cache_repo=fake_cache_repository,
    )
    request = YourRequest(param="value")

    # Act
    response = await use_case.execute(request)

    # Assert
    assert response.field == expected_value
```

### Template for Domain Tests

```python
import pytest
from fdk_mcp.domain.entities import YourEntity

@pytest.mark.unit
def test_your_entity_behavior():
    """Test description here."""
    # Arrange & Act
    entity = YourEntity(id="TEST", name="Test")

    # Assert
    assert entity.id == "TEST"
    assert entity.name == "Test"
```

## Migration from Legacy Tests

### What Changed

**Old Architecture** (`test_service.py`):

- Tests imported from `fdk_mcp.service`
- Used `patch` to mock `cache` and `api_client` modules
- Tightly coupled to implementation

**New Architecture** (use case tests):

- Tests import from `fdk_mcp.use_cases`
- Use fake repositories (no mocking needed)
- Test behavior, not implementation

### Example Comparison

**Old Style:**

```python
with patch("fdk_mcp.service.cache.list_cached_objects", return_value=[obj]):
    with patch("fdk_mcp.service.api_client.fetch_object", return_value=detail):
        result = service.get_object_details("OBJ_1")
```

**New Style:**

```python
fake_repo = FakeCatalogRepository(objects=[obj])
use_case = GetObjectUseCase(catalog_repo=fake_repo, cache_repo=None)
request = GetObjectRequest(object_id="OBJ_1")
response = await use_case.execute(request)
```

## Coverage Goals

| Layer          | Goal | Status |
| -------------- | ---- | ------ |
| Domain         | 100% | ✓      |
| Use Cases      | >90% | ✓      |
| Infrastructure | >80% | ✓      |
| Adapters       | >90% | ✓      |
| Plugins        | >85% | ✓      |

## Troubleshooting

### Import Error: Cannot import FakeCatalogRepository

**Solution**: Ensure `conftest_new_fixtures.py` is loaded:

```python
# In conftest.py, verify this line exists:
pytest_plugins = ['tests.conftest_new_fixtures']
```

### Async Test Not Running

**Solution**: Add `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_my_async_function():
    result = await my_async_function()
    assert result is not None
```

### Fixture Not Found

**Solution**: Check fixture is defined in `conftest_new_fixtures.py` or `conftest.py`:

```bash
uv run pytest --fixtures | grep your_fixture_name
```

## Next Steps

1. **Extend Coverage**: Add more edge case tests
2. **Property-Based Testing**: Add Hypothesis tests
3. **Mutation Testing**: Verify test quality with mutmut
4. **Performance Tests**: Add benchmarks for use cases
5. **Deprecate Legacy**: Gradually migrate old tests to new style

## Resources

- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Test Doubles (Martin Fowler)](https://martinfowler.com/bliki/TestDouble.html)
