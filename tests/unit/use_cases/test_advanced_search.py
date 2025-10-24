"""Tests for AdvancedSearchUseCase."""

from typing import TYPE_CHECKING

import pytest

from fdk_mcp.use_cases.advanced_search import AdvancedSearchRequest, AdvancedSearchUseCase


if TYPE_CHECKING:
    from conftest import FakeCacheRepository, FakeCatalogRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_advanced_search_in_name(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test advanced search in object names."""
    use_case = AdvancedSearchUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    request = AdvancedSearchRequest(search_fields=["name"], query="Bridge", language="en")
    response = await use_case.execute(request)

    assert response.total_matches > 0
    assert all("Bridge" in match.object_name for match in response.matches)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_advanced_search_no_results(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test advanced search with no results."""
    use_case = AdvancedSearchUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    request = AdvancedSearchRequest(search_fields=["name"], query="NonExistent", language="en")
    response = await use_case.execute(request)

    assert response.total_matches == 0
