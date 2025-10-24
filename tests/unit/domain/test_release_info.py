"""Tests for ReleaseInfo domain entity."""

import pytest

from fdk_mcp.domain.entities import ReleaseInfo


@pytest.mark.unit
def test_release_info_creation() -> None:
    """Test basic release info creation."""
    release = ReleaseInfo(name="v2024.1", date="2024-01-15")
    assert release.name == "v2024.1"
    assert release.date == "2024-01-15"


@pytest.mark.unit
def test_release_info_equality() -> None:
    """Test release info equality comparison."""
    release1 = ReleaseInfo(name="v2024.1", date="2024-01-15")
    release2 = ReleaseInfo(name="v2024.1", date="2024-01-15")
    release3 = ReleaseInfo(name="v2024.2", date="2024-02-01")

    assert release1 == release2
    assert release1 != release3


@pytest.mark.unit
def test_release_info_different_names() -> None:
    """Test release info with different names."""
    release1 = ReleaseInfo(name="v2024.1", date="2024-01-15")
    release2 = ReleaseInfo(name="v2024.2", date="2024-01-15")

    assert release1 != release2


@pytest.mark.unit
def test_release_info_different_dates() -> None:
    """Test release info with different dates."""
    release1 = ReleaseInfo(name="v2024.1", date="2024-01-15")
    release2 = ReleaseInfo(name="v2024.1", date="2024-02-15")

    assert release1 != release2


@pytest.mark.unit
def test_release_info_str() -> None:
    """Test string representation of release info."""
    release = ReleaseInfo(name="v2024.1", date="2024-01-15")
    result = str(release)
    assert "v2024.1" in result or "2024-01-15" in result


@pytest.mark.unit
def test_release_info_with_empty_values() -> None:
    """Test release info with empty values."""
    release = ReleaseInfo(name="", date="")
    assert release.name == ""
    assert release.date == ""
