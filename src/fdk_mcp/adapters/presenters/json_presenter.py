"""JSON presenter for formatting domain entities as JSON."""

import json
from typing import Any

from ...domain.entities import CatalogObject, Property, PropertySet
from ...domain.repositories import CacheCoverageStats
from ...use_cases import GroupedObjects, PropertyMatch, SearchMatch


class JsonPresenter:
    """Format domain objects as JSON for MCP responses.

    This presenter converts domain entities into JSON format
    suitable for programmatic consumption by MCP clients.

    Examples:
        >>> presenter = JsonPresenter()
        >>> json_str = presenter.format_object(obj)
        >>> data = json.loads(json_str)
    """

    def format_object(self, obj: CatalogObject, from_cache: bool = False) -> str:
        """Format single object as JSON.

        Args:
            obj: Catalog object to format
            from_cache: Whether object was loaded from cache

        Returns:
            JSON-formatted string with object data
        """
        data = self._catalog_object_to_dict(obj)
        if from_cache:
            data["_from_cache"] = True

        return json.dumps(data, indent=2, ensure_ascii=False)

    def format_object_list(self, objects: list[CatalogObject], total: int, offset: int = 0) -> str:
        """Format list of objects as JSON.

        Args:
            objects: List of catalog objects
            total: Total number of matching objects
            offset: Pagination offset

        Returns:
            JSON-formatted string with object list and metadata
        """
        return json.dumps(
            {
                "total": total,
                "count": len(objects),
                "offset": offset,
                "data": [self._catalog_object_to_dict(obj) for obj in objects],
            },
            indent=2,
            ensure_ascii=False,
        )

    def format_property_matches(self, matches: list[PropertyMatch], total: int) -> str:
        """Format property search matches as JSON.

        Args:
            matches: List of property matches
            total: Total number of matches

        Returns:
            JSON-formatted string with property matches
        """
        return json.dumps(
            {"total": total, "count": len(matches), "data": [self._property_match_to_dict(match) for match in matches]},
            indent=2,
            ensure_ascii=False,
        )

    def format_domains_summary(self, domains: dict[str, int], total_domains: int, total_objects: int) -> str:
        """Format domains summary as JSON.

        Args:
            domains: Dict mapping domain name to object count
            total_domains: Total number of unique domains
            total_objects: Total number of objects

        Returns:
            JSON-formatted string with domains summary
        """
        return json.dumps(
            {"total_domains": total_domains, "total_objects": total_objects, "domains": domains},
            indent=2,
            ensure_ascii=False,
        )

    def format_search_matches(self, matches: list[SearchMatch], total: int) -> str:
        """Format advanced search matches as JSON.

        Args:
            matches: List of search matches
            total: Total number of matches

        Returns:
            JSON-formatted string with search results
        """
        return json.dumps(
            {"total": total, "count": len(matches), "data": [self._search_match_to_dict(match) for match in matches]},
            indent=2,
            ensure_ascii=False,
        )

    def format_download_stats(self, total: int, downloaded: int, cached: int, failed: int, duration: float) -> str:
        """Format download statistics as JSON.

        Args:
            total: Total number of objects
            downloaded: Number of objects downloaded
            cached: Number of objects already cached
            failed: Number of failed downloads
            duration: Duration in seconds

        Returns:
            JSON-formatted string with download statistics
        """
        success_rate = ((downloaded + cached) / total * 100) if total > 0 else 0.0

        return json.dumps(
            {
                "total": total,
                "downloaded": downloaded,
                "already_cached": cached,
                "failed": failed,
                "duration_seconds": round(duration, 2),
                "success_rate_percent": round(success_rate, 1),
            },
            indent=2,
            ensure_ascii=False,
        )

    def format_cache_stats(
        self, last_updated: str | None, object_count: int, is_fresh: bool, release_name: str | None
    ) -> str:
        """Format cache statistics as JSON.

        Args:
            last_updated: Last update timestamp
            object_count: Number of cached objects
            is_fresh: Whether cache is fresh
            release_name: Release version name

        Returns:
            JSON-formatted string with cache statistics
        """
        data: dict[str, Any] = {"object_count": object_count, "is_fresh": is_fresh}

        if last_updated:
            data["last_updated"] = last_updated

        if release_name:
            data["release_name"] = release_name

        return json.dumps(data, indent=2, ensure_ascii=False)

    # Private helper methods

    def _catalog_object_to_dict(self, obj: CatalogObject) -> dict[str, Any]:
        """Convert CatalogObject to dictionary.

        Args:
            obj: Catalog object to convert

        Returns:
            Dictionary representation of the object
        """
        return {
            "id": obj.id,
            "name": obj.name,
            "domain": obj.domain,
            "description": obj.description,
            "image_id": obj.image_id,
            "property_sets": [self._property_set_to_dict(ps) for ps in obj.property_sets],
            "relationships": obj.relationships,
            "classifications": obj.classifications,
            "metadata": obj.metadata,
        }

    def _property_set_to_dict(self, pset: PropertySet) -> dict[str, Any]:
        """Convert PropertySet to dictionary.

        Args:
            pset: Property set to convert

        Returns:
            Dictionary representation of the property set
        """
        return {
            "id": pset.id,
            "name": pset.name,
            "description": pset.description,
            "properties": [self._property_to_dict(prop) for prop in pset.properties],
            "metadata": pset.metadata,
        }

    def _property_to_dict(self, prop: Property) -> dict[str, Any]:
        """Convert Property to dictionary.

        Args:
            prop: Property to convert

        Returns:
            Dictionary representation of the property
        """
        return {
            "id": prop.id,
            "name": prop.name,
            "value": prop.value,
            "unit": prop.unit,
            "description": prop.description,
            "data_type": prop.data_type,
            "metadata": prop.metadata,
        }

    def _property_match_to_dict(self, match: PropertyMatch) -> dict[str, Any]:
        """Convert PropertyMatch to dictionary.

        Args:
            match: Property match to convert

        Returns:
            Dictionary representation of the match
        """
        return {
            "property": self._property_to_dict(match.property),
            "object_id": match.object_id,
            "object_name": match.object_name,
            "property_set_name": match.property_set_name,
        }

    def _search_match_to_dict(self, match: SearchMatch) -> dict[str, Any]:
        """Convert SearchMatch to dictionary.

        Args:
            match: Search match to convert

        Returns:
            Dictionary representation of the match
        """
        return {
            "object_id": match.object_id,
            "object_name": match.object_name,
            "domain": match.domain,
            "field": match.field,
            "match_path": match.match_path,
            "matched_value": match.matched_value,
            "property_set_name": match.property_set_name,
        }

    def format_cache_coverage(self, stats: CacheCoverageStats) -> str:
        """Format cache coverage statistics as JSON.

        Args:
            stats: Cache coverage statistics

        Returns:
            JSON-formatted string with coverage analysis
        """
        result = {
            "total_objects": stats.total_objects,
            "cached_with_details": stats.cached_with_details,
            "cached_summary_only": stats.cached_summary_only,
            "not_cached": stats.not_cached,
            "coverage_percentage": stats.coverage_percentage,
            "estimated_download_time_seconds": stats.estimated_download_time_seconds,
            "missing_count": stats.cached_summary_only + stats.not_cached,
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    def format_grouped_objects(self, result: GroupedObjects) -> str:
        """Format grouped/sorted objects as JSON.

        Args:
            result: GroupedObjects with groups and counts

        Returns:
            JSON-formatted string
        """
        # Convert CatalogObject instances to dicts
        groups_dict = self._groups_to_dict(result.groups)

        output = {"total_objects": result.total_objects, "groups": groups_dict, "group_counts": result.group_counts}

        return json.dumps(output, indent=2, ensure_ascii=False)

    def _groups_to_dict(self, groups: dict[str, Any]) -> dict[str, Any]:
        """Convert groups with CatalogObject to dict representation.

        Args:
            groups: Groups (can contain CatalogObject instances)

        Returns:
            Dict with serialized objects
        """
        result = {}
        for key, value in groups.items():
            if isinstance(value, list):
                # List of objects
                result[key] = [{"id": obj.id, "name": obj.name, "domain": obj.domain} for obj in value]
            elif isinstance(value, dict):
                # Nested groups
                result[key] = self._groups_to_dict(value)
            else:
                result[key] = value

        return result
