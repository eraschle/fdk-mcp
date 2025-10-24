"""Data models for SBB FDK MCP server."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Type Definitions
LanguageCode = Literal["de", "fr", "it", "en"]
SortField = Literal["name", "id", "domain"]
SortOrder = Literal["asc", "desc"]
GroupField = Literal["domain", "ifcClass", "propertySet", "name"]

# Public API
__all__ = [
    # Type Definitions
    "LanguageCode",
    "SortField",
    "SortOrder",
    "GroupField",
    # Enums
    "ResponseFormat",
    "DetailLevel",
    # Input Models
    "ListObjectsInput",
    "GetObjectInput",
    "SearchPropertiesInput",
    "AdvancedSearchInput",
    "GetCacheCoverageInput",
    "GroupObjectsInput",
]


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


class DetailLevel(str, Enum):
    """Detail level for responses."""

    CONCISE = "concise"
    DETAILED = "detailed"


class MatchMode(str, Enum):
    """Match mode for search operations."""

    CONTAINS = "contains"
    EQUALS = "equals"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class ListObjectsInput(BaseModel):
    """Input model for listing FDK objects."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    domain: str | None = Field(
        default=None,
        description="Filter by domain (e.g., 'Brücken', 'Energie')",
        max_length=100,
    )
    search: str | None = Field(
        default=None,
        description="Search term for object names",
        min_length=1,
        max_length=200,
    )
    limit: int = Field(
        default=20,
        description="Max results (1-100)",
        ge=1,
        le=100,
    )
    offset: int = Field(
        default=0,
        description="Skip results for pagination",
        ge=0,
    )
    detail: DetailLevel = Field(
        default=DetailLevel.CONCISE,
        description="Response detail level",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format",
    )

    @field_validator("search")
    @classmethod
    def validate_search(cls, v: str | None) -> str | None:
        if v and not v.strip():
            raise ValueError("Search cannot be whitespace only")
        return v.strip() if v else None


class GetObjectInput(BaseModel):
    """Input model for getting an FDK object."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    object_id: str = Field(
        ...,
        description="Object ID (e.g., 'OBJ_BR_1')",
        min_length=1,
        max_length=50,
        pattern=r"^[A-Z0-9_]+$",
    )
    language: LanguageCode = Field(
        default="de",
        description="Language code",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format",
    )


class SearchPropertiesInput(BaseModel):
    """Input model for searching properties."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    query: str = Field(
        ...,
        description="Search term for property names",
        min_length=1,
        max_length=200,
    )
    limit: int = Field(
        default=20,
        description="Max results (1-100)",
        ge=1,
        le=100,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be whitespace")
        return v.strip()


class AdvancedSearchInput(BaseModel):
    """Input model for advanced search across any JSON field."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    search_fields: list[str] = Field(
        default=["all"],
        description=(
            "JSON fields to search in. Options: 'all', 'propertySets', 'properties', "
            "'ifcClassAssignments', 'ebkpConcepts', 'aksCode', 'componentRelationships', "
            "'assemblyRelationships', 'domainModel', 'nameObjectGroup', 'nameSubgroup'"
        ),
        min_length=1,
    )
    query: str = Field(
        ...,
        description="Search term to find in specified fields",
        min_length=1,
        max_length=200,
    )
    domain_filter: str | None = Field(
        default=None,
        description="Optional domain filter (e.g., 'Hochbau', 'Brücken')",
        max_length=100,
    )
    match_mode: MatchMode = Field(
        default=MatchMode.CONTAINS,
        description="How to match the query: contains, equals, starts_with, ends_with",
    )
    case_sensitive: bool = Field(
        default=False,
        description="Whether search should be case-sensitive",
    )
    limit: int = Field(
        default=50,
        description="Max results (1-200)",
        ge=1,
        le=200,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format",
    )

    @field_validator("query")
    @classmethod
    def validate_query_advanced(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be whitespace")
        return v.strip()

    @field_validator("search_fields")
    @classmethod
    def validate_search_fields(cls, v: list[str]) -> list[str]:
        valid_fields = {
            "all",
            "propertySets",
            "properties",
            "ifcClassAssignments",
            "ebkpConcepts",
            "aksCode",
            "componentRelationships",
            "assemblyRelationships",
            "domainModel",
            "nameObjectGroup",
            "nameSubgroup",
            "description",
            "name",
        }
        for field in v:
            if field not in valid_fields:
                raise ValueError(f"Invalid search_field: {field}. Must be one of: {', '.join(valid_fields)}")
        return v


class GetCacheCoverageInput(BaseModel):
    """Input model for cache coverage analysis."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    language: LanguageCode = Field(
        default="de",
        description="Language code (de/fr/it/en)",
    )
    domain_filter: str | None = Field(
        default=None,
        description="Analyze coverage for specific domain only",
        max_length=100,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format (markdown or json)",
    )


class GroupObjectsInput(BaseModel):
    """Input model for grouping and sorting objects."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    object_ids: list[str] = Field(description="List of object IDs to group/sort", min_length=1, max_length=500)
    group_by: GroupField | list[GroupField] | None = Field(
        default=None,
        description="Field(s) to group by: domain, ifcClass, propertySet, name. None = sort only.",
    )
    sort_by: SortField | None = Field(
        default=None,
        description="Field to sort by: name, id, domain. Sorts within groups if grouped.",
    )
    order: SortOrder = Field(
        default="asc",
        description="Sort order: asc or desc",
    )
    include_count: bool = Field(
        default=True,
        description="Include count of objects per group",
    )
    language: LanguageCode = Field(
        default="de",
        description="Language code (de/fr/it/en)",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format (markdown or json)",
    )

    @field_validator("group_by")
    @classmethod
    def validate_group_by(cls, v: GroupField | list[GroupField] | None) -> GroupField | list[GroupField] | None:
        """Validate group_by: reject empty lists for semantic clarity."""
        if isinstance(v, list) and len(v) == 0:
            raise ValueError("group_by list cannot be empty. Use None for sort-only mode.")
        return v
