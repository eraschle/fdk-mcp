"""Search Properties Across Objects Use Case."""

from dataclasses import dataclass

from ..domain.entities import CatalogObject, Property
from ..domain.repositories import CacheRepository, CatalogRepository
from ..models import LanguageCode


@dataclass
class PropertyMatch:
    """A single property match result."""

    property: Property
    """The matched property."""

    object_id: str
    """ID of the object containing this property."""

    object_name: str
    """Name of the object containing this property."""

    property_set_name: str
    """Name of the property set containing this property."""


@dataclass
class SearchPropertiesRequest:
    """Request parameters for searching properties."""

    query: str
    """Search term to find in property names."""

    language: LanguageCode = "en"
    """Language code for fetching objects."""

    limit: int | None = None
    """Optional limit on number of results."""


@dataclass
class SearchPropertiesResponse:
    """Response containing property search results."""

    matches: list[PropertyMatch]
    """List of matching properties with context."""

    total_matches: int
    """Total number of matches found."""


class SearchPropertiesUseCase:
    """Use case for searching properties across all catalog objects.

    This use case handles:
    - Searching property names across all objects
    - Fuzzy matching (case-insensitive, partial match)
    - Returning properties with context (object, property set)
    - Working with cached objects (requires detail objects)

    Follows Clean Architecture:
    - Depends on abstractions (CatalogRepository, CacheRepository)
    - Works with domain entities (CatalogObject, Property)
    - Single Responsibility: search properties across catalog
    """

    def __init__(self, catalog_repo: CatalogRepository, cache_repo: CacheRepository | None = None):
        """Initialize use case with repository dependencies.

        Args:
            catalog_repo: Repository for fetching catalog data from API
            cache_repo: Optional cache repository for performance optimization
        """
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: SearchPropertiesRequest) -> SearchPropertiesResponse:
        """Execute the search properties use case.

        Args:
            request: Request parameters with search query

        Returns:
            SearchPropertiesResponse with matching properties

        Raises:
            CatalogError: If catalog fetch fails
        """
        query_lower = request.query.lower()
        matches: list[PropertyMatch] = []

        # Get all objects (prefer cache if available for performance)
        objects = await self._get_objects(request.language)

        # Search through all objects and their properties
        for obj in objects:
            # Only search in objects with property sets (detail objects)
            if not obj.has_property_sets():
                continue

            # Search in each property set
            for pset in obj.property_sets:
                for prop in pset.properties:
                    # Fuzzy match: case-insensitive, partial match in property name
                    if query_lower in prop.name.lower():
                        match = PropertyMatch(
                            property=prop, object_id=obj.id, object_name=obj.name, property_set_name=pset.name
                        )
                        matches.append(match)

        # Apply limit if specified
        total_matches = len(matches)
        if request.limit is not None:
            matches = matches[: request.limit]

        return SearchPropertiesResponse(matches=matches, total_matches=total_matches)

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
