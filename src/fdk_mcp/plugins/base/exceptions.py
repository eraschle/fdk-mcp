"""Plugin-related exceptions."""


class PluginError(Exception):
    """Base exception for plugin-related errors."""

    pass


class PluginNotFoundError(PluginError):
    """Raised when a requested plugin is not registered."""

    def __init__(self, plugin_name: str):
        """Initialize exception.

        Args:
            plugin_name: Name of the plugin that was not found
        """
        self.plugin_name = plugin_name
        super().__init__(f"Plugin '{plugin_name}' not found")


class PluginConfigurationError(PluginError):
    """Raised when plugin configuration is invalid."""

    pass


class CatalogError(Exception):
    """Base exception for catalog operations."""

    pass


class ObjectNotFoundError(CatalogError):
    """Raised when a catalog object is not found."""

    def __init__(self, object_id: str):
        """Initialize exception.

        Args:
            object_id: ID of the object that was not found
        """
        self.object_id = object_id
        super().__init__(f"Object '{object_id}' not found")
