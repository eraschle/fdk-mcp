"""Tests for PropertySet and Property domain entities."""

import pytest

from fdk_mcp.domain.entities import Property, PropertySet


@pytest.mark.unit
def test_property_creation() -> None:
    """Test basic property creation."""
    prop = Property(id="PROP_1", name="Width", value="10.5", unit="m")
    assert prop.id == "PROP_1"
    assert prop.name == "Width"
    assert prop.value == "10.5"
    assert prop.unit == "m"


@pytest.mark.unit
def test_property_with_optional_fields() -> None:
    """Test property with all optional fields."""
    prop = Property(
        id="PROP_1",
        name="Width",
        value="10.5",
        unit="m",
        description="Width measurement",
        data_type="number",
        metadata={"source": "measurement"},
    )
    assert prop.description == "Width measurement"
    assert prop.data_type == "number"
    assert prop.metadata == {"source": "measurement"}


@pytest.mark.unit
def test_property_str_with_value_and_unit() -> None:
    """Test property string representation with value and unit."""
    prop = Property(id="PROP_1", name="Width", value="10.5", unit="m")
    result = str(prop)
    assert "Width" in result
    assert "10.5" in result
    assert "m" in result


@pytest.mark.unit
def test_property_str_without_value() -> None:
    """Test property string representation without value."""
    prop = Property(id="PROP_1", name="Width")
    result = str(prop)
    assert "Width" in result
    assert result == "Width"


@pytest.mark.unit
def test_property_set_creation() -> None:
    """Test basic property set creation."""
    pset = PropertySet(id="PS_1", name="Dimensions", properties=[])
    assert pset.id == "PS_1"
    assert pset.name == "Dimensions"
    assert pset.properties == []


@pytest.mark.unit
def test_property_set_with_properties() -> None:
    """Test property set with properties."""
    prop1 = Property(id="P1", name="Width", value="10")
    prop2 = Property(id="P2", name="Height", value="20")

    pset = PropertySet(id="PS_1", name="Dimensions", properties=[prop1, prop2])
    assert len(pset.properties) == 2
    assert pset.properties[0].name == "Width"
    assert pset.properties[1].name == "Height"


@pytest.mark.unit
def test_property_set_get_property_found() -> None:
    """Test get_property returns property when found."""
    prop = Property(id="P1", name="Width", value="10")
    pset = PropertySet(id="PS_1", name="Dimensions", properties=[prop])

    result = pset.get_property("Width")
    assert result is not None
    assert result.name == "Width"
    assert result.value == "10"


@pytest.mark.unit
def test_property_set_get_property_case_insensitive() -> None:
    """Test get_property is case insensitive."""
    prop = Property(id="P1", name="Width", value="10")
    pset = PropertySet(id="PS_1", name="Dimensions", properties=[prop])

    result = pset.get_property("width")
    assert result is not None
    assert result.name == "Width"


@pytest.mark.unit
def test_property_set_get_property_not_found() -> None:
    """Test get_property returns None when not found."""
    pset = PropertySet(id="PS_1", name="Dimensions", properties=[])

    result = pset.get_property("NonExistent")
    assert result is None


@pytest.mark.unit
def test_property_set_str() -> None:
    """Test property set string representation."""
    prop1 = Property(id="P1", name="Width", value="10")
    prop2 = Property(id="P2", name="Height", value="20")

    pset = PropertySet(id="PS_1", name="Dimensions", properties=[prop1, prop2])

    result = str(pset)
    assert "Dimensions" in result
    assert "2 properties" in result


@pytest.mark.unit
def test_property_set_with_description() -> None:
    """Test property set with description."""
    pset = PropertySet(id="PS_1", name="Dimensions", properties=[], description="Dimensional properties")
    assert pset.description == "Dimensional properties"


@pytest.mark.unit
def test_property_set_with_metadata() -> None:
    """Test property set with metadata."""
    pset = PropertySet(id="PS_1", name="Dimensions", properties=[], metadata={"source": "IFC", "version": "4.0"})
    assert pset.metadata == {"source": "IFC", "version": "4.0"}


@pytest.mark.unit
def test_property_numeric_value() -> None:
    """Test property with numeric value."""
    prop = Property(id="PROP_1", name="Temperature", value=25.5, unit="°C", data_type="float")
    assert prop.value == 25.5
    assert isinstance(prop.value, float)


@pytest.mark.unit
def test_property_boolean_value() -> None:
    """Test property with boolean value."""
    prop = Property(id="PROP_1", name="IsLoadBearing", value=True, data_type="boolean")
    assert prop.value is True
    assert isinstance(prop.value, bool)


@pytest.mark.unit
def test_property_none_value() -> None:
    """Test property with None value."""
    prop = Property(id="PROP_1", name="Optional", value=None)
    assert prop.value is None


@pytest.mark.unit
def test_property_set_multiple_get_property() -> None:
    """Test getting multiple properties from set."""
    prop1 = Property(id="P1", name="Width", value="10")
    prop2 = Property(id="P2", name="Height", value="20")
    prop3 = Property(id="P3", name="Depth", value="30")

    pset = PropertySet(id="PS_1", name="Dimensions", properties=[prop1, prop2, prop3])

    width_prop = pset.get_property("Width")
    height_prop = pset.get_property("Height")
    depth_prop = pset.get_property("Depth")

    assert width_prop is not None
    assert height_prop is not None
    assert depth_prop is not None

    assert width_prop.value == "10"
    assert height_prop.value == "20"
    assert depth_prop.value == "30"
    assert pset.get_property("Length") is None
