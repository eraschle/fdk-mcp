"""Tests for SBB FDK Plugin."""

import pytest

from fdk_mcp.plugins.sbb import SbbFdkPlugin


@pytest.mark.unit
def test_sbb_plugin_initialization() -> None:
    """Test SBB plugin initialization."""
    plugin = SbbFdkPlugin()

    assert plugin is not None
    assert plugin.metadata.name == "sbb"


@pytest.mark.unit
def test_sbb_plugin_metadata() -> None:
    """Test SBB plugin metadata."""
    plugin = SbbFdkPlugin()
    metadata = plugin.metadata

    assert metadata.name == "sbb"
    assert metadata.version
    assert metadata.display_name
    assert metadata.description
    assert metadata.api_base_url
    assert isinstance(metadata.supported_languages, list)
    assert "de" in metadata.supported_languages


@pytest.mark.unit
def test_sbb_plugin_supported_languages() -> None:
    """Test SBB plugin supported languages."""
    plugin = SbbFdkPlugin()

    languages = plugin.metadata.supported_languages

    assert "de" in languages
    assert "fr" in languages
    assert "it" in languages
    assert "en" in languages


@pytest.mark.unit
def test_sbb_plugin_validate_config_valid() -> None:
    """Test SBB plugin validates valid configuration."""
    plugin = SbbFdkPlugin()

    config = {"base_url": "https://example.com", "timeout": 30.0, "cache_dir": "/tmp/cache"}

    # Should not raise any exceptions
    plugin.validate_config(config)


@pytest.mark.unit
def test_sbb_plugin_validate_config_missing_fields() -> None:
    """Test SBB plugin accepts config with missing optional fields."""
    plugin = SbbFdkPlugin()

    config = {}

    # Should not raise - optional fields have defaults
    plugin.validate_config(config)


@pytest.mark.unit
def test_sbb_plugin_create_catalog_repository() -> None:
    """Test SBB plugin creates catalog repository."""
    plugin = SbbFdkPlugin()

    config = {"base_url": "https://example.com", "timeout": 30.0}

    catalog_repo = plugin.create_catalog_repository(config)

    assert catalog_repo is not None
    assert hasattr(catalog_repo, "fetch_all_objects")
    assert hasattr(catalog_repo, "fetch_object_by_id")
    assert hasattr(catalog_repo, "get_supported_languages")


@pytest.mark.unit
def test_sbb_plugin_create_cache_repository() -> None:
    """Test SBB plugin creates cache repository."""
    plugin = SbbFdkPlugin()

    config = {"cache_dir": "/tmp/test_cache", "cache_max_age_hours": 24}

    cache_repo = plugin.create_cache_repository(config)

    assert cache_repo is not None
    assert hasattr(cache_repo, "is_cache_fresh")
    assert hasattr(cache_repo, "save_object")
    assert hasattr(cache_repo, "get_cached_object")


@pytest.mark.unit
def test_sbb_plugin_repository_independence() -> None:
    """Test that plugin creates independent repository instances."""
    plugin = SbbFdkPlugin()

    config = {"base_url": "https://example.com"}

    repo1 = plugin.create_catalog_repository(config)
    repo2 = plugin.create_catalog_repository(config)

    # Should be different instances
    assert repo1 is not repo2
