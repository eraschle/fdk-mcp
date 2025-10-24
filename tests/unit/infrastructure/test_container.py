"""Tests for DI Container."""

import pytest

from fdk_mcp.infrastructure.di import Container
from fdk_mcp.use_cases import ListObjectsUseCase


@pytest.mark.unit
def test_container_initialization() -> None:
    """Test container initialization with defaults."""
    container = Container()

    assert container.plugin is not None
    assert container.catalog_repo is not None
    assert container.registry is not None


@pytest.mark.unit
def test_container_get_use_case() -> None:
    """Test getting use case from container."""
    container = Container()

    use_case = container.get_use_case(ListObjectsUseCase)

    assert isinstance(use_case, ListObjectsUseCase)
    assert use_case.catalog is not None


@pytest.mark.unit
def test_container_get_catalog_repository() -> None:
    """Test getting catalog repository from container."""
    container = Container()

    catalog_repo = container.get_catalog_repository()

    assert catalog_repo is not None
    # Check it has the expected methods
    assert hasattr(catalog_repo, "fetch_all_objects")
    assert hasattr(catalog_repo, "fetch_object_by_id")


@pytest.mark.unit
def test_container_get_cache_repository() -> None:
    """Test getting cache repository from container."""
    container = Container()

    cache_repo = container.get_cache_repository()

    # Cache repo can be None for some plugins
    if cache_repo is not None:
        assert hasattr(cache_repo, "is_cache_fresh")
        assert hasattr(cache_repo, "save_object")


@pytest.mark.unit
def test_container_get_plugin_info() -> None:
    """Test getting plugin info from container."""
    container = Container()

    info = container.get_plugin_info()

    assert "name" in info
    assert "version" in info
    assert "display_name" in info
    assert "supported_languages" in info
    assert info["name"] == "sbb"


@pytest.mark.unit
def test_container_list_available_plugins() -> None:
    """Test listing available plugins."""
    container = Container()

    plugins = container.list_available_plugins()

    assert isinstance(plugins, list)
    assert "sbb" in plugins


@pytest.mark.unit
def test_container_with_custom_config() -> None:
    """Test container with custom configuration."""
    custom_config = {"base_url": "http://test.example.com", "timeout": 10.0, "cache_dir": "/tmp/test_cache"}

    container = Container(config=custom_config)

    assert container.plugin is not None
    assert container._config["base_url"] == "http://test.example.com"
    assert container._config["timeout"] == 10.0


@pytest.mark.unit
def test_container_plugin_name_override() -> None:
    """Test container with plugin name override."""
    container = Container(plugin_name="sbb")

    assert container.plugin.metadata.name == "sbb"


@pytest.mark.unit
def test_container_creates_different_use_case_instances() -> None:
    """Test that container creates new use case instances each time."""
    container = Container()

    use_case1 = container.get_use_case(ListObjectsUseCase)
    use_case2 = container.get_use_case(ListObjectsUseCase)

    # Should be different instances
    assert use_case1 is not use_case2

    # But should share same repositories
    assert use_case1.catalog is use_case2.catalog
