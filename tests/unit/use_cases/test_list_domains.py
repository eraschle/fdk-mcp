"""Tests for ListDomainsUseCase."""

from typing import TYPE_CHECKING

import pytest

from fdk_mcp.use_cases.list_domains import ListDomainsRequest, ListDomainsUseCase


if TYPE_CHECKING:
    from conftest import FakeCacheRepository, FakeCatalogRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_domains(
    multiple_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test listing domains."""
    use_case = ListDomainsUseCase(catalog_repo=multiple_objects_catalog, cache_repo=fake_cache_repository)

    request = ListDomainsRequest(language="en")
    response = await use_case.execute(request)

    assert response.total_domains == 3
    assert "Bridges" in response.domains
    assert "Tunnels" in response.domains
    assert "Tracks" in response.domains
    assert response.domains["Bridges"] == 2
    assert response.domains["Tunnels"] == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_domains_empty(
    empty_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test listing domains when catalog is empty."""
    use_case = ListDomainsUseCase(catalog_repo=empty_catalog_repository, cache_repo=fake_cache_repository)

    request = ListDomainsRequest(language="en")
    response = await use_case.execute(request)

    assert response.total_domains == 0
    assert len(response.domains) == 0
