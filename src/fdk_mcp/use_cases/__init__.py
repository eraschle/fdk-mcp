"""Use Cases Layer - Application Business Logic.

This module contains all use cases (application controllers) following Clean Architecture.
Each use case:
- Orchestrates domain logic
- Depends on repository abstractions (not concrete implementations)
- Handles optional cache (CacheRepository | None)
- Works with domain entities (vendor-agnostic)
- Has Single Responsibility (one business operation)

Use Cases:
1. ListObjectsUseCase - List and filter catalog objects
2. GetObjectUseCase - Retrieve single object with caching
3. SearchPropertiesUseCase - Search properties across objects
4. ListDomainsUseCase - List available domains with counts
5. AdvancedSearchUseCase - Advanced multi-field search
6. DownloadCatalogUseCase - Bulk download all objects
7. UpdateCacheUseCase - Incremental cache updates
8. GetCacheCoverageUseCase - Analyze cache coverage and estimate download time
9. GroupObjectsUseCase - Group and sort objects by attributes
"""

# Use Case Classes
from .advanced_search import (
    AdvancedSearchRequest,
    AdvancedSearchResponse,
    AdvancedSearchUseCase,
    MatchMode,
    SearchMatch,
)
from .download_catalog import DownloadCatalogRequest, DownloadCatalogResponse, DownloadCatalogUseCase, DownloadStats
from .get_cache_coverage import GetCacheCoverageRequest, GetCacheCoverageResponse, GetCacheCoverageUseCase
from .get_object import GetObjectRequest, GetObjectResponse, GetObjectUseCase
from .group_objects import GroupedObjects, GroupObjectsRequest, GroupObjectsResponse, GroupObjectsUseCase
from .list_domains import ListDomainsRequest, ListDomainsResponse, ListDomainsUseCase
from .list_objects import ListObjectsRequest, ListObjectsResponse, ListObjectsUseCase
from .search_properties import PropertyMatch, SearchPropertiesRequest, SearchPropertiesResponse, SearchPropertiesUseCase
from .update_cache import UpdateCacheRequest, UpdateCacheResponse, UpdateCacheUseCase, UpdateStats


__all__ = [
    # List Objects
    "ListObjectsUseCase",
    "ListObjectsRequest",
    "ListObjectsResponse",
    # Get Object
    "GetObjectUseCase",
    "GetObjectRequest",
    "GetObjectResponse",
    # Search Properties
    "SearchPropertiesUseCase",
    "SearchPropertiesRequest",
    "SearchPropertiesResponse",
    "PropertyMatch",
    # List Domains
    "ListDomainsUseCase",
    "ListDomainsRequest",
    "ListDomainsResponse",
    # Advanced Search
    "AdvancedSearchUseCase",
    "AdvancedSearchRequest",
    "AdvancedSearchResponse",
    "SearchMatch",
    "MatchMode",
    # Download Catalog
    "DownloadCatalogUseCase",
    "DownloadCatalogRequest",
    "DownloadCatalogResponse",
    "DownloadStats",
    # Update Cache
    "UpdateCacheUseCase",
    "UpdateCacheRequest",
    "UpdateCacheResponse",
    "UpdateStats",
    # Get Cache Coverage
    "GetCacheCoverageUseCase",
    "GetCacheCoverageRequest",
    "GetCacheCoverageResponse",
    # Group Objects
    "GroupObjectsUseCase",
    "GroupObjectsRequest",
    "GroupObjectsResponse",
    "GroupedObjects",
]
