"""Group and Sort Objects Use Case."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from ..domain.entities import CatalogObject
from ..domain.repositories import CacheRepository, CatalogRepository
from ..models import GroupField, LanguageCode, SortField, SortOrder


@dataclass
class GroupObjectsRequest:
    """Request for grouping and sorting objects."""

    object_ids: list[str]
    """List of object IDs to group/sort."""

    group_by: GroupField | list[GroupField] | None = None
    """Field(s) to group by. None = no grouping (just sort).

    Supported fields:
    - "domain": Domain name
    - "ifcClass": IFC classification (first one if multiple)
    - "propertySet": PropertySet name (creates multiple groups per object)
    - "name": Object name
    """

    sort_by: SortField | None = None
    """Field to sort by (within groups if grouped).

    Supported fields:
    - "name": Object name
    - "id": Object ID
    - "domain": Domain name
    """

    order: SortOrder = "asc"
    """Sort order: 'asc' or 'desc'."""

    include_count: bool = True
    """Include count of objects in each group."""

    language: LanguageCode = "de"
    """Language for fetching objects."""


@dataclass
class GroupedObjects:
    """Container for grouped objects."""

    groups: dict[str, Any]
    """Grouped objects. Structure depends on group_by:
    - Single field: {group_name: [objects]}
    - Multiple fields: {level1: {level2: [objects]}}
    - None (sort only): {"all": [objects]}
    """

    total_objects: int
    """Total number of objects processed."""

    group_counts: dict[str, int] | None = None
    """Count of objects per group (flat, even for nested groups)."""


@dataclass
class GroupObjectsResponse:
    """Response with grouped/sorted objects."""

    result: GroupedObjects
    """Grouped and sorted objects."""


class GroupObjectsUseCase:
    """Group and sort catalog objects by attributes.

    This use case allows flexible organization of objects:
    - Group by single or multiple attributes
    - Sort within groups
    - Extract attribute values (domain, IFC class, PropertySets, etc.)

    Follows Clean Architecture:
    - Depends on abstractions (CatalogRepository, CacheRepository)
    - Works with domain entities (CatalogObject)
    - Single Responsibility: organizing objects
    """

    def __init__(self, catalog_repo: CatalogRepository, cache_repo: CacheRepository | None = None):
        """Initialize use case with repository dependencies.

        Args:
            catalog_repo: Repository for fetching catalog data
            cache_repo: Optional cache repository
        """
        self.catalog = catalog_repo
        self.cache = cache_repo

    async def execute(self, request: GroupObjectsRequest) -> GroupObjectsResponse:
        """Execute grouping and sorting.

        Args:
            request: Request with object IDs and grouping parameters

        Returns:
            GroupObjectsResponse with organized objects

        Raises:
            CatalogError: If object fetch fails
        """
        # Fetch all requested objects in parallel
        objects = await self._fetch_objects(request.object_ids, request.language)

        # If no grouping, just sort
        if not request.group_by:
            sorted_objects = self._sort_objects(objects, request.sort_by, request.order)
            return GroupObjectsResponse(
                result=GroupedObjects(
                    groups={"all": sorted_objects},
                    total_objects=len(objects),
                    group_counts={"all": len(objects)} if request.include_count else None,
                )
            )

        # Group objects
        if isinstance(request.group_by, list):
            # Multi-level grouping
            groups = self._group_by_multiple(objects, request.group_by)
        else:
            # Single-level grouping
            groups = self._group_by_single(objects, request.group_by)

        # Sort within groups if requested
        if request.sort_by:
            groups = self._sort_groups(groups, request.sort_by, request.order)

        # Calculate counts if requested
        group_counts = None
        if request.include_count:
            group_counts = self._calculate_counts(groups)

        return GroupObjectsResponse(
            result=GroupedObjects(groups=groups, total_objects=len(objects), group_counts=group_counts)
        )

    async def _fetch_objects(self, object_ids: list[str], language: LanguageCode) -> list[CatalogObject]:
        """Fetch objects by IDs in parallel.

        Args:
            object_ids: List of object IDs
            language: Language code

        Returns:
            List of CatalogObjects
        """
        import asyncio

        # Try cache first
        cached_objects = []
        missing_ids = []

        if self.cache:
            for oid in object_ids:
                cached = self.cache.get_cached_object(oid)
                if cached:
                    cached_objects.append(cached)
                else:
                    missing_ids.append(oid)
        else:
            missing_ids = object_ids

        # Fetch missing objects in parallel
        if missing_ids:
            max_concurrent = 20
            semaphore = asyncio.Semaphore(max_concurrent)

            async def fetch_one(oid: str) -> CatalogObject | None:
                async with semaphore:
                    try:
                        return await self.catalog.fetch_object_by_id(oid, language)
                    except Exception:
                        return None

            tasks = [fetch_one(oid) for oid in missing_ids]
            fetched = await asyncio.gather(*tasks)

            # Filter out None (failed fetches)
            for obj in fetched:
                if obj:
                    cached_objects.append(obj)
                    # Cache for future use
                    if self.cache:
                        self.cache.save_object(obj.id, obj)

        return cached_objects

    def _group_by_single(self, objects: list[CatalogObject], field: str) -> dict[str, list[CatalogObject]]:
        """Group objects by a single field.

        Args:
            objects: List of objects to group
            field: Field name to group by

        Returns:
            Dictionary with groups
        """
        groups: dict[str, list[CatalogObject]] = defaultdict(list)

        for obj in objects:
            # Special handling for propertySet (one object can have multiple)
            if field == "propertySet":
                for pset in obj.property_sets:
                    groups[pset.name].append(obj)
            else:
                # Get field value
                value = self._get_field_value(obj, field)
                if value:
                    groups[value].append(obj)

        return dict(groups)

    def _group_by_multiple(self, objects: list[CatalogObject], fields: list[GroupField]) -> dict[str, Any]:
        """Group objects by multiple fields (nested grouping).

        Args:
            objects: List of objects to group
            fields: List of field names (in order)

        Returns:
            Nested dictionary with groups
        """
        if not fields:
            return {"all": objects}

        # Group by first field
        first_field = fields[0]
        remaining_fields = fields[1:]

        first_level_groups = self._group_by_single(objects, first_field)

        # If no more fields, return
        if not remaining_fields:
            return first_level_groups

        # Recursively group remaining levels
        result = {}
        for group_name, group_objects in first_level_groups.items():
            result[group_name] = self._group_by_multiple(group_objects, remaining_fields)

        return result

    def _get_field_value(self, obj: CatalogObject, field: str) -> str | None:
        """Extract field value from object.

        Args:
            obj: CatalogObject
            field: Field name

        Returns:
            Field value as string or None
        """
        if field == "domain":
            return obj.domain
        elif field == "name":
            return obj.name
        elif field == "id":
            return obj.id
        elif field == "ifcClass":
            # Return first IFC classification
            if obj.classifications:
                return obj.classifications[0]
            return "No IFC Class"
        else:
            return None

    def _sort_objects(
        self, objects: list[CatalogObject], sort_by: SortField | None, order: SortOrder
    ) -> list[CatalogObject]:
        """Sort objects by field.

        Args:
            objects: List of objects
            sort_by: Field to sort by
            order: 'asc' or 'desc'

        Returns:
            Sorted list of objects
        """
        if not sort_by:
            return objects

        def get_sort_key(obj: CatalogObject) -> str:
            value = self._get_field_value(obj, sort_by)
            return value if value else ""

        reverse = order == "desc"
        return sorted(objects, key=get_sort_key, reverse=reverse)

    def _sort_groups(self, groups: dict[str, Any], sort_by: SortField, order: SortOrder) -> dict[str, Any]:
        """Sort objects within groups.

        Args:
            groups: Grouped objects (can be nested)
            sort_by: Field to sort by
            order: 'asc' or 'desc'

        Returns:
            Groups with sorted objects
        """
        result = {}
        for group_name, group_content in groups.items():
            if isinstance(group_content, list):
                # Leaf level: sort objects
                result[group_name] = self._sort_objects(group_content, sort_by, order)
            elif isinstance(group_content, dict):
                # Nested level: recursively sort
                result[group_name] = self._sort_groups(group_content, sort_by, order)
            else:
                result[group_name] = group_content

        return result

    def _calculate_counts(self, groups: dict[str, Any]) -> dict[str, int]:
        """Calculate object counts per group (flat structure).

        Args:
            groups: Grouped objects (can be nested)

        Returns:
            Flat dictionary with counts
        """
        counts: dict[str, int] = {}

        def count_recursive(prefix: str, content: Any) -> None:
            if isinstance(content, list):
                counts[prefix] = len(content)
            elif isinstance(content, dict):
                for key, value in content.items():
                    new_prefix = f"{prefix}/{key}" if prefix else key
                    count_recursive(new_prefix, value)

        count_recursive("", groups)
        return counts
