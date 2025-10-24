"""List Available Domains Use Case."""

from dataclasses import dataclass

from ..domain.entities import CatalogObject
from ..domain.repositories import CacheRepository, CatalogRepository
from ..models import LanguageCode


@dataclass
class ListDomainsRequest:
    """Request parameters for listing domains."""

    language: LanguageCode = "en"
    """Language code for fetching objects."""


@dataclass
class ListDomainsResponse:
    """Response containing domain summary."""

    domains: dict[str, int]
    """Dictionary mapping domain name to object count."""

    total_domains: int
    """Total number of unique domains."""

    total_objects: int
    """Total number of objects across all domains."""


class ListDomainsUseCase:
    """Use case for listing available domains with object counts.

    This use case handles:
    - Grouping catalog objects by domain
    - Counting objects per domain
    - Providing domain statistics

    Follows Clean Architecture:
    - Depends on abstractions (CatalogRepository, CacheRepository)
    - Works with domain entities (CatalogObject)
    - Single Responsibility: analyze and summarize domains
    """

    def __init__(self, catalog_repo: CatalogRepository, cache_repo: CacheRepository | None = None):
        """Initialize use case with repository dependencies.

        Args:
            catalog_repo: Repository for fetching catalog data from API
            cache_repo: Optional cache repository for performance optimization
        """
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: ListDomainsRequest) -> ListDomainsResponse:
        """Execute the list domains use case.

        Args:
            request: Request parameters with language

        Returns:
            ListDomainsResponse with domain statistics

        Raises:
            CatalogError: If catalog fetch fails
        """
        # Get all objects (prefer cache if available)
        objects = await self._get_objects(request.language)

        # Count objects per domain
        domain_counts = self._count_by_domain(objects)

        # Calculate statistics
        total_domains = len(domain_counts)
        total_objects = sum(domain_counts.values())

        return ListDomainsResponse(domains=domain_counts, total_domains=total_domains, total_objects=total_objects)

    async def _get_objects(self, language: LanguageCode) -> list[CatalogObject]:
        """Get all objects from cache or catalog.

        Prefers cache for performance, falls back to catalog if needed.

        Args:
            language: Language code for fetching objects

        Returns:
            List of catalog objects
        """
        # Try cache first
        if self.cache:
            cached_objects = self.cache.list_cached_objects()
            if cached_objects:
                return cached_objects

        # Fallback to catalog API
        response = await self.catalog.fetch_all_objects(language)
        return response.objects

    @staticmethod
    def _count_by_domain(objects: list[CatalogObject]) -> dict[str, int]:
        """Count objects grouped by domain.

        Args:
            objects: List of catalog objects

        Returns:
            Dictionary mapping domain name to object count
        """
        domain_counts: dict[str, int] = {}

        for obj in objects:
            domain = obj.domain if obj.domain else "Unknown"
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        return domain_counts
