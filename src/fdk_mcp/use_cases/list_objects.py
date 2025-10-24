"""List/Search Catalog Objects Use Case."""

from dataclasses import dataclass

from ..domain.entities import CatalogObject
from ..domain.repositories import CacheRepository, CatalogRepository
from ..models import LanguageCode


@dataclass
class ListObjectsRequest:
    """Request parameters for listing catalog objects."""

    domain_filter: str | None = None
    """Filter objects by domain name."""

    search_query: str | None = None
    """Search term for object names."""

    language: LanguageCode = "en"
    """Language code for fetching objects."""

    limit: int = 20
    """Maximum number of results to return."""

    offset: int = 0
    """Number of results to skip for pagination."""


@dataclass
class ListObjectsResponse:
    """Response containing list of catalog objects."""

    objects: list[CatalogObject]
    """List of catalog objects matching criteria."""

    total: int
    """Total number of objects matching criteria (before pagination)."""


class ListObjectsUseCase:
    """Use case for listing and searching catalog objects.

    This use case handles:
    - Fetching objects from catalog or cache
    - Filtering by domain
    - Searching by name
    - Pagination

    Follows Clean Architecture:
    - Depends on abstractions (CatalogRepository, CacheRepository)
    - Works with domain entities (CatalogObject)
    - Single Responsibility: list and filter objects
    """

    def __init__(self, catalog_repo: CatalogRepository, cache_repo: CacheRepository | None = None):
        """Initialize use case with repository dependencies.

        Args:
            catalog_repo: Repository for fetching catalog data from API
            cache_repo: Optional cache repository for performance optimization
        """
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: ListObjectsRequest) -> ListObjectsResponse:
        """Execute the list objects use case.

        Args:
            request: Request parameters for listing/searching objects

        Returns:
            ListObjectsResponse with filtered and paginated objects

        Raises:
            CatalogError: If catalog fetch fails
        """
        # Step 1: Ensure cache is fresh (if cache exists)
        if self.cache:
            await self._ensure_cache_fresh()

        # Step 2: Get objects from catalog
        response = await self.catalog.fetch_all_objects(request.language)
        objects = response.objects

        # Step 3: Apply domain filter
        if request.domain_filter:
            objects = self._filter_by_domain(objects, request.domain_filter)

        # Step 4: Apply search query filter
        if request.search_query:
            objects = self._filter_by_search(objects, request.search_query)

        # Step 5: Apply pagination
        total = len(objects)
        paginated_objects = self._paginate(objects, request.limit, request.offset)

        return ListObjectsResponse(objects=paginated_objects, total=total)

    async def _ensure_cache_fresh(self) -> None:
        """Ensure cache has fresh data by checking release info.

        This method:
        1. Fetches current release info from catalog
        2. Checks if cache is fresh
        3. Updates cache if stale
        """
        if not self.cache:
            return

        # Fetch current release info
        response = await self.catalog.fetch_all_objects()

        # Check if cache needs refresh
        if self.cache.is_cache_fresh(response.release):
            return

        # Cache is stale - update it with all objects
        for obj in response.objects:
            self.cache.save_object(obj.id, obj)

        # Update cache metadata
        self.cache.update_metadata(response.total_count, response.release)

    @staticmethod
    def _filter_by_domain(objects: list[CatalogObject], domain_filter: str) -> list[CatalogObject]:
        """Filter objects by domain name (case-insensitive).

        Args:
            objects: List of objects to filter
            domain_filter: Domain name to match

        Returns:
            Filtered list of objects
        """
        domain_lower = domain_filter.lower()
        return [obj for obj in objects if obj.domain.lower() == domain_lower]

    @staticmethod
    def _filter_by_search(objects: list[CatalogObject], search_query: str) -> list[CatalogObject]:
        """Filter objects by search query in name (case-insensitive).

        Args:
            objects: List of objects to filter
            search_query: Search term to match in object names

        Returns:
            Filtered list of objects
        """
        query_lower = search_query.lower()
        return [obj for obj in objects if query_lower in obj.name.lower()]

    @staticmethod
    def _paginate(objects: list[CatalogObject], limit: int, offset: int) -> list[CatalogObject]:
        """Apply pagination to object list.

        Args:
            objects: List of objects to paginate
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Paginated list of objects
        """
        return objects[offset : offset + limit]
