"""Tests for GetObjectUseCase."""

from typing import TYPE_CHECKING

import pytest

from fdk_mcp.use_cases.get_object import GetObjectRequest, GetObjectUseCase


if TYPE_CHECKING:
    from conftest import FakeCacheRepository, FakeCatalogRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_object_found(
    fake_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test getting an object that exists."""
    use_case = GetObjectUseCase(catalog_repo=fake_catalog_repository, cache_repo=fake_cache_repository)

    request = GetObjectRequest(object_id="TEST_1", language="en")
    response = await use_case.execute(request)

    assert response.object is not None
    assert response.object.id == "TEST_1"
    assert response.object.name == "Test Bridge"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_object_not_found(
    empty_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test getting an object that doesn't exist."""
    use_case = GetObjectUseCase(catalog_repo=empty_catalog_repository, cache_repo=fake_cache_repository)

    request = GetObjectRequest(object_id="NONEXISTENT", language="en")
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute(request)

    assert "Object with ID 'NONEXISTENT' not found" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_object_from_cache(
    fake_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test getting object from cache when available."""
    # Pre-populate cache
    catalog_obj = fake_catalog_repository.objects[0]
    fake_cache_repository.save_object("TEST_1", catalog_obj)

    use_case = GetObjectUseCase(catalog_repo=fake_catalog_repository, cache_repo=fake_cache_repository)

    request = GetObjectRequest(object_id="TEST_1", language="en")
    response = await use_case.execute(request)

    assert response.object is not None
    assert response.from_cache is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_object_no_cache(fake_catalog_repository: "FakeCatalogRepository") -> None:
    """Test getting object without cache."""
    use_case = GetObjectUseCase(catalog_repo=fake_catalog_repository, cache_repo=None)

    request = GetObjectRequest(object_id="TEST_1", language="en")
    response = await use_case.execute(request)

    assert response.object is not None
    assert response.from_cache is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_object_saves_to_cache(
    fake_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test that fetched object is saved to cache."""
    use_case = GetObjectUseCase(catalog_repo=fake_catalog_repository, cache_repo=fake_cache_repository)

    request = GetObjectRequest(object_id="TEST_1", language="en")
    await use_case.execute(request)

    # Verify object was cached
    cached_obj = fake_cache_repository.get_cached_object("TEST_1")
    assert cached_obj is not None
    assert cached_obj.id == "TEST_1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_object_language_parameter(
    fake_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test that language parameter is passed to repository."""
    use_case = GetObjectUseCase(catalog_repo=fake_catalog_repository, cache_repo=fake_cache_repository)

    request = GetObjectRequest(object_id="TEST_1", language="de")
    await use_case.execute(request)

    # Check that fetch was called with correct language
    assert len(fake_catalog_repository._fetch_calls) > 0
    call = fake_catalog_repository._fetch_calls[-1]
    assert call["language"] == "de"
    assert call["object_id"] == "TEST_1"
