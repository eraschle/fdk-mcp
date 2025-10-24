"""Get Single Object Details Use Case."""

from dataclasses import dataclass

from ..domain.entities import CatalogObject
from ..domain.repositories import CacheRepository, CatalogRepository
from ..models import LanguageCode


@dataclass
class GetObjectRequest:
    """Request parameters for getting a single catalog object."""

    object_id: str
    """Unique identifier of the object to retrieve."""

    language: LanguageCode = "en"
    """Language code for fetching object details."""


@dataclass
class GetObjectResponse:
    """Response containing a single catalog object with full details."""

    object: CatalogObject
    """Catalog object with complete property sets."""

    from_cache: bool = False
    """Indicates whether object was retrieved from cache."""


class GetObjectUseCase:
    """Use case for retrieving a single catalog object with full details.

    This use case handles:
    - Cache-first strategy (check cache before API)
    - Fetching from API if not cached or cache stale
    - Saving fetched objects to cache
    - Fallback to cached summary if API fails

    Follows Clean Architecture:
    - Depends on abstractions (CatalogRepository, CacheRepository)
    - Works with domain entities (CatalogObject)
    - Single Responsibility: retrieve single object with caching logic
    """

    def __init__(self, catalog_repo: CatalogRepository, cache_repo: CacheRepository | None = None):
        """Initialize use case with repository dependencies.

        Args:
            catalog_repo: Repository for fetching catalog data from API
            cache_repo: Optional cache repository for performance optimization
        """
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: GetObjectRequest) -> GetObjectResponse:
        """Execute the get object use case.

        Strategy:
        1. Check cache first for object with full property sets
        2. If not cached or incomplete, fetch from API
        3. Save fetched object to cache
        4. Return object with cache indicator

        Args:
            request: Request parameters with object ID and language

        Returns:
            GetObjectResponse with the catalog object

        Raises:
            ObjectNotFoundError: If object doesn't exist
            CatalogError: If API fetch fails and no cached fallback
        """
        # Step 1: Check cache first (if available)
        if self.cache:
            cached_obj = self.cache.get_cached_object(request.object_id)

            # If cached object has property sets (detail object), use it
            if cached_obj and cached_obj.has_property_sets():
                return GetObjectResponse(object=cached_obj, from_cache=True)

        # Step 2: Fetch from API (not cached or only summary cached)
        try:
            obj = await self.catalog.fetch_object_by_id(object_id=request.object_id, language=request.language)

            # Step 3: Save to cache (if cache available)
            if self.cache:
                self.cache.save_object(request.object_id, obj)

            return GetObjectResponse(object=obj, from_cache=False)

        except Exception as e:
            # Step 4: Fallback to cached summary if API fails
            if self.cache:
                cached_obj = self.cache.get_cached_object(request.object_id)
                if cached_obj:
                    # Return cached summary even without property sets
                    return GetObjectResponse(object=cached_obj, from_cache=True)

            # No fallback available - re-raise error
            raise e
