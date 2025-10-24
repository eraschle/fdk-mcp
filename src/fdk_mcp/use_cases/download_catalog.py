"""Download All Catalog Objects Use Case."""

import asyncio
import time
from dataclasses import dataclass

from ..domain.entities import CatalogObject
from ..domain.repositories import CacheRepository, CatalogRepository
from ..models import LanguageCode


@dataclass
class DownloadStats:
    """Statistics about download operation."""

    total_objects: int
    """Total number of objects to download."""

    downloaded: int
    """Number of successfully downloaded objects."""

    cached: int
    """Number of objects already cached (same as downloaded)."""

    failed: int
    """Number of failed downloads."""

    duration_seconds: float
    """Total duration of download operation in seconds."""


@dataclass
class DownloadCatalogRequest:
    """Request parameters for downloading catalog."""

    language: LanguageCode = "en"
    """Language code for downloading objects."""

    domain_filter: str | None = None
    """Optional domain filter to download only specific domain."""

    max_concurrent: int = 10
    """Maximum number of concurrent downloads."""


@dataclass
class DownloadCatalogResponse:
    """Response containing download statistics."""

    stats: DownloadStats
    """Download statistics."""


class DownloadCatalogUseCase:
    """Use case for downloading all catalog objects to cache.

    This use case handles:
    - Fetching list of all object IDs
    - Downloading each object with full details
    - Concurrent downloads with configurable parallelism
    - Retry logic for failed downloads
    - Progress tracking and statistics
    - Saving all objects to cache

    Follows Clean Architecture:
    - Depends on abstractions (CatalogRepository, CacheRepository)
    - Works with domain entities (CatalogObject)
    - Single Responsibility: bulk download and cache catalog
    """

    def __init__(self, catalog_repo: CatalogRepository, cache_repo: CacheRepository | None = None):
        """Initialize use case with repository dependencies.

        Args:
            catalog_repo: Repository for fetching catalog data from API
            cache_repo: Optional cache repository for storing downloaded objects
        """
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: DownloadCatalogRequest) -> DownloadCatalogResponse:
        """Execute the download catalog use case.

        Args:
            request: Request parameters with language and filters

        Returns:
            DownloadCatalogResponse with download statistics

        Raises:
            CatalogError: If initial catalog fetch fails
        """
        start_time = time.time()

        # Step 1: Get list of all objects
        response = await self.catalog.fetch_all_objects(request.language)
        all_objects = response.objects

        # Step 2: Filter by domain if specified
        if request.domain_filter:
            all_objects = self._filter_by_domain(all_objects, request.domain_filter)

        if not all_objects:
            # No objects to download
            return DownloadCatalogResponse(
                stats=DownloadStats(
                    total_objects=0, downloaded=0, cached=0, failed=0, duration_seconds=time.time() - start_time
                )
            )

        # Step 3: Download all objects with parallelism
        total = len(all_objects)
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
        tasks = [download_one(obj) for obj in all_objects]
        await asyncio.gather(*tasks)

        # Step 4: Update cache metadata
        if self.cache:
            self.cache.update_metadata(response.total_count, response.release)

        # Calculate final statistics
        duration = time.time() - start_time
        return DownloadCatalogResponse(
            stats=DownloadStats(
                total_objects=total, downloaded=successful, cached=successful, failed=failed, duration_seconds=duration
            )
        )

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

                # Save to cache (if available)
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
