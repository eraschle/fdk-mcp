"""Tests for presenters (Markdown and JSON)."""

import json

import pytest

from fdk_mcp.adapters.presenters import JsonPresenter, MarkdownPresenter
from fdk_mcp.domain.entities import CatalogObject, Property
from fdk_mcp.use_cases import PropertyMatch


@pytest.mark.unit
def test_markdown_presenter_object_list(sample_catalog_object: CatalogObject) -> None:
    """Test markdown presenter formats object list."""
    presenter = MarkdownPresenter()

    result = presenter.format_object_list([sample_catalog_object], total=1)

    assert "# FDK Objects (1 total)" in result
    assert "Test Bridge" in result
    assert "TEST_1" in result
    assert "Bridges" in result


@pytest.mark.unit
def test_markdown_presenter_object_list_multiple() -> None:
    """Test markdown presenter formats multiple objects."""
    obj1 = CatalogObject(id="OBJ_1", name="Object 1", domain="Domain A")
    obj2 = CatalogObject(id="OBJ_2", name="Object 2", domain="Domain B")

    presenter = MarkdownPresenter()
    result = presenter.format_object_list([obj1, obj2], total=2)

    assert "# FDK Objects (2 total)" in result
    assert "Object 1" in result
    assert "Object 2" in result


@pytest.mark.unit
def test_markdown_presenter_object_list_with_offset() -> None:
    """Test markdown presenter formats object list with pagination."""
    obj = CatalogObject(id="OBJ_1", name="Object 1", domain="Domain A")

    presenter = MarkdownPresenter()
    result = presenter.format_object_list([obj], total=10, offset=5)

    assert "Showing items 6-6 of 10" in result


@pytest.mark.unit
def test_markdown_presenter_object_detail(sample_catalog_object: CatalogObject) -> None:
    """Test markdown presenter formats object detail."""
    presenter = MarkdownPresenter()

    result = presenter.format_object_detail(sample_catalog_object)

    assert "# Test Bridge" in result
    assert "**ID**: TEST_1" in result
    assert "**Domain**: Bridges" in result
    assert "Standard bridge type A" in result


@pytest.mark.unit
def test_markdown_presenter_object_detail_from_cache(sample_catalog_object: CatalogObject) -> None:
    """Test markdown presenter indicates cache source."""
    presenter = MarkdownPresenter()

    result = presenter.format_object_detail(sample_catalog_object, from_cache=True)

    assert "cache" in result.lower()


@pytest.mark.unit
def test_markdown_presenter_object_with_property_sets(sample_catalog_object: CatalogObject) -> None:
    """Test markdown presenter formats object with property sets."""
    presenter = MarkdownPresenter()

    result = presenter.format_object_detail(sample_catalog_object)

    assert "Property Sets" in result
    assert "Dimensions" in result
    assert "Width" in result


@pytest.mark.unit
def test_markdown_presenter_domains_summary() -> None:
    """Test markdown presenter formats domains summary."""
    domains = {"Bridges": 10, "Tunnels": 5, "Tracks": 3}

    presenter = MarkdownPresenter()
    result = presenter.format_domains_summary(domains, total_domains=3, total_objects=18)

    assert "# FDK Domains Summary" in result
    assert "Total Domains" in result
    assert "Total Objects" in result
    assert "Bridges" in result
    assert "10 objects" in result


@pytest.mark.unit
def test_markdown_presenter_property_matches() -> None:
    """Test markdown presenter formats property search matches."""
    prop = Property(id="P1", name="Width", value="10", unit="m")
    match = PropertyMatch(property=prop, object_id="OBJ_1", object_name="Test Object", property_set_name="Dimensions")

    presenter = MarkdownPresenter()
    result = presenter.format_property_matches([match], total=1)

    assert "# Property Search Results (1 matches)" in result
    assert "Width" in result
    assert "Test Object" in result
    assert "Dimensions" in result


@pytest.mark.unit
def test_markdown_presenter_download_stats() -> None:
    """Test markdown presenter formats download statistics."""
    presenter = MarkdownPresenter()

    result = presenter.format_download_stats(total=100, downloaded=80, cached=15, failed=5, duration=45.5)

    assert "# Download Summary" in result
    assert "Total Objects" in result
    assert "100" in result
    assert "80" in result
    assert "45.5" in result or "45.50" in result


@pytest.mark.unit
def test_markdown_presenter_cache_stats() -> None:
    """Test markdown presenter formats cache statistics."""
    presenter = MarkdownPresenter()

    result = presenter.format_cache_stats(
        last_updated="2024-01-15T10:00:00", object_count=100, is_fresh=True, release_name="v2024.1"
    )

    assert "# Cache Statistics" in result
    assert "100" in result
    assert "Fresh" in result or "✓" in result
    assert "v2024.1" in result


# ============================================================================
# JSON Presenter Tests
# ============================================================================


@pytest.mark.unit
def test_json_presenter_object_list(sample_catalog_object: CatalogObject) -> None:
    """Test JSON presenter formats object list."""
    presenter = JsonPresenter()

    result = presenter.format_object_list([sample_catalog_object], total=1, offset=0)

    data = json.loads(result)
    assert data["total"] == 1
    assert data["count"] == 1
    assert data["offset"] == 0
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == "TEST_1"
    assert data["data"][0]["name"] == "Test Bridge"


@pytest.mark.unit
def test_json_presenter_object_detail(sample_catalog_object: CatalogObject) -> None:
    """Test JSON presenter formats object detail."""
    presenter = JsonPresenter()

    result = presenter.format_object(sample_catalog_object, from_cache=False)

    data = json.loads(result)
    assert data["id"] == "TEST_1"
    assert data["name"] == "Test Bridge"
    assert data["domain"] == "Bridges"
    assert "_from_cache" not in data  # Not included when False


@pytest.mark.unit
def test_json_presenter_object_detail_from_cache(sample_catalog_object: CatalogObject) -> None:
    """Test JSON presenter indicates cache source."""
    presenter = JsonPresenter()

    result = presenter.format_object(sample_catalog_object, from_cache=True)

    data = json.loads(result)
    assert data["_from_cache"] is True


@pytest.mark.unit
def test_json_presenter_object_with_property_sets(sample_catalog_object: CatalogObject) -> None:
    """Test JSON presenter includes property sets."""
    presenter = JsonPresenter()

    result = presenter.format_object(sample_catalog_object)

    data = json.loads(result)
    assert "property_sets" in data
    assert len(data["property_sets"]) > 0
    assert data["property_sets"][0]["name"] == "Dimensions"


@pytest.mark.unit
def test_json_presenter_domains_summary() -> None:
    """Test JSON presenter formats domains summary."""
    domains = {"Bridges": 10, "Tunnels": 5}

    presenter = JsonPresenter()
    result = presenter.format_domains_summary(domains, total_domains=2, total_objects=15)

    data = json.loads(result)
    assert data["total_domains"] == 2
    assert data["total_objects"] == 15
    assert data["domains"]["Bridges"] == 10
    assert data["domains"]["Tunnels"] == 5


@pytest.mark.unit
def test_json_presenter_property_matches() -> None:
    """Test JSON presenter formats property matches."""
    prop = Property(id="P1", name="Width", value="10", unit="m")
    match = PropertyMatch(property=prop, object_id="OBJ_1", object_name="Test Object", property_set_name="Dimensions")

    presenter = JsonPresenter()
    result = presenter.format_property_matches([match], total=1)

    data = json.loads(result)
    assert data["total"] == 1
    assert data["count"] == 1
    assert len(data["data"]) == 1
    assert data["data"][0]["property"]["name"] == "Width"
    assert data["data"][0]["object_name"] == "Test Object"


@pytest.mark.unit
def test_json_presenter_valid_json_structure(sample_catalog_object: CatalogObject) -> None:
    """Test that JSON presenter always produces valid JSON."""
    presenter = JsonPresenter()

    # Test all format methods produce valid JSON
    results = [
        presenter.format_object_list([sample_catalog_object], total=1, offset=0),
        presenter.format_object(sample_catalog_object),
        presenter.format_domains_summary({"Test": 1}, total_domains=1, total_objects=1),
    ]

    for result in results:
        # Should not raise JSONDecodeError
        data = json.loads(result)
        assert isinstance(data, dict)
