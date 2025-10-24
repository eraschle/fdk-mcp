"""Tests for UpdateCacheUseCase."""

from typing import TYPE_CHECKING

import pytest

from fdk_mcp.use_cases.update_cache import UpdateCacheRequest, UpdateCacheUseCase


if TYPE_CHECKING:
    from conftest import FakeCacheRepository, FakeCatalogRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_cache(
    fake_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test updating cache."""
    use_case = UpdateCacheUseCase(catalog_repo=fake_catalog_repository, cache_repo=fake_cache_repository)

    request = UpdateCacheRequest(language="en")
    response = await use_case.execute(request)

    assert response.stats.downloaded > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_cache_no_cache_repo(fake_catalog_repository: "FakeCatalogRepository") -> None:
    """Test update cache without cache repository."""
    use_case = UpdateCacheUseCase(catalog_repo=fake_catalog_repository, cache_repo=None)

    request = UpdateCacheRequest(language="en")
    response = await use_case.execute(request)

    # Should still succeed but indicate no cache
    assert response.stats.downloaded == 0
