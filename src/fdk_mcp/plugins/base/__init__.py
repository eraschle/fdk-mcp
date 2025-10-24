"""Base plugin interface and exceptions."""

from .exceptions import PluginError, PluginNotFoundError
from .plugin_interface import FdkPlugin, PluginMetadata


__all__ = [
    "FdkPlugin",
    "PluginMetadata",
    "PluginError",
    "PluginNotFoundError",
]
