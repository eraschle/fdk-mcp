"""Tests for PluginRegistry."""

import pytest

from fdk_mcp.infrastructure.di import PluginRegistry
from fdk_mcp.plugins.base import PluginNotFoundError
from fdk_mcp.plugins.sbb import SbbFdkPlugin


@pytest.mark.unit
def test_plugin_registry_initialization() -> None:
    """Test plugin registry initialization."""
    registry = PluginRegistry()

    assert registry is not None
    assert registry.list_plugins() == []


@pytest.mark.unit
def test_plugin_registry_register() -> None:
    """Test registering a plugin."""
    registry = PluginRegistry()
    plugin = SbbFdkPlugin()

    registry.register(plugin)

    assert registry.has_plugin("sbb")
    assert "sbb" in registry.list_plugins()


@pytest.mark.unit
def test_plugin_registry_get_plugin() -> None:
    """Test getting a registered plugin."""
    registry = PluginRegistry()
    plugin = SbbFdkPlugin()
    registry.register(plugin)

    retrieved = registry.get_plugin("sbb")

    assert retrieved is not None
    assert retrieved.metadata.name == "sbb"


@pytest.mark.unit
def test_plugin_registry_get_plugin_not_found() -> None:
    """Test getting a non-existent plugin raises error."""
    registry = PluginRegistry()

    with pytest.raises(PluginNotFoundError) as exc_info:
        registry.get_plugin("nonexistent")

    assert "nonexistent" in str(exc_info.value)


@pytest.mark.unit
def test_plugin_registry_duplicate_registration() -> None:
    """Test that duplicate plugin registration raises error."""
    registry = PluginRegistry()
    plugin = SbbFdkPlugin()
    registry.register(plugin)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(SbbFdkPlugin())


@pytest.mark.unit
def test_plugin_registry_has_plugin() -> None:
    """Test has_plugin method."""
    registry = PluginRegistry()
    plugin = SbbFdkPlugin()

    assert not registry.has_plugin("sbb")

    registry.register(plugin)

    assert registry.has_plugin("sbb")
    assert not registry.has_plugin("other")


@pytest.mark.unit
def test_plugin_registry_list_plugins() -> None:
    """Test listing all registered plugins."""
    registry = PluginRegistry()

    assert registry.list_plugins() == []

    registry.register(SbbFdkPlugin())

    plugins = registry.list_plugins()
    assert len(plugins) == 1
    assert "sbb" in plugins


@pytest.mark.unit
def test_plugin_registry_multiple_plugins() -> None:
    """Test registry with multiple plugins."""
    registry = PluginRegistry()
    plugin1 = SbbFdkPlugin()

    registry.register(plugin1)

    # Can't test with another plugin since we only have SBB
    # But we can verify the list works correctly
    plugins = registry.list_plugins()
    assert len(plugins) == 1
