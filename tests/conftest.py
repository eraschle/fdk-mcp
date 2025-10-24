"""Pytest configuration and shared fixtures for SBB FDK MCP tests."""

from pathlib import Path
from typing import Any

import pytest

from fdk_mcp.domain.entities import CatalogObject, Property, PropertySet, ReleaseInfo
from fdk_mcp.domain.repositories import CatalogResponse
from fdk_mcp.models import LanguageCode


__all__ = ["FakeCatalogRepository"]


# Pytest markers
def pytest_configure(config: Any) -> None:
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests (optional)")


# Sample Data Fixtures
@pytest.fixture
def sample_release_info() -> ReleaseInfo:
    """Sample release info using domain entity."""
    return ReleaseInfo(name="v2024.1", date="2024-01-15")


@pytest.fixture
def sample_property() -> Property:
    """Sample property using domain entity."""
    return Property(
        id="PROP_1",
        name="Width",
        value="10.5",
        unit="m",
        description="Width of the element",
        data_type="IfcLengthMeasure",
    )


@pytest.fixture
def sample_property_set(sample_property: Property) -> PropertySet:
    """Sample property set using domain entity."""
    return PropertySet(
        id="PSET_1", name="Dimensions", properties=[sample_property], description="Dimensional properties"
    )


@pytest.fixture
def sample_catalog_object(sample_property_set: PropertySet) -> CatalogObject:
    """Sample catalog object using domain entity."""
    return CatalogObject(
        id="TEST_1",
        name="Test Bridge",
        domain="Bridges",
        description="Standard bridge type A",
        image_id="IMG_001",
        property_sets=[sample_property_set],
        classifications=["IfcBridge"],
    )


@pytest.fixture
def sample_catalog_object_list(sample_catalog_object: CatalogObject) -> list[CatalogObject]:
    """Sample list of catalog objects."""
    return [
        sample_catalog_object,
        CatalogObject(id="OBJ_BR_2", name="Bridge A", domain="Bridges", description="Standard bridge type A"),
        CatalogObject(id="OBJ_TUN_1", name="Tunnel Type A", domain="Tunnels", description="Standard tunnel type A"),
        CatalogObject(id="OBJ_TRK_1", name="Track Type A", domain="Tracks", description="Standard track type A"),
    ]


# Fake Repository for Testing
class FakeCacheRepository:
    """Fake cache repository for testing.

    Implements CacheRepository protocol without real file I/O.
    """

    def __init__(self) -> None:
        """Initialize with empty cache."""
        self.cache: dict[str, CatalogObject] = {}
        self.last_updated: str | None = None
        self.release_info: ReleaseInfo | None = None
        self._is_fresh: bool = True

    def save_object(self, object_id: str, obj: CatalogObject) -> None:
        """Save object to cache."""
        self.cache[object_id] = obj

    def get_cached_object(self, object_id: str) -> CatalogObject | None:
        """Get cached object by ID."""
        return self.cache.get(object_id)

    def list_cached_objects(self) -> list[CatalogObject]:
        """List all cached objects."""
        return list(self.cache.values())

    def is_cache_fresh(self, current_release: ReleaseInfo | None = None) -> bool:
        """Check if cache is still fresh/valid."""
        return self._is_fresh

    def update_metadata(self, count: int, release: ReleaseInfo | None = None) -> None:
        """Update cache metadata."""
        self.release_info = release
        # Update last_updated timestamp
        from datetime import datetime

        self.last_updated = datetime.now().isoformat()

    def get_cache_stats(self) -> Any:
        """Get cache statistics."""
        from fdk_mcp.domain.repositories import CacheStats

        return CacheStats(
            last_updated=self.last_updated,
            object_count=len(self.cache),
            is_fresh=self._is_fresh,
            release=self.release_info,
        )

    def get_cache_coverage(self, all_object_ids: list[str], check_detail_level: bool = True) -> Any:
        """Analyze cache coverage for given objects."""
        from fdk_mcp.domain.repositories import CacheCoverageStats

        cached_ids = set(self.cache.keys())

        # For testing, assume all cached objects have full details
        cached_with_details = len(cached_ids)
        cached_summary_only = 0
        not_cached = len(set(all_object_ids) - cached_ids)
        total_objects = len(all_object_ids)

        coverage_percentage = (cached_with_details / total_objects * 100) if total_objects > 0 else 0.0

        return CacheCoverageStats(
            total_objects=total_objects,
            cached_with_details=cached_with_details,
            cached_summary_only=cached_summary_only,
            not_cached=not_cached,
            coverage_percentage=coverage_percentage,
        )

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self.last_updated = None
        self.release_info = None

    # Helper method for tests
    def set_fresh(self, is_fresh: bool) -> None:
        """Set cache freshness state (test helper)."""
        self._is_fresh = is_fresh


class FakeCatalogRepository:
    """Fake catalog repository for testing.

    Implements CatalogRepository protocol without hitting real API.
    """

    def __init__(self, objects: list[CatalogObject] | None = None):
        """Initialize with optional pre-populated objects."""
        self.objects = objects or []
        self._fetch_calls: list[dict[str, Any]] = []

    async def fetch_all_objects(self, language: LanguageCode = "en") -> CatalogResponse:
        """Fetch all objects (returns pre-populated data)."""
        self._fetch_calls.append({"method": "fetch_all_objects", "language": language})
        return CatalogResponse(objects=self.objects, total_count=len(self.objects))

    async def fetch_object_by_id(self, object_id: str, language: LanguageCode = "en") -> CatalogObject:
        """Fetch object by ID.

        Raises:
            ValueError: If object not found (mimics ObjectNotFoundError)
        """
        self._fetch_calls.append({"method": "fetch_object_by_id", "object_id": object_id, "language": language})
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        raise ValueError(f"Object with ID '{object_id}' not found")

    def get_supported_languages(self) -> list[str]:
        """Get supported languages."""
        return ["de", "en", "fr", "it"]


@pytest.fixture
def fake_catalog_repository(sample_catalog_object: CatalogObject) -> FakeCatalogRepository:
    """Fake catalog repository with single sample object."""
    return FakeCatalogRepository(objects=[sample_catalog_object])


@pytest.fixture
def empty_catalog_repository() -> FakeCatalogRepository:
    """Fake catalog repository with no data."""
    return FakeCatalogRepository(objects=[])


@pytest.fixture
def multiple_objects_catalog(sample_catalog_object_list: list[CatalogObject]) -> FakeCatalogRepository:
    """Fake catalog repository with multiple objects (alias for fake_catalog_repository)."""
    return FakeCatalogRepository(objects=sample_catalog_object_list)


@pytest.fixture
def fake_cache_repository() -> FakeCacheRepository:
    """Fake cache repository for testing."""
    return FakeCacheRepository()


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Temporary directory for cache testing."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
