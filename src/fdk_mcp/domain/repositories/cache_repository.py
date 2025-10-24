"""Cache repository protocol - vendor-agnostic interface."""

from dataclasses import dataclass
from typing import Protocol

from ..entities import CatalogObject, ReleaseInfo


@dataclass
class CacheStats:
    """Statistics about cached data."""

    last_updated: str | None
    """Last update timestamp (ISO format)."""

    object_count: int
    """Number of cached objects."""

    is_fresh: bool
    """Whether cache is considered fresh."""

    release: ReleaseInfo | None = None
    """Release information if available."""


@dataclass
class CacheCoverageStats:
    """Detailed statistics about cache coverage."""

    total_objects: int
    """Total number of objects in catalog."""

    cached_with_details: int
    """Objects cached with PropertySets/full data."""

    cached_summary_only: int
    """Objects cached but only summary (no PropertySets)."""

    not_cached: int
    """Objects not yet cached."""

    coverage_percentage: float
    """Percentage of objects with full details."""

    estimated_download_time_seconds: int | None = None
    """Estimated time to download missing objects."""

    missing_object_ids: list[str] | None = None
    """IDs of objects that need downloading (optional)."""

    coverage_by_domain: dict[str, dict[str, int]] | None = None
    """Coverage breakdown per domain (optional)."""


class CacheRepository(Protocol):
    """Protocol for cache operations.

    This defines the interface for caching catalog objects.
    Implementations can use file system, Redis, database, or any storage.

    Using Protocol (not ABC) follows Clean Architecture's Dependency Rule:
    - Domain layer defines the interface
    - Outer layers (infrastructure) implement it
    - No explicit inheritance needed
    """

    def is_cache_fresh(self, current_release: ReleaseInfo | None = None) -> bool:
        """Check if cache is still fresh/valid.

        Args:
            current_release: Current release info from API (optional)

        Returns:
            True if cache is fresh, False if it needs refresh
        """
        ...

    def get_cached_object(self, object_id: str) -> CatalogObject | None:
        """Get cached object by ID.

        Args:
            object_id: Unique object identifier

        Returns:
            Cached CatalogObject or None if not found
        """
        ...

    def save_object(self, object_id: str, obj: CatalogObject) -> None:
        """Save object to cache.

        Args:
            object_id: Unique object identifier
            obj: CatalogObject to cache
        """
        ...

    def list_cached_objects(self) -> list[CatalogObject]:
        """List all cached objects.

        Returns:
            List of all cached CatalogObjects
        """
        ...

    def update_metadata(self, count: int, release: ReleaseInfo | None = None) -> None:
        """Update cache metadata.

        Args:
            count: Number of objects in cache
            release: Optional release information
        """
        ...

    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            CacheStats with freshness and object count
        """
        ...

    def get_cache_coverage(self, all_object_ids: list[str], check_detail_level: bool = True) -> CacheCoverageStats:
        """Analyze cache coverage for given objects.

        Args:
            all_object_ids: All object IDs that exist in catalog
            check_detail_level: Whether to distinguish summary vs. detail objects

        Returns:
            CacheCoverageStats with detailed coverage analysis
        """
        ...

    def clear_cache(self) -> None:
        """Clear all cached data."""
        ...
