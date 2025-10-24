"""Tests for Pydantic models with Literal type validation."""

from typing import Any

import pytest
from pydantic import ValidationError

from fdk_mcp.models import GroupObjectsInput, ResponseFormat


class TestGroupObjectsInputSortField:
    """Test SortField Literal validation in GroupObjectsInput."""

    @pytest.mark.unit
    def test_valid_sort_by_name(self) -> None:
        """Test that 'name' is accepted as a valid sort_by value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "sort_by": "name",
        }
        model = GroupObjectsInput(**data)
        assert model.sort_by == "name"

    @pytest.mark.unit
    def test_valid_sort_by_id(self) -> None:
        """Test that 'id' is accepted as a valid sort_by value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "sort_by": "id",
        }
        model = GroupObjectsInput(**data)
        assert model.sort_by == "id"

    @pytest.mark.unit
    def test_valid_sort_by_domain(self) -> None:
        """Test that 'domain' is accepted as a valid sort_by value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "sort_by": "domain",
        }
        model = GroupObjectsInput(**data)
        assert model.sort_by == "domain"

    @pytest.mark.unit
    def test_invalid_sort_by_value(self) -> None:
        """Test that invalid sort_by values are rejected."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "sort_by": "invalid_field",
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("sort_by",)
        assert "Input should be 'name', 'id' or 'domain'" in errors[0]["msg"]

    @pytest.mark.unit
    def test_sort_by_none_is_valid(self) -> None:
        """Test that sort_by can be None (default behavior)."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "sort_by": None,
        }
        model = GroupObjectsInput(**data)
        assert model.sort_by is None

    @pytest.mark.unit
    def test_sort_by_default_is_none(self) -> None:
        """Test that sort_by defaults to None when not provided."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
        }
        model = GroupObjectsInput(**data)
        assert model.sort_by is None


class TestGroupObjectsInputSortOrder:
    """Test SortOrder Literal validation in GroupObjectsInput."""

    @pytest.mark.unit
    def test_valid_order_asc(self) -> None:
        """Test that 'asc' is accepted as a valid order value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "order": "asc",
        }
        model = GroupObjectsInput(**data)
        assert model.order == "asc"

    @pytest.mark.unit
    def test_valid_order_desc(self) -> None:
        """Test that 'desc' is accepted as a valid order value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "order": "desc",
        }
        model = GroupObjectsInput(**data)
        assert model.order == "desc"

    @pytest.mark.unit
    def test_invalid_order_value(self) -> None:
        """Test that invalid order values are rejected."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "order": "ascending",
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("order",)
        assert "Input should be 'asc' or 'desc'" in errors[0]["msg"]

    @pytest.mark.unit
    def test_order_default_is_asc(self) -> None:
        """Test that order defaults to 'asc' when not provided."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
        }
        model = GroupObjectsInput(**data)
        assert model.order == "asc"


class TestGroupObjectsInputGroupField:
    """Test GroupField Literal validation in GroupObjectsInput."""

    @pytest.mark.unit
    def test_valid_group_by_domain(self) -> None:
        """Test that 'domain' is accepted as a valid group_by value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": "domain",
        }
        model = GroupObjectsInput(**data)
        assert model.group_by == "domain"

    @pytest.mark.unit
    def test_valid_group_by_ifc_class(self) -> None:
        """Test that 'ifcClass' is accepted as a valid group_by value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": "ifcClass",
        }
        model = GroupObjectsInput(**data)
        assert model.group_by == "ifcClass"

    @pytest.mark.unit
    def test_valid_group_by_property_set(self) -> None:
        """Test that 'propertySet' is accepted as a valid group_by value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": "propertySet",
        }
        model = GroupObjectsInput(**data)
        assert model.group_by == "propertySet"

    @pytest.mark.unit
    def test_valid_group_by_name(self) -> None:
        """Test that 'name' is accepted as a valid group_by value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": "name",
        }
        model = GroupObjectsInput(**data)
        assert model.group_by == "name"

    @pytest.mark.unit
    def test_valid_group_by_list_single(self) -> None:
        """Test that a list with a single valid field is accepted."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": ["domain"],
        }
        model = GroupObjectsInput(**data)
        assert model.group_by == ["domain"]

    @pytest.mark.unit
    def test_valid_group_by_list_multiple(self) -> None:
        """Test that a list with multiple valid fields is accepted."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": ["domain", "ifcClass", "propertySet"],
        }
        model = GroupObjectsInput(**data)
        assert model.group_by == ["domain", "ifcClass", "propertySet"]

    @pytest.mark.unit
    def test_valid_group_by_list_all_fields(self) -> None:
        """Test that a list with all valid fields is accepted."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": ["domain", "ifcClass", "propertySet", "name"],
        }
        model = GroupObjectsInput(**data)
        assert model.group_by == ["domain", "ifcClass", "propertySet", "name"]

    @pytest.mark.unit
    def test_invalid_group_by_single_value(self) -> None:
        """Test that invalid group_by value is rejected."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": "invalid_field",
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        # Union types produce multiple errors (one per variant)
        assert len(errors) >= 1
        # Check that at least one error has the expected message
        assert any("Input should be 'domain', 'ifcClass', 'propertySet' or 'name'" in error["msg"] for error in errors)

    @pytest.mark.unit
    def test_invalid_group_by_list_with_invalid_value(self) -> None:
        """Test that a list containing an invalid field is rejected."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": ["domain", "invalid_field"],
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        # Union types and list validation can produce multiple errors
        assert len(errors) >= 1
        # Check that all errors relate to group_by field
        assert all(error["loc"][0] == "group_by" for error in errors)
        # Check that we have an error about the invalid value
        assert any("invalid_field" in str(error["input"]) for error in errors)

    @pytest.mark.unit
    def test_group_by_none_is_valid(self) -> None:
        """Test that group_by can be None (sort-only mode)."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": None,
        }
        model = GroupObjectsInput(**data)
        assert model.group_by is None

    @pytest.mark.unit
    def test_group_by_default_is_none(self) -> None:
        """Test that group_by defaults to None when not provided."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
        }
        model = GroupObjectsInput(**data)
        assert model.group_by is None

    @pytest.mark.unit
    def test_group_by_empty_list_is_rejected(self) -> None:
        """Test that an empty list for group_by is rejected (line 246 edge case)."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": [],
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        assert any("empty" in error["msg"].lower() for error in errors)
        # Empty list should be rejected - use None for sort-only mode

    @pytest.mark.unit
    def test_group_by_mixed_valid_invalid_in_list(self) -> None:
        """Test that a list with both valid and invalid values is rejected (line 246)."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": ["domain", "invalidField", "name"],
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        # Should reject the list because it contains invalid field

    @pytest.mark.unit
    def test_group_by_duplicate_fields_in_list(self) -> None:
        """Test that duplicate fields in group_by list are accepted (line 246)."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": ["domain", "domain", "ifcClass"],
        }
        # Duplicates should be accepted - validation happens at use-case level
        model = GroupObjectsInput(**data)
        assert model.group_by == ["domain", "domain", "ifcClass"]

    @pytest.mark.unit
    def test_group_by_case_sensitive(self) -> None:
        """Test that group_by field names are case-sensitive (line 246)."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": "Domain",  # Wrong case
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        # "Domain" should not match "domain"


class TestGroupObjectsInputCombinations:
    """Test combinations of Literal fields in GroupObjectsInput."""

    @pytest.mark.unit
    def test_all_literal_fields_valid(self) -> None:
        """Test that all Literal fields can be set to valid values together."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2", "OBJ_3"],
            "group_by": ["domain", "ifcClass"],
            "sort_by": "name",
            "order": "desc",
        }
        model = GroupObjectsInput(**data)
        assert model.group_by == ["domain", "ifcClass"]
        assert model.sort_by == "name"
        assert model.order == "desc"

    @pytest.mark.unit
    def test_sort_only_mode(self) -> None:
        """Test sort-only mode (group_by=None, with sort_by and order)."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": None,
            "sort_by": "domain",
            "order": "asc",
        }
        model = GroupObjectsInput(**data)
        assert model.group_by is None
        assert model.sort_by == "domain"
        assert model.order == "asc"

    @pytest.mark.unit
    def test_group_only_mode(self) -> None:
        """Test group-only mode (with group_by, sort_by=None)."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1", "OBJ_2"],
            "group_by": "domain",
            "sort_by": None,
        }
        model = GroupObjectsInput(**data)
        assert model.group_by == "domain"
        assert model.sort_by is None
        assert model.order == "asc"  # default

    @pytest.mark.unit
    def test_minimal_valid_input(self) -> None:
        """Test minimal valid input (only object_ids required)."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1"],
        }
        model = GroupObjectsInput(**data)
        assert model.object_ids == ["OBJ_1"]
        assert model.group_by is None
        assert model.sort_by is None
        assert model.order == "asc"
        assert model.include_count is True
        assert model.language == "de"
        assert model.response_format == ResponseFormat.MARKDOWN


class TestGroupObjectsInputLanguageCode:
    """Test LanguageCode Literal validation in GroupObjectsInput."""

    @pytest.mark.unit
    def test_valid_language_de(self) -> None:
        """Test that 'de' is accepted as a valid language value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1"],
            "language": "de",
        }
        model = GroupObjectsInput(**data)
        assert model.language == "de"

    @pytest.mark.unit
    def test_valid_language_fr(self) -> None:
        """Test that 'fr' is accepted as a valid language value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1"],
            "language": "fr",
        }
        model = GroupObjectsInput(**data)
        assert model.language == "fr"

    @pytest.mark.unit
    def test_valid_language_it(self) -> None:
        """Test that 'it' is accepted as a valid language value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1"],
            "language": "it",
        }
        model = GroupObjectsInput(**data)
        assert model.language == "it"

    @pytest.mark.unit
    def test_valid_language_en(self) -> None:
        """Test that 'en' is accepted as a valid language value."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1"],
            "language": "en",
        }
        model = GroupObjectsInput(**data)
        assert model.language == "en"

    @pytest.mark.unit
    def test_invalid_language_code(self) -> None:
        """Test that invalid language codes are rejected."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1"],
            "language": "es",
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("language",)
        assert "Input should be 'de', 'fr', 'it' or 'en'" in errors[0]["msg"]

    @pytest.mark.unit
    def test_language_default_is_de(self) -> None:
        """Test that language defaults to 'de' when not provided."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1"],
        }
        model = GroupObjectsInput(**data)
        assert model.language == "de"


class TestGroupObjectsInputOtherValidations:
    """Test other validation rules in GroupObjectsInput."""

    @pytest.mark.unit
    def test_object_ids_required(self) -> None:
        """Test that object_ids is required."""
        data: dict[str, Any] = {}
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("object_ids",) for error in errors)

    @pytest.mark.unit
    def test_object_ids_min_length(self) -> None:
        """Test that object_ids must have at least one item."""
        data: dict[str, Any] = {
            "object_ids": [],
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("object_ids",)
        assert "at least 1 item" in errors[0]["msg"].lower()

    @pytest.mark.unit
    def test_object_ids_max_length(self) -> None:
        """Test that object_ids cannot exceed 500 items."""
        data: dict[str, Any] = {
            "object_ids": [f"OBJ_{i}" for i in range(501)],
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("object_ids",)
        assert "at most 500 items" in errors[0]["msg"].lower()

    @pytest.mark.unit
    def test_object_ids_exactly_500_is_valid(self) -> None:
        """Test that exactly 500 object_ids is valid."""
        data: dict[str, Any] = {
            "object_ids": [f"OBJ_{i}" for i in range(500)],
        }
        model = GroupObjectsInput(**data)
        assert len(model.object_ids) == 500

    @pytest.mark.unit
    def test_whitespace_stripping(self) -> None:
        """Test that string fields in object_ids are stripped of whitespace.

        Note: Literal type fields don't strip whitespace before validation in Pydantic,
        so we test with fields that do support stripping (like object_ids list items).
        """
        data: dict[str, Any] = {
            "object_ids": ["  OBJ_1  ", "OBJ_2  "],
            "group_by": "domain",  # Use valid literal value without whitespace
        }
        model = GroupObjectsInput(**data)
        # object_ids should have whitespace stripped
        assert model.object_ids == ["OBJ_1", "OBJ_2"]
        assert model.group_by == "domain"

    @pytest.mark.unit
    def test_extra_fields_forbidden(self) -> None:
        """Test that extra fields are rejected."""
        data: dict[str, Any] = {
            "object_ids": ["OBJ_1"],
            "extra_field": "not_allowed",
        }
        with pytest.raises(ValidationError) as exc_info:
            GroupObjectsInput(**data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)
