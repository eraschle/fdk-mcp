"""Plugin registry for managing FDK plugins."""

from ...plugins.base import FdkPlugin, PluginNotFoundError


class PluginRegistry:
    """Central registry for FDK plugins.

    Manages the life cycle of FDK plugins, allowing registration,
    retrieval, and listing of available plugins.

    This follows the Registry pattern and supports multiple FDK vendors
    (e.g., SBB, future vendors) through a simple name-based lookup system.

    Design Principles:
    - Single Responsibility: Manages plugin registration and retrieval
    - Open/Closed: Open for new plugins, closed for modification
    - Dependency Inversion: Depends on FdkPlugin protocol, not concrete implementations

    Example:
        ```python
        registry = PluginRegistry()
        registry.register(SbbFdkPlugin())
        registry.register(OtherFdkPlugin())

        # Retrieve plugin by name
        sbb_plugin = registry.get_plugin("sbb")

        # List all available plugins
        plugins = registry.list_plugins()  # ["sbb", "other"]
        ```
    """

    def __init__(self) -> None:
        """Initialize an empty plugin registry."""
        self._plugins: dict[str, FdkPlugin] = {}

    def register(self, plugin: FdkPlugin) -> None:
        """Register a plugin with the registry.

        Args:
            plugin: Plugin instance to register. Must implement FdkPlugin protocol.

        Raises:
            ValueError: If a plugin with the same name is already registered.
                       This prevents accidental overrides and ensures explicit control.

        Example:
            ```python
            registry = PluginRegistry()
            registry.register(SbbFdkPlugin())

            # Trying to register again will raise ValueError
            registry.register(SbbFdkPlugin())  # ValueError: Plugin 'sbb' already registered
            ```
        """
        plugin_name = plugin.metadata.name
        if plugin_name in self._plugins:
            raise ValueError(f"Plugin '{plugin_name}' already registered")

        self._plugins[plugin_name] = plugin

    def get_plugin(self, name: str) -> FdkPlugin:
        """Get a plugin by name.

        Args:
            name: Plugin name (e.g., "sbb", "example_fdk")

        Returns:
            Plugin instance that implements FdkPlugin protocol

        Raises:
            PluginNotFoundError: If no plugin with the given name is registered.
                                This provides clear error messaging for missing plugins.

        Example:
            ```python
            plugin = registry.get_plugin("sbb")
            catalog_repo = plugin.create_catalog_repository(config)
            ```
        """
        if name not in self._plugins:
            raise PluginNotFoundError(name)

        return self._plugins[name]

    def list_plugins(self) -> list[str]:
        """List all registered plugin names.

        Returns:
            List of plugin names in registration order.
            Returns empty list if no plugins are registered.

        Example:
            ```python
            registry.register(SbbFdkPlugin())
            registry.register(OtherFdkPlugin())

            plugins = registry.list_plugins()
            # ["sbb", "other"]
            ```
        """
        return list(self._plugins.keys())

    def has_plugin(self, name: str) -> bool:
        """Check if a plugin is registered.

        Provides a safe way to check for plugin existence without
        catching exceptions.

        Args:
            name: Plugin name to check

        Returns:
            True if plugin with given name is registered, False otherwise

        Example:
            ```python
            if registry.has_plugin("sbb"):
                plugin = registry.get_plugin("sbb")
            else:
                print("SBB plugin not available")
            ```
        """
        return name in self._plugins
