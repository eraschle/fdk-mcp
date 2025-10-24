"""Get Cache Coverage Use Case."""

from dataclasses import dataclass

from ..domain.repositories import CacheCoverageStats, CacheRepository, CatalogRepository
from ..models import LanguageCode


@dataclass
class GetCacheCoverageRequest:
    """Request for cache coverage analysis."""

    language: LanguageCode = "de"
    """Language for fetching object list."""

    domain_filter: str | None = None
    """Optional domain to analyze coverage for."""


@dataclass
class GetCacheCoverageResponse:
    """Response with cache coverage statistics."""

    stats: CacheCoverageStats
    """Coverage statistics."""


class GetCacheCoverageUseCase:
    """Analyze cache coverage to estimate download needs.

    This use case helps inform the user about:
    - How many objects are already cached
    - How many need to be downloaded
    - Estimated time for downloads

    Follows Clean Architecture:
    - Depends on abstractions (CatalogRepository, CacheRepository)
    - Works with domain entities (CacheCoverageStats)
    - Single Responsibility: analyzing cache coverage
    """

    def __init__(self, catalog_repo: CatalogRepository, cache_repo: CacheRepository | None = None):
        """Initialize use case with repository dependencies.

        Args:
            catalog_repo: Repository for fetching catalog data from API
            cache_repo: Optional cache repository for analyzing coverage
        """
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: GetCacheCoverageRequest) -> GetCacheCoverageResponse:
        """Execute cache coverage analysis.

        Args:
            request: Request parameters with language and optional domain filter

        Returns:
            GetCacheCoverageResponse with coverage statistics

        Raises:
            CatalogError: If catalog fetch fails
        """
        # Fetch all objects from API (summary only, fast!)
        response = await self.catalog.fetch_all_objects(request.language)
        all_objects = response.objects

        # Filter by domain if specified
        if request.domain_filter:
            domain_lower = request.domain_filter.lower()
            all_objects = [obj for obj in all_objects if obj.domain.lower() == domain_lower]

        # Get all object IDs
        all_object_ids = [obj.id for obj in all_objects]

        # If no cache, all objects need downloading
        if not self.cache:
            total = len(all_object_ids)
            estimated_time = int((total / 20) * 0.5 * 20) if total > 0 else None

            stats = CacheCoverageStats(
                total_objects=total,
                cached_with_details=0,
                cached_summary_only=0,
                not_cached=total,
                coverage_percentage=0.0,
                estimated_download_time_seconds=estimated_time,
                missing_object_ids=all_object_ids if all_object_ids else None,
            )
            return GetCacheCoverageResponse(stats=stats)

        # Analyze cache coverage
        stats = self.cache.get_cache_coverage(all_object_ids, check_detail_level=True)

        return GetCacheCoverageResponse(stats=stats)
