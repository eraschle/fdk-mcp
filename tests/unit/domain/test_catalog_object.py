"""Tests for CatalogObject domain entity."""

import pytest

from fdk_mcp.domain.entities import CatalogObject, Property, PropertySet


@pytest.mark.unit
def test_catalog_object_creation() -> None:
    """Test basic catalog object creation."""
    obj = CatalogObject(id="TEST_1", name="Test Object", domain="Test Domain")
    assert obj.id == "TEST_1"
    assert obj.name == "Test Object"
    assert obj.domain == "Test Domain"
    assert obj.description is None
    assert obj.property_sets == []
    assert obj.relationships == {}
    assert obj.classifications == []


@pytest.mark.unit
def test_catalog_object_with_optional_fields() -> None:
    """Test catalog object with all optional fields."""
    obj = CatalogObject(
        id="TEST_1",
        name="Test Object",
        domain="Test Domain",
        description="Test description",
        image_id="IMG_001",
        property_sets=[],
        relationships={"components": ["C1", "C2"]},
        classifications=["IfcBridge", "eBKP_123"],
        metadata={"custom_field": "value"},
    )
    assert obj.description == "Test description"
    assert obj.image_id == "IMG_001"
    assert obj.relationships == {"components": ["C1", "C2"]}
    assert obj.classifications == ["IfcBridge", "eBKP_123"]
    assert obj.metadata == {"custom_field": "value"}


@pytest.mark.unit
def test_get_property_set_found(sample_property_set: PropertySet) -> None:
    """Test get_property_set returns property set when found."""
    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[sample_property_set])
    result = obj.get_property_set("Dimensions")
    assert result is not None
    assert result.name == "Dimensions"


@pytest.mark.unit
def test_get_property_set_case_insensitive(sample_property_set: PropertySet) -> None:
    """Test get_property_set is case insensitive."""
    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[sample_property_set])
    result = obj.get_property_set("dimensions")
    assert result is not None
    assert result.name == "Dimensions"


@pytest.mark.unit
def test_get_property_set_not_found() -> None:
    """Test get_property_set returns None when not found."""
    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[])
    result = obj.get_property_set("NonExistent")
    assert result is None


@pytest.mark.unit
def test_get_property_found(sample_property_set: PropertySet) -> None:
    """Test get_property returns property value when found."""
    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[sample_property_set])
    result = obj.get_property("Width")
    assert result == "10.5"


@pytest.mark.unit
def test_get_property_with_pset_name(sample_property_set: PropertySet) -> None:
    """Test get_property with specific property set name."""
    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[sample_property_set])
    result = obj.get_property("Width", pset_name="Dimensions")
    assert result == "10.5"


@pytest.mark.unit
def test_get_property_not_found() -> None:
    """Test get_property returns None when not found."""
    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[])
    result = obj.get_property("NonExistent")
    assert result is None


@pytest.mark.unit
def test_get_property_wrong_pset() -> None:
    """Test get_property returns None when property set doesn't exist."""
    pset = PropertySet(id="PS_1", name="Dimensions", properties=[Property(id="P1", name="Width", value="10")])
    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[pset])
    result = obj.get_property("Width", pset_name="WrongSet")
    assert result is None


@pytest.mark.unit
def test_has_property_sets_true(sample_property_set: PropertySet) -> None:
    """Test has_property_sets returns True when property sets exist."""
    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[sample_property_set])
    assert obj.has_property_sets() is True


@pytest.mark.unit
def test_has_property_sets_false() -> None:
    """Test has_property_sets returns False when no property sets."""
    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[])
    assert obj.has_property_sets() is False


@pytest.mark.unit
def test_catalog_object_str() -> None:
    """Test string representation of catalog object."""
    obj = CatalogObject(id="TEST_1", name="Test Bridge", domain="Bridges")
    result = str(obj)
    assert "Test Bridge" in result
    assert "TEST_1" in result
    assert "Bridges" in result


@pytest.mark.unit
def test_catalog_object_str_with_property_sets(sample_property_set: PropertySet) -> None:
    """Test string representation includes property set count."""
    obj = CatalogObject(id="TEST_1", name="Test Bridge", domain="Bridges", property_sets=[sample_property_set])
    result = str(obj)
    assert "1 sets" in result


@pytest.mark.unit
def test_catalog_object_multiple_property_sets() -> None:
    """Test object with multiple property sets."""
    pset1 = PropertySet(id="PS_1", name="Dimensions", properties=[])
    pset2 = PropertySet(id="PS_2", name="Materials", properties=[])

    obj = CatalogObject(id="TEST_1", name="Test", domain="Test", property_sets=[pset1, pset2])

    assert len(obj.property_sets) == 2
    assert obj.get_property_set("Dimensions") == pset1
    assert obj.get_property_set("Materials") == pset2


@pytest.mark.unit
def test_catalog_object_complex_relationships() -> None:
    """Test object with complex relationship structure."""
    obj = CatalogObject(
        id="TEST_1",
        name="Test",
        domain="Test",
        relationships={"components": ["C1", "C2", "C3"], "assemblies": ["A1", "A2"], "dependencies": ["D1"]},
    )

    assert len(obj.relationships["components"]) == 3
    assert len(obj.relationships["assemblies"]) == 2
    assert len(obj.relationships["dependencies"]) == 1
