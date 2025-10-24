"""Tests for DownloadCatalogUseCase."""

from typing import TYPE_CHECKING

import pytest

from fdk_mcp.use_cases.download_catalog import DownloadCatalogRequest, DownloadCatalogUseCase


if TYPE_CHECKING:
    from conftest import FakeCacheRepository, FakeCatalogRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_download_catalog(
    fake_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test downloading entire catalog."""
    use_case = DownloadCatalogUseCase(catalog_repo=fake_catalog_repository, cache_repo=fake_cache_repository)

    request = DownloadCatalogRequest(language="en")
    response = await use_case.execute(request)

    assert response.stats.total_objects > 0
    assert response.stats.downloaded > 0
    assert response.stats.failed == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_download_catalog_with_domain_filter(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test downloading catalog with domain filter."""
    use_case = DownloadCatalogUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    request = DownloadCatalogRequest(language="en", domain_filter="Bridges")
    response = await use_case.execute(request)

    assert response.stats.total_objects == 2
