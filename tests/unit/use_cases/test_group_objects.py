"""Tests for GroupObjectsUseCase."""

from typing import TYPE_CHECKING

import pytest

from fdk_mcp.domain.entities import CatalogObject, PropertySet
from fdk_mcp.use_cases.group_objects import (
    GroupObjectsRequest,
    GroupObjectsUseCase,
)


if TYPE_CHECKING:
    from conftest import FakeCacheRepository, FakeCatalogRepository


@pytest.fixture
def grouped_objects_catalog() -> "FakeCatalogRepository":
    """Catalog repository with diverse objects for grouping tests."""
    from conftest import FakeCatalogRepository

    objects = [
        CatalogObject(
            id="OBJ_BR_1",
            name="Bridge A",
            domain="Bridges",
            description="Bridge type A",
            classifications=["IfcBridge"],
            property_sets=[
                PropertySet(id="PSET_1", name="Pset_Common", properties=[]),
                PropertySet(id="PSET_2", name="Pset_Geometry", properties=[]),
            ],
        ),
        CatalogObject(
            id="OBJ_BR_2",
            name="Bridge B",
            domain="Bridges",
            description="Bridge type B",
            classifications=["IfcBridge"],
            property_sets=[
                PropertySet(id="PSET_1", name="Pset_Common", properties=[]),
            ],
        ),
        CatalogObject(
            id="OBJ_TUN_1",
            name="Tunnel A",
            domain="Tunnels",
            description="Tunnel type A",
            classifications=["IfcTunnel"],
            property_sets=[
                PropertySet(id="PSET_3", name="Pset_Tunnel", properties=[]),
            ],
        ),
        CatalogObject(
            id="OBJ_TRK_1",
            name="Track A",
            domain="Tracks",
            description="Track type A",
            classifications=["IfcRail"],
            property_sets=[
                PropertySet(id="PSET_1", name="Pset_Common", properties=[]),
                PropertySet(id="PSET_4", name="Pset_Rail", properties=[]),
            ],
        ),
    ]
    return FakeCatalogRepository(objects=objects)


# Test valid Literal values


@pytest.mark.unit
@pytest.mark.asyncio
async def test_group_by_domain_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test grouping by domain with valid Literal value."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by="domain",  # Valid Literal value
        language="en",
    )
    response = await use_case.execute(request)

    assert response.result.total_objects == 4
    assert "Bridges" in response.result.groups
    assert "Tunnels" in response.result.groups
    assert "Tracks" in response.result.groups
    assert len(response.result.groups["Bridges"]) == 2
    assert len(response.result.groups["Tunnels"]) == 1
    assert len(response.result.groups["Tracks"]) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_group_by_ifc_class_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test grouping by ifcClass with valid Literal value."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by="ifcClass",  # Valid Literal value
        language="en",
    )
    response = await use_case.execute(request)

    assert response.result.total_objects == 4
    assert "IfcBridge" in response.result.groups
    assert "IfcTunnel" in response.result.groups
    assert "IfcRail" in response.result.groups


@pytest.mark.unit
@pytest.mark.asyncio
async def test_group_by_property_set_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test grouping by propertySet with valid Literal value."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by="propertySet",  # Valid Literal value
        language="en",
    )
    response = await use_case.execute(request)

    # Note: Objects can appear in multiple groups when grouped by propertySet
    assert response.result.total_objects == 4
    assert "Pset_Common" in response.result.groups
    assert "Pset_Geometry" in response.result.groups
    assert "Pset_Tunnel" in response.result.groups
    assert "Pset_Rail" in response.result.groups


@pytest.mark.unit
@pytest.mark.asyncio
async def test_group_by_name_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test grouping by name with valid Literal value."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by="name",  # Valid Literal value
        language="en",
    )
    response = await use_case.execute(request)

    assert response.result.total_objects == 4
    assert "Bridge A" in response.result.groups
    assert "Bridge B" in response.result.groups
    assert "Tunnel A" in response.result.groups
    assert "Track A" in response.result.groups


# Test valid sort_by Literal values


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sort_by_name_asc_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test sorting by name ascending with valid Literal values."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by=None,
        sort_by="name",  # Valid Literal value
        order="asc",  # Valid Literal value
        language="en",
    )
    response = await use_case.execute(request)

    objects = response.result.groups["all"]
    assert len(objects) == 4
    assert objects[0].name == "Bridge A"
    assert objects[1].name == "Bridge B"
    assert objects[2].name == "Track A"
    assert objects[3].name == "Tunnel A"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sort_by_name_desc_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test sorting by name descending with valid Literal values."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by=None,
        sort_by="name",  # Valid Literal value
        order="desc",  # Valid Literal value
        language="en",
    )
    response = await use_case.execute(request)

    objects = response.result.groups["all"]
    assert len(objects) == 4
    assert objects[0].name == "Tunnel A"
    assert objects[1].name == "Track A"
    assert objects[2].name == "Bridge B"
    assert objects[3].name == "Bridge A"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sort_by_id_asc_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test sorting by id ascending with valid Literal values."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by=None,
        sort_by="id",  # Valid Literal value
        order="asc",  # Valid Literal value
        language="en",
    )
    response = await use_case.execute(request)

    objects = response.result.groups["all"]
    assert len(objects) == 4
    assert objects[0].id == "OBJ_BR_1"
    assert objects[1].id == "OBJ_BR_2"
    assert objects[2].id == "OBJ_TRK_1"
    assert objects[3].id == "OBJ_TUN_1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sort_by_domain_asc_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test sorting by domain ascending with valid Literal values."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by=None,
        sort_by="domain",  # Valid Literal value
        order="asc",  # Valid Literal value
        language="en",
    )
    response = await use_case.execute(request)

    objects = response.result.groups["all"]
    assert len(objects) == 4
    assert objects[0].domain == "Bridges"
    assert objects[1].domain == "Bridges"
    assert objects[2].domain == "Tracks"
    assert objects[3].domain == "Tunnels"


# Test multi-level grouping with valid values


@pytest.mark.unit
@pytest.mark.asyncio
async def test_multi_level_grouping_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test multi-level grouping with valid Literal values."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by=["domain", "ifcClass"],  # Valid Literal values
        language="en",
    )
    response = await use_case.execute(request)

    assert response.result.total_objects == 4
    assert "Bridges" in response.result.groups
    assert "IfcBridge" in response.result.groups["Bridges"]
    assert len(response.result.groups["Bridges"]["IfcBridge"]) == 2


# Test grouping with sorting


@pytest.mark.unit
@pytest.mark.asyncio
async def test_grouping_with_sorting_valid(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test grouping with sorting using valid Literal values."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by="domain",  # Valid Literal value
        sort_by="name",  # Valid Literal value
        order="asc",  # Valid Literal value
        language="en",
    )
    response = await use_case.execute(request)

    bridges = response.result.groups["Bridges"]
    assert len(bridges) == 2
    assert bridges[0].name == "Bridge A"
    assert bridges[1].name == "Bridge B"


# Test include_count parameter


@pytest.mark.unit
@pytest.mark.asyncio
async def test_include_count_true(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test grouping with include_count=True."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by="domain",
        include_count=True,
        language="en",
    )
    response = await use_case.execute(request)

    assert response.result.group_counts is not None
    assert response.result.group_counts["Bridges"] == 2
    assert response.result.group_counts["Tunnels"] == 1
    assert response.result.group_counts["Tracks"] == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_include_count_false(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test grouping with include_count=False."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by="domain",
        include_count=False,
        language="en",
    )
    response = await use_case.execute(request)

    assert response.result.group_counts is None


# Test edge cases


@pytest.mark.unit
@pytest.mark.asyncio
async def test_no_grouping_no_sorting(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test with no grouping and no sorting."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1", "OBJ_BR_2", "OBJ_TUN_1", "OBJ_TRK_1"],
        group_by=None,
        sort_by=None,
        language="en",
    )
    response = await use_case.execute(request)

    assert response.result.total_objects == 4
    assert "all" in response.result.groups
    assert len(response.result.groups["all"]) == 4


@pytest.mark.unit
@pytest.mark.asyncio
async def test_single_object(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test grouping with a single object."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1"],
        group_by="domain",
        language="en",
    )
    response = await use_case.execute(request)

    assert response.result.total_objects == 1
    assert "Bridges" in response.result.groups
    assert len(response.result.groups["Bridges"]) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_from_cache(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test that objects are fetched from cache when available."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    # Pre-populate cache
    obj = CatalogObject(
        id="OBJ_BR_1",
        name="Bridge A",
        domain="Bridges",
        description="Bridge type A",
    )
    fake_cache_repository.save_object("OBJ_BR_1", obj)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1"],
        group_by="domain",
        language="en",
    )
    response = await use_case.execute(request)

    # Should get from cache, not API
    assert response.result.total_objects == 1
    assert len(grouped_objects_catalog._fetch_calls) == 0  # No API calls


@pytest.mark.unit
@pytest.mark.asyncio
async def test_language_parameter(
    grouped_objects_catalog: "FakeCatalogRepository", fake_cache_repository: "FakeCacheRepository"
) -> None:
    """Test that language parameter is passed correctly."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1"],
        group_by="domain",
        language="de",  # Valid LanguageCode
    )
    await use_case.execute(request)

    # Check that fetch was called with correct language
    assert len(grouped_objects_catalog._fetch_calls) > 0
    assert grouped_objects_catalog._fetch_calls[0]["language"] == "de"


# Test all valid language codes


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("language", ["de", "fr", "it", "en"])
async def test_all_valid_language_codes(
    grouped_objects_catalog: "FakeCatalogRepository",
    fake_cache_repository: "FakeCacheRepository",
    language: str,
) -> None:
    """Test all valid LanguageCode literal values."""
    use_case = GroupObjectsUseCase(catalog_repo=grouped_objects_catalog, cache_repo=fake_cache_repository)

    request = GroupObjectsRequest(
        object_ids=["OBJ_BR_1"],
        group_by="domain",
        language=language,  # type: ignore
    )
    response = await use_case.execute(request)

    assert response.result.total_objects == 1
