"""Tests for SearchPropertiesUseCase."""

# Import used at runtime for creating test objects
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from fdk_mcp.domain.entities import CatalogObject, Property, PropertySet
from fdk_mcp.use_cases.search_properties import SearchPropertiesRequest, SearchPropertiesUseCase


sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import FakeCatalogRepository  # noqa: E402


if TYPE_CHECKING:
    from conftest import FakeCacheRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_properties_found(fake_cache_repository: "FakeCacheRepository") -> None:
    """Test searching properties returns matches."""
    # Create objects with searchable properties
    prop1 = Property(id="P1", name="Width", value="10", unit="m")
    prop2 = Property(id="P2", name="Height", value="20", unit="m")
    pset1 = PropertySet(id="PS1", name="Dimensions", properties=[prop1, prop2])

    obj = CatalogObject(id="OBJ_1", name="Test Object", domain="Test", property_sets=[pset1])

    catalog_repo = FakeCatalogRepository(objects=[obj])

    use_case = SearchPropertiesUseCase(catalog_repo=catalog_repo, cache_repo=fake_cache_repository)

    request = SearchPropertiesRequest(query="Width", language="en")
    response = await use_case.execute(request)

    assert response.total_matches > 0
    assert len(response.matches) > 0
    assert response.matches[0].property.name == "Width"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_properties_case_insensitive(fake_cache_repository: "FakeCacheRepository") -> None:
    """Test property search is case insensitive."""
    prop = Property(id="P1", name="Width", value="10")
    pset = PropertySet(id="PS1", name="Dimensions", properties=[prop])
    obj = CatalogObject(id="OBJ_1", name="Test", domain="Test", property_sets=[pset])

    catalog_repo = FakeCatalogRepository(objects=[obj])
    use_case = SearchPropertiesUseCase(catalog_repo=catalog_repo, cache_repo=fake_cache_repository)

    request = SearchPropertiesRequest(query="width", language="en")
    response = await use_case.execute(request)

    assert response.total_matches > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_properties_no_matches(
    empty_catalog_repository: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test searching properties with no matches."""
    use_case = SearchPropertiesUseCase(catalog_repo=empty_catalog_repository, cache_repo=fake_cache_repository)

    request = SearchPropertiesRequest(query="NonExistent", language="en")
    response = await use_case.execute(request)

    assert response.total_matches == 0
    assert len(response.matches) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_properties_pagination(fake_cache_repository: "FakeCacheRepository") -> None:
    """Test property search with pagination."""
    # Create multiple objects with properties
    objects = []
    for i in range(5):
        prop = Property(id=f"P{i}", name="Width", value=str(i))
        pset = PropertySet(id=f"PS{i}", name="Dimensions", properties=[prop])
        obj = CatalogObject(id=f"OBJ_{i}", name=f"Object {i}", domain="Test", property_sets=[pset])
        objects.append(obj)

    catalog_repo = FakeCatalogRepository(objects=objects)
    use_case = SearchPropertiesUseCase(catalog_repo=catalog_repo, cache_repo=fake_cache_repository)

    request = SearchPropertiesRequest(query="Width", language="en", limit=2)
    response = await use_case.execute(request)

    assert response.total_matches == 5
    assert len(response.matches) == 2
