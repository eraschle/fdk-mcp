"""Update Missing Objects in Cache Use Case."""

import asyncio
import time
from dataclasses import dataclass

from ..domain.entities import CatalogObject
from ..domain.repositories import CacheRepository, CatalogRepository
from ..models import LanguageCode


@dataclass
class UpdateStats:
    """Statistics about cache update operation."""

    total_objects: int
    """Total number of objects in catalog."""

    downloaded: int
    """Number of objects downloaded in this update."""

    already_cached: int
    """Number of objects already in cache (skipped)."""

    failed: int
    """Number of failed downloads."""

    duration_seconds: float
    """Total duration of update operation in seconds."""


@dataclass
class UpdateCacheRequest:
    """Request parameters for updating cache."""

    language: LanguageCode = "en"
    """Language code for downloading objects."""

    domain_filter: str | None = None
    """Optional domain filter to update only specific domain."""

    force_refresh: bool = False
    """If True, re-download all objects regardless of cache status."""

    max_concurrent: int = 10
    """Maximum number of concurrent downloads."""


@dataclass
class UpdateCacheResponse:
    """Response containing update statistics."""

    stats: UpdateStats
    """Update statistics."""


class UpdateCacheUseCase:
    """Use case for updating missing or outdated objects in cache.

    This use case handles:
    - Checking which objects are missing in cache
    - Downloading only missing objects (incremental update)
    - Force refresh mode to re-download all objects
    - Concurrent downloads with configurable parallelism
    - Retry logic for failed downloads
    - Progress tracking and statistics

    Follows Clean Architecture:
    - Depends on abstractions (CatalogRepository, CacheRepository)
    - Works with domain entities (CatalogObject)
    - Single Responsibility: incremental cache updates
    """

    def __init__(self, catalog_repo: CatalogRepository, cache_repo: CacheRepository | None = None):
        """Initialize use case with repository dependencies.

        Args:
            catalog_repo: Repository for fetching catalog data from API
            cache_repo: Optional cache repository for storing downloaded objects
        """
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: UpdateCacheRequest) -> UpdateCacheResponse:
        """Execute the update cache use case.

        Args:
            request: Request parameters with language and filters

        Returns:
            UpdateCacheResponse with update statistics

        Raises:
            CatalogError: If initial catalog fetch fails
        """
        start_time = time.time()

        # If no cache available, return empty stats
        if not self.cache:
            return UpdateCacheResponse(
                stats=UpdateStats(
                    total_objects=0, downloaded=0, already_cached=0, failed=0, duration_seconds=time.time() - start_time
                )
            )

        # Step 1: Get list of all objects from API
        response = await self.catalog.fetch_all_objects(request.language)
        all_objects = response.objects

        # Step 2: Filter by domain if specified
        if request.domain_filter:
            all_objects = self._filter_by_domain(all_objects, request.domain_filter)

        if not all_objects:
            # No objects to update
            return UpdateCacheResponse(
                stats=UpdateStats(
                    total_objects=0, downloaded=0, already_cached=0, failed=0, duration_seconds=time.time() - start_time
                )
            )

        # Step 3: Find objects to download
        objects_to_download = self._find_objects_to_download(all_objects, request.force_refresh)

        total_objects = len(all_objects)
        already_cached = total_objects - len(objects_to_download)

        if not objects_to_download:
            # Everything already cached
            return UpdateCacheResponse(
                stats=UpdateStats(
                    total_objects=total_objects,
                    downloaded=0,
                    already_cached=already_cached,
                    failed=0,
                    duration_seconds=time.time() - start_time,
                )
            )

        # Step 4: Download missing objects with parallelism
        successful = 0
        failed = 0
        semaphore = asyncio.Semaphore(request.max_concurrent)

        async def download_one(obj: CatalogObject) -> None:
            """Download a single object with retry logic."""
            nonlocal successful, failed
            async with semaphore:
                success = await self._download_with_retry(obj.id, request.language)
                if success:
                    successful += 1
                else:
                    failed += 1

        # Execute all downloads in parallel
        tasks = [download_one(obj) for obj in objects_to_download]
        await asyncio.gather(*tasks)

        # Step 5: Update cache metadata
        self.cache.update_metadata(response.total_count, response.release)

        # Calculate final statistics
        duration = time.time() - start_time
        return UpdateCacheResponse(
            stats=UpdateStats(
                total_objects=total_objects,
                downloaded=successful,
                already_cached=already_cached,
                failed=failed,
                duration_seconds=duration,
            )
        )

    def _find_objects_to_download(self, all_objects: list[CatalogObject], force_refresh: bool) -> list[CatalogObject]:
        """Find objects that need to be downloaded.

        Args:
            all_objects: List of all objects from API
            force_refresh: If True, download all objects

        Returns:
            List of objects to download
        """
        if not self.cache:
            return all_objects

        if force_refresh:
            # Force refresh - download all objects
            return all_objects

        # Get currently cached objects
        cached_objects = {obj.id: obj for obj in self.cache.list_cached_objects()}

        # Find objects that need downloading
        to_download: list[CatalogObject] = []
        for obj in all_objects:
            cached_obj = cached_objects.get(obj.id)

            # Download if: not cached OR only summary cached (no property sets)
            if cached_obj is None or not cached_obj.has_property_sets():
                to_download.append(obj)

        return to_download

    async def _download_with_retry(self, object_id: str, language: LanguageCode, max_retries: int = 3) -> bool:
        """Download a single object with retry logic.

        Args:
            object_id: ID of object to download
            language: Language code
            max_retries: Maximum number of retry attempts

        Returns:
            True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                # Fetch object from catalog
                obj = await self.catalog.fetch_object_by_id(object_id, language)

                # Save to cache
                if self.cache:
                    self.cache.save_object(object_id, obj)

                return True

            except Exception:
                if attempt == max_retries - 1:
                    # Last attempt failed
                    return False

                # Exponential backoff: 1s, 2s, 4s
                await asyncio.sleep(2**attempt)

        return False

    @staticmethod
    def _filter_by_domain(objects: list[CatalogObject], domain_filter: str) -> list[CatalogObject]:
        """Filter objects by domain."""
        domain_lower = domain_filter.lower()
        return [obj for obj in objects if obj.domain.lower() == domain_lower]
