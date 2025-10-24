"""Tests for ListObjectsUseCase."""

from typing import TYPE_CHECKING

import pytest

from fdk_mcp.use_cases.list_objects import ListObjectsRequest, ListObjectsUseCase


if TYPE_CHECKING:
    from conftest import FakeCacheRepository, FakeCatalogRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_no_filter(
    fake_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test listing objects without any filters."""
    use_case = ListObjectsUseCase(catalog_repo=fake_catalog_repository, cache_repo=fake_cache_repository)

    request = ListObjectsRequest(language="en", limit=10)
    response = await use_case.execute(request)

    assert response.total == 1
    assert len(response.objects) == 1
    assert response.objects[0].name == "Test Bridge"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_with_domain_filter(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test listing objects with domain filter."""
    use_case = ListObjectsUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    request = ListObjectsRequest(domain_filter="Bridges", language="en", limit=10)
    response = await use_case.execute(request)

    assert response.total == 2
    assert len(response.objects) == 2
    assert all(obj.domain == "Bridges" for obj in response.objects)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_with_search_query(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test listing objects with search query."""
    use_case = ListObjectsUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    request = ListObjectsRequest(search_query="Bridge A", language="en", limit=10)
    response = await use_case.execute(request)

    assert response.total == 1
    assert len(response.objects) == 1
    assert response.objects[0].name == "Bridge A"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_case_insensitive_search(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test listing objects with case-insensitive search."""
    use_case = ListObjectsUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    request = ListObjectsRequest(search_query="bridge", language="en", limit=10)
    response = await use_case.execute(request)

    assert response.total == 2
    assert all("Bridge" in obj.name for obj in response.objects)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_pagination(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test listing objects with pagination."""
    use_case = ListObjectsUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    # Get first page (2 items)
    request1 = ListObjectsRequest(language="en", limit=2, offset=0)
    response1 = await use_case.execute(request1)

    assert response1.total == 4
    assert len(response1.objects) == 2

    # Get second page (2 items)
    request2 = ListObjectsRequest(language="en", limit=2, offset=2)
    response2 = await use_case.execute(request2)

    assert response2.total == 4
    assert len(response2.objects) == 2

    # Verify different objects
    assert response1.objects[0].id != response2.objects[0].id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_empty_result(
    empty_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test listing objects when catalog is empty."""
    use_case = ListObjectsUseCase(catalog_repo=empty_catalog_repository, cache_repo=fake_cache_repository)

    request = ListObjectsRequest(language="en", limit=10)
    response = await use_case.execute(request)

    assert response.total == 0
    assert len(response.objects) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_combined_filters(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test listing objects with both domain and search filters."""
    use_case = ListObjectsUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    request = ListObjectsRequest(domain_filter="Bridges", search_query="Bridge A", language="en", limit=10)
    response = await use_case.execute(request)

    assert response.total == 1
    assert response.objects[0].name == "Bridge A"
    assert response.objects[0].domain == "Bridges"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_no_cache(fake_catalog_repository: "FakeCatalogRepository") -> None:
    """Test listing objects without cache repository."""
    use_case = ListObjectsUseCase(catalog_repo=fake_catalog_repository, cache_repo=None)

    request = ListObjectsRequest(language="en", limit=10)
    response = await use_case.execute(request)

    assert response.total == 1
    assert len(response.objects) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_pagination_beyond_results(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test pagination beyond available results."""
    use_case = ListObjectsUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    # Request page beyond results
    request = ListObjectsRequest(language="en", limit=10, offset=100)
    response = await use_case.execute(request)

    assert response.total == 4
    assert len(response.objects) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_language_parameter(
    fake_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test that language parameter is passed to repository."""
    use_case = ListObjectsUseCase(catalog_repo=fake_catalog_repository, cache_repo=fake_cache_repository)

    request = ListObjectsRequest(language="de", limit=10)
    await use_case.execute(request)

    # Check that fetch was called with correct language
    assert len(fake_catalog_repository._fetch_calls) > 0
    assert fake_catalog_repository._fetch_calls[-1]["language"] == "de"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_objects_cache_freshness_check(
    fake_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test that cache freshness is checked when cache exists."""
    # Set cache as stale
    fake_cache_repository.set_fresh(False)

    use_case = ListObjectsUseCase(catalog_repo=fake_catalog_repository, cache_repo=fake_cache_repository)

    request = ListObjectsRequest(language="en", limit=10)
    await use_case.execute(request)

    # Verify cache was updated (object was saved)
    cached_objects = fake_cache_repository.list_cached_objects()
    assert len(cached_objects) > 0
