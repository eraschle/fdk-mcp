"""Markdown presenter for formatting domain entities as Markdown."""

from typing import Any

from ...domain.entities import CatalogObject, Property, PropertySet
from ...domain.repositories import CacheCoverageStats
from ...use_cases import GroupedObjects, PropertyMatch, SearchMatch


class MarkdownPresenter:
    """Format domain objects as Markdown for MCP responses.

    This presenter converts domain entities (CatalogObject, PropertySet, etc.)
    into human-readable Markdown format suitable for display in MCP clients.

    Examples:
        >>> presenter = MarkdownPresenter()
        >>> markdown = presenter.format_object_list(objects, total=100)
        >>> print(markdown)
        # FDK Objects (100 total)
        - **Object 1** (OBJ_1) - Domain A
        - **Object 2** (OBJ_2) - Domain B
    """

    def format_object_list(self, objects: list[CatalogObject], total: int, offset: int = 0) -> str:
        """Format list of objects as Markdown.

        Args:
            objects: List of catalog objects to format
            total: Total number of matching objects (before pagination)
            offset: Pagination offset

        Returns:
            Markdown-formatted string with object list
        """
        lines = [f"# FDK Objects ({total} total)\n"]

        if offset > 0:
            lines.append(f"*Showing items {offset + 1}-{offset + len(objects)} of {total}*\n")

        for obj in objects:
            lines.append(f"- **{obj.name}** ({obj.id}) - {obj.domain}")

        return "\n".join(lines)

    def format_object_list_detailed(self, objects: list[CatalogObject], total: int, offset: int = 0) -> str:
        """Format list of objects as detailed Markdown.

        Args:
            objects: List of catalog objects to format
            total: Total number of matching objects
            offset: Pagination offset

        Returns:
            Markdown-formatted string with detailed object information
        """
        lines = [f"# FDK Objects ({total} total)\n"]

        if offset > 0:
            lines.append(f"*Showing items {offset + 1}-{offset + len(objects)} of {total}*\n")

        for obj in objects:
            lines.append(f"## {obj.name} ({obj.id})")
            lines.append(f"- **Domain**: {obj.domain}")

            if obj.description:
                desc_preview = obj.description[:200] + "..." if len(obj.description) > 200 else obj.description
                lines.append(f"- **Description**: {desc_preview}")

            if obj.property_sets:
                pset_names = [ps.name for ps in obj.property_sets[:3]]
                lines.append(f"- **Property Sets**: {', '.join(pset_names)}")
                if len(obj.property_sets) > 3:
                    lines.append(f"  *(and {len(obj.property_sets) - 3} more)*")

            lines.append("")

        return "\n".join(lines)

    def format_object_detail(self, obj: CatalogObject, from_cache: bool = False) -> str:
        """Format single object with full details as Markdown.

        Args:
            obj: Catalog object to format
            from_cache: Whether object was loaded from cache

        Returns:
            Markdown-formatted string with complete object details
        """
        lines = [f"# {obj.name}"]
        lines.append(f"**ID**: {obj.id}")
        lines.append(f"**Domain**: {obj.domain}")

        if from_cache:
            lines.append("*📦 Loaded from cache*")

        lines.append("")

        if obj.description:
            lines.append(f"## Description\n{obj.description}\n")

        if obj.image_id:
            lines.append(f"**Image ID**: {obj.image_id}\n")

        if obj.classifications:
            lines.append("## Classifications")
            for classification in obj.classifications:
                lines.append(f"- {classification}")
            lines.append("")

        if obj.property_sets:
            lines.append(f"## Property Sets ({len(obj.property_sets)})\n")
            for pset in obj.property_sets:
                lines.extend(self._format_property_set(pset))

        if obj.relationships:
            lines.append("## Relationships")
            for rel_type, rel_data in obj.relationships.items():
                lines.append(f"### {rel_type}")
                if isinstance(rel_data, list):
                    for item in rel_data:
                        lines.append(f"- {item}")
                else:
                    lines.append(f"- {rel_data}")
            lines.append("")

        return "\n".join(lines)

    def _format_property_set(self, pset: PropertySet) -> list[str]:
        """Format a property set as Markdown lines.

        Args:
            pset: Property set to format

        Returns:
            List of markdown lines
        """
        lines = [f"### {pset.name}"]

        if pset.description:
            lines.append(f"*{pset.description}*")

        lines.append(f"\n**Properties** ({len(pset.properties)}):")

        for prop in pset.properties:
            lines.extend(self._format_property(prop))

        lines.append("")
        return lines

    def _format_property(self, prop: Property) -> list[str]:
        """Format a single property as Markdown lines.

        Args:
            prop: Property to format

        Returns:
            List of markdown lines
        """
        lines = [f"- **{prop.name}**"]

        if prop.value:
            unit_str = f" {prop.unit}" if prop.unit else ""
            lines.append(f"  - Value: {prop.value}{unit_str}")

        if prop.data_type:
            lines.append(f"  - Type: {prop.data_type}")

        if prop.description:
            desc_preview = prop.description[:150] + "..." if len(prop.description) > 150 else prop.description
            lines.append(f"  - Description: {desc_preview}")

        return lines

    def format_property_matches(self, matches: list[PropertyMatch], total: int) -> str:
        """Format property search matches as Markdown.

        Args:
            matches: List of property matches
            total: Total number of matches

        Returns:
            Markdown-formatted string with property matches
        """
        lines = [f"# Property Search Results ({total} matches)\n"]

        for match in matches:
            lines.append(f"## {match.property.name}")
            lines.append(f"- **Object**: {match.object_name} ({match.object_id})")
            lines.append(f"- **Property Set**: {match.property_set_name}")

            if match.property.value:
                unit_str = f" {match.property.unit}" if match.property.unit else ""
                lines.append(f"- **Value**: {match.property.value}{unit_str}")

            if match.property.description:
                desc_preview = (
                    match.property.description[:200] + "..."
                    if len(match.property.description) > 200
                    else match.property.description
                )
                lines.append(f"- **Description**: {desc_preview}")

            lines.append("")

        return "\n".join(lines)

    def format_domains_summary(self, domains: dict[str, int], total_domains: int, total_objects: int) -> str:
        """Format domains summary as Markdown.

        Args:
            domains: Dict mapping domain name to object count
            total_domains: Total number of unique domains
            total_objects: Total number of objects across all domains

        Returns:
            Markdown-formatted string with domains summary
        """
        lines = ["# FDK Domains Summary"]
        lines.append(f"\n**Total Domains**: {total_domains}")
        lines.append(f"**Total Objects**: {total_objects}\n")
        lines.append("## Objects by Domain\n")

        # Sort domains by object count (descending)
        sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)

        for domain_name, count in sorted_domains:
            percentage = (count / total_objects * 100) if total_objects > 0 else 0
            lines.append(f"- **{domain_name}**: {count} objects ({percentage:.1f}%)")

        return "\n".join(lines)

    def format_search_matches(self, matches: list[SearchMatch], total: int) -> str:
        """Format advanced search matches as Markdown.

        Args:
            matches: List of search matches
            total: Total number of matches

        Returns:
            Markdown-formatted string with search results
        """
        lines = [f"# Advanced Search Results ({total} matches)\n"]

        for match in matches:
            lines.append(f"## {match.object_name} ({match.object_id})")
            lines.append(f"- **Domain**: {match.domain}")
            lines.append(f"- **Match Field**: `{match.field}`")

            if match.match_path:
                lines.append(f"- **Match Path**: {match.match_path}")

            if match.property_set_name:
                lines.append(f"- **Property Set**: {match.property_set_name}")

            if match.matched_value:
                value_preview = (
                    str(match.matched_value)[:200] + "..."
                    if len(str(match.matched_value)) > 200
                    else str(match.matched_value)
                )
                lines.append(f"- **Matched Value**: {value_preview}")

            lines.append("")

        return "\n".join(lines)

    def format_download_stats(self, total: int, downloaded: int, cached: int, failed: int, duration: float) -> str:
        """Format download statistics as Markdown.

        Args:
            total: Total number of objects
            downloaded: Number of objects downloaded
            cached: Number of objects already cached
            failed: Number of failed downloads
            duration: Duration in seconds

        Returns:
            Markdown-formatted string with download statistics
        """
        lines = ["# Download Summary\n"]
        lines.append(f"- **Total Objects**: {total}")
        lines.append(f"- **Downloaded**: {downloaded}")
        lines.append(f"- **Already Cached**: {cached}")
        lines.append(f"- **Failed**: {failed}")
        lines.append(f"- **Duration**: {duration:.2f} seconds")

        if total > 0:
            success_rate = ((downloaded + cached) / total) * 100
            lines.append(f"- **Success Rate**: {success_rate:.1f}%")

        return "\n".join(lines)

    def format_cache_stats(
        self, last_updated: str | None, object_count: int, is_fresh: bool, release_name: str | None
    ) -> str:
        """Format cache statistics as Markdown.

        Args:
            last_updated: Last update timestamp
            object_count: Number of cached objects
            is_fresh: Whether cache is fresh
            release_name: Release version name

        Returns:
            Markdown-formatted string with cache statistics
        """
        lines = ["# Cache Statistics\n"]
        lines.append(f"- **Object Count**: {object_count}")
        lines.append(f"- **Status**: {'✓ Fresh' if is_fresh else '✗ Stale'}")

        if last_updated:
            lines.append(f"- **Last Updated**: {last_updated}")

        if release_name:
            lines.append(f"- **Release**: {release_name}")

        return "\n".join(lines)

    def format_cache_coverage(self, stats: CacheCoverageStats) -> str:
        """Format cache coverage statistics as Markdown.

        Args:
            stats: Cache coverage statistics

        Returns:
            Markdown-formatted string with coverage analysis
        """
        result = "# 📊 Cache Coverage Analysis\n\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        result += f"**Total Objects**: {stats.total_objects}\n\n"

        # Visual progress bar
        pct_details = int((stats.cached_with_details / stats.total_objects) * 20) if stats.total_objects > 0 else 0
        pct_summary = int((stats.cached_summary_only / stats.total_objects) * 20) if stats.total_objects > 0 else 0
        pct_missing = 20 - pct_details - pct_summary

        bar = "█" * pct_details + "▓" * pct_summary + "░" * pct_missing
        result += f"`{bar}` {stats.coverage_percentage}%\n\n"

        # Breakdown
        details_pct = (stats.cached_with_details / stats.total_objects * 100) if stats.total_objects > 0 else 0
        summary_pct = (stats.cached_summary_only / stats.total_objects * 100) if stats.total_objects > 0 else 0
        missing_pct = (stats.not_cached / stats.total_objects * 100) if stats.total_objects > 0 else 0

        result += f"✓ **Cached with details**: {stats.cached_with_details} ({details_pct:.1f}%)\n"
        result += f"⚠ **Cached (summary only)**: {stats.cached_summary_only} ({summary_pct:.1f}%)\n"
        result += f"✗ **Not cached**: {stats.not_cached} ({missing_pct:.1f}%)\n\n"

        # Download estimate
        missing_total = stats.cached_summary_only + stats.not_cached
        if missing_total > 0 and stats.estimated_download_time_seconds:
            result += "## ⚡ Download Required\n\n"
            result += f"- **Objects to download**: {missing_total}\n"
            result += f"- **Estimated time**: ~{stats.estimated_download_time_seconds} seconds\n"
            result += "- **Concurrency**: 20 parallel connections\n\n"

            # Recommendation
            result += "💡 **Recommendation**:\n"
            if missing_total > 500:
                result += "- Run `update_cache()` first to download all missing objects\n"
                result += "- Then searches will be instant!\n"
            elif missing_total > 100:
                result += '- Consider running `update_cache(domain_filter="...")` for specific domains\n'
            else:
                result += "- Download time is acceptable, you can proceed with searches\n"
        else:
            result += "## ✅ All objects cached with full details!\n\n"
            result += "Cache is complete. All searches will be instant.\n"

        return result

    def format_grouped_objects(self, result: GroupedObjects) -> str:
        """Format grouped/sorted objects as Markdown.

        Args:
            result: GroupedObjects with groups and counts

        Returns:
            Markdown-formatted string with grouped objects
        """
        output = "# 📊 Grouped Objects\n\n"
        output += f"**Total Objects**: {result.total_objects}\n\n"

        # Format groups
        output += self._format_groups_recursive(result.groups, level=0, counts=result.group_counts)

        return output

    def _format_groups_recursive(
        self, groups: dict[str, Any], level: int = 0, counts: dict[str, int] | None = None
    ) -> str:
        """Recursively format groups as Markdown tree.

        Args:
            groups: Group dictionary (can be nested)
            level: Current nesting level
            counts: Optional counts dictionary

        Returns:
            Formatted string
        """
        output = ""
        indent = "  " * level

        for group_name, group_content in groups.items():
            # Get count for this group
            count_str = ""
            if counts:
                # Try to find count for this group
                for key, count in counts.items():
                    if key.endswith(group_name) or key == group_name:
                        count_str = f" ({count})"
                        break

            if isinstance(group_content, list):
                # Leaf level: list objects
                output += f"{indent}## {group_name}{count_str}\n\n"
                for obj in group_content:
                    output += f"{indent}- **{obj.name}** (`{obj.id}`)\n"
                output += "\n"

            elif isinstance(group_content, dict):
                # Nested level: show group and recurse
                output += f"{indent}## {group_name}{count_str}\n\n"
                output += self._format_groups_recursive(group_content, level + 1, counts)

        return output
