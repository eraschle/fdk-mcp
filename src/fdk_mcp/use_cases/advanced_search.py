"""Advanced Multi-field Search Use Case."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..domain.entities import CatalogObject
from ..domain.repositories import CacheRepository, CatalogRepository
from ..models import LanguageCode


class MatchMode(str, Enum):
    """Match mode for search operations."""

    CONTAINS = "contains"
    EQUALS = "equals"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


@dataclass
class SearchMatch:
    """A single search match result."""

    object_id: str
    """ID of the object containing the match."""

    object_name: str
    """Name of the object containing the match."""

    domain: str
    """Domain of the object."""

    field: str
    """Field where match was found."""

    match_path: str
    """JSON path to the matched value (e.g., 'name', 'propertySets[0].properties[1].name')."""

    matched_value: str
    """The actual value that matched."""

    property_set_name: str | None = None
    """Property set name if match is in properties."""


@dataclass
class AdvancedSearchRequest:
    """Request parameters for advanced search."""

    search_fields: list[str]
    """List of fields to search in (e.g., ['name', 'description']) or ['all']."""

    query: str
    """Search query to find in specified fields."""

    domain_filter: str | None = None
    """Optional domain filter."""

    match_mode: MatchMode = MatchMode.CONTAINS
    """How to match the query."""

    case_sensitive: bool = False
    """Whether search should be case-sensitive."""

    language: LanguageCode = "en"
    """Language code for fetching objects."""

    limit: int | None = None
    """Optional limit on number of results."""


@dataclass
class AdvancedSearchResponse:
    """Response containing advanced search results."""

    matches: list[SearchMatch]
    """List of search matches."""

    total_matches: int
    """Total number of matches found."""


class AdvancedSearchUseCase:
    """Use case for advanced multi-field search across catalog objects.

    This use case handles:
    - Searching across multiple fields (name, description, properties, etc.)
    - Multiple match modes (contains, equals, starts_with, ends_with)
    - Case-sensitive and case-insensitive search
    - Domain filtering
    - Auto-downloading detail objects when needed
    - Recursive search in nested structures

    Follows Clean Architecture:
    - Depends on abstractions (CatalogRepository, CacheRepository)
    - Works with domain entities (CatalogObject)
    - Single Responsibility: advanced search across multiple fields
    """

    def __init__(self, catalog_repo: CatalogRepository, cache_repo: CacheRepository | None = None):
        """Initialize use case with repository dependencies.

        Args:
            catalog_repo: Repository for fetching catalog data from API
            cache_repo: Optional cache repository for performance optimization
        """
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: AdvancedSearchRequest) -> AdvancedSearchResponse:
        """Execute the advanced search use case.

        Args:
            request: Request parameters with search criteria

        Returns:
            AdvancedSearchResponse with matching results

        Raises:
            CatalogError: If catalog fetch fails
        """
        matches: list[SearchMatch] = []

        # Ensure cache has basic object data
        await self._ensure_cache_fresh(request.language)

        # Get objects from cache (preferred for performance)
        objects = await self._get_objects(request.language)

        # Filter by domain if specified
        if request.domain_filter:
            objects = self._filter_by_domain(objects, request.domain_filter)

        # First, batch-download all needed detail objects (parallel)
        objects = await self._batch_ensure_details(objects, request.search_fields, request.language)

        # Then process each object for searching
        for obj in objects:
            # Determine which fields to search
            fields_to_search = self._determine_search_fields(request.search_fields, obj)

            # Search in each field
            for field in fields_to_search:
                field_matches = self._search_in_field(obj, field, request)
                matches.extend(field_matches)

        # Apply limit if specified
        total_matches = len(matches)
        if request.limit is not None:
            matches = matches[: request.limit]

        return AdvancedSearchResponse(matches=matches, total_matches=total_matches)

    async def _ensure_cache_fresh(self, language: LanguageCode) -> None:
        """Ensure cache has fresh data."""
        if not self.cache:
            return

        response = await self.catalog.fetch_all_objects(language)

        if self.cache.is_cache_fresh(response.release):
            return

        # Update cache
        for obj in response.objects:
            self.cache.save_object(obj.id, obj)

        self.cache.update_metadata(response.total_count, response.release)

    async def _get_objects(self, language: LanguageCode) -> list[CatalogObject]:
        """Get all objects from cache or catalog."""
        if self.cache:
            cached_objects = self.cache.list_cached_objects()
            if cached_objects:
                return cached_objects

        response = await self.catalog.fetch_all_objects(language)
        return response.objects

    @staticmethod
    def _filter_by_domain(objects: list[CatalogObject], domain_filter: str) -> list[CatalogObject]:
        """Filter objects by domain."""
        domain_lower = domain_filter.lower()
        return [obj for obj in objects if obj.domain.lower() == domain_lower]

    @staticmethod
    def _needs_detail_object(search_fields: list[str], obj: CatalogObject) -> bool:
        """Check if we need to download detail object for search."""
        detail_fields = {
            "property_sets",
            "propertySets",  # Alternative name for PropertySets
            "properties",
            "relationships",
            "classifications",
            "description",
        }

        # Need details if searching in detail fields and object doesn't have them
        return ("all" in search_fields or any(field in detail_fields for field in search_fields)) and (
            not obj.has_property_sets()
        )

    async def _batch_ensure_details(
        self, objects: list[CatalogObject], search_fields: list[str], language: LanguageCode
    ) -> list[CatalogObject]:
        """Batch-download detail objects in parallel (much faster).

        Args:
            objects: List of objects (may be summaries or details)
            search_fields: Fields to search (determines if details needed)
            language: Language code

        Returns:
            List of objects with details loaded where needed
        """
        import asyncio

        # Identify which objects need details
        to_download = []
        indices = []
        for idx, obj in enumerate(objects):
            if self._needs_detail_object(search_fields, obj):
                to_download.append(obj)
                indices.append(idx)

        if not to_download:
            return objects  # No downloads needed

        # Download all in parallel (with semaphore for rate limiting)
        max_concurrent = 20  # Configurable
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_one(obj: CatalogObject) -> CatalogObject:
            async with semaphore:
                return await self._ensure_detail_object(obj, language)

        # Execute downloads in parallel
        tasks = [download_one(obj) for obj in to_download]
        downloaded = await asyncio.gather(*tasks, return_exceptions=True)

        # Replace objects with downloaded versions
        result = list(objects)  # Copy
        for idx, detail_obj in zip(indices, downloaded, strict=True):
            if isinstance(detail_obj, CatalogObject):
                result[idx] = detail_obj

        return result

    async def _ensure_detail_object(self, obj: CatalogObject, language: LanguageCode) -> CatalogObject:
        """Ensure we have detail object (download if needed)."""
        try:
            detail_obj = await self.catalog.fetch_object_by_id(obj.id, language)

            # Cache the detail object
            if self.cache:
                self.cache.save_object(obj.id, detail_obj)

            return detail_obj
        except Exception:
            # Return original object on failure
            return obj

    @staticmethod
    def _determine_search_fields(search_fields: list[str], obj: CatalogObject) -> list[str]:
        """Determine which fields to search based on request."""
        if "all" in search_fields:
            # Search in all simple string fields
            return ["name", "domain", "description"]

        return search_fields

    def _search_in_field(self, obj: CatalogObject, field: str, request: AdvancedSearchRequest) -> list[SearchMatch]:
        """Search in a specific field of the object."""
        matches: list[SearchMatch] = []

        # Special handling for properties (nested structure)
        if field == "properties":
            return self._search_in_properties(obj, request)

        # Special handling for propertySets (search in PropertySet names)
        if field == "propertySets":
            return self._search_in_property_sets(obj, request)

        # Get field value
        field_value = self._get_field_value(obj, field)
        if field_value is None:
            return matches

        # Convert to dict for recursive search
        search_results = self._search_in_value(
            field_value, request.query, request.match_mode, request.case_sensitive, field
        )

        # Convert to SearchMatch objects
        for result in search_results:
            matches.append(
                SearchMatch(
                    object_id=obj.id,
                    object_name=obj.name,
                    domain=obj.domain,
                    field=field,
                    match_path=result["path"],
                    matched_value=result["value"],
                )
            )

        return matches

    def _search_in_property_sets(self, obj: CatalogObject, request: AdvancedSearchRequest) -> list[SearchMatch]:
        """Search in PropertySet names."""
        matches: list[SearchMatch] = []

        for pset in obj.property_sets:
            # Search in PropertySet name
            if self._match_value(pset.name, request.query, request.match_mode, request.case_sensitive):
                matches.append(
                    SearchMatch(
                        object_id=obj.id,
                        object_name=obj.name,
                        domain=obj.domain,
                        field="propertySets",
                        match_path=pset.name,
                        matched_value=pset.name,
                        property_set_name=pset.name,
                    )
                )

        return matches

    def _search_in_properties(self, obj: CatalogObject, request: AdvancedSearchRequest) -> list[SearchMatch]:
        """Search in object properties (nested in property sets)."""
        matches: list[SearchMatch] = []

        for pset in obj.property_sets:
            for prop in pset.properties:
                # Search in property name and value
                if self._match_value(prop.name, request.query, request.match_mode, request.case_sensitive):
                    matches.append(
                        SearchMatch(
                            object_id=obj.id,
                            object_name=obj.name,
                            domain=obj.domain,
                            field="properties",
                            match_path=f"{pset.name}.{prop.name}",
                            matched_value=prop.name,
                            property_set_name=pset.name,
                        )
                    )

                # Search in property value if it's a string
                if isinstance(prop.value, str) and self._match_value(
                    prop.value, request.query, request.match_mode, request.case_sensitive
                ):
                    matches.append(
                        SearchMatch(
                            object_id=obj.id,
                            object_name=obj.name,
                            domain=obj.domain,
                            field="properties",
                            match_path=f"{pset.name}.{prop.name}",
                            matched_value=str(prop.value),
                            property_set_name=pset.name,
                        )
                    )

        return matches

    @staticmethod
    def _get_field_value(obj: CatalogObject, field: str) -> Any:
        """Get field value from object."""
        field_map = {
            "name": obj.name,
            "domain": obj.domain,
            "description": obj.description,
            "classifications": obj.classifications,
        }
        return field_map.get(field)

    @staticmethod
    def _match_value(value: str, query: str, match_mode: MatchMode, case_sensitive: bool) -> bool:
        """Check if value matches query based on match mode."""
        if not case_sensitive:
            value = value.lower()
            query = query.lower()

        if match_mode == MatchMode.CONTAINS:
            return query in value
        elif match_mode == MatchMode.EQUALS:
            return value == query
        elif match_mode == MatchMode.STARTS_WITH:
            return value.startswith(query)
        elif match_mode == MatchMode.ENDS_WITH:
            return value.endswith(query)

        return False

    def _search_in_value(
        self, value: Any, query: str, match_mode: MatchMode, case_sensitive: bool, current_path: str = ""
    ) -> list[dict[str, Any]]:
        """Recursively search in a value (string, dict, list)."""
        matches: list[dict[str, Any]] = []

        if isinstance(value, str):
            if self._match_value(value, query, match_mode, case_sensitive):
                matches.append({"path": current_path, "value": value})

        elif isinstance(value, dict):
            for key, val in value.items():
                new_path = f"{current_path}.{key}" if current_path else key
                matches.extend(self._search_in_value(val, query, match_mode, case_sensitive, new_path))

        elif isinstance(value, list):
            for idx, item in enumerate(value):
                new_path = f"{current_path}[{idx}]"
                matches.extend(self._search_in_value(item, query, match_mode, case_sensitive, new_path))

        return matches
