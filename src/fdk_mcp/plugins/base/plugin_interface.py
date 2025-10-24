"""Base plugin interface for FDK implementations."""

from dataclasses import dataclass
from typing import Any, Protocol

from ...domain.repositories import CacheRepository, CatalogRepository


@dataclass(frozen=True)
class PluginMetadata:
    """Metadata about an FDK plugin."""

    name: str
    """Plugin identifier (e.g., 'sbb', 'example_fdk')."""

    version: str
    """Plugin version (e.g., '1.0.0')."""

    display_name: str
    """Human-readable plugin name (e.g., 'SBB FDK')."""

    description: str
    """Plugin description."""

    supported_languages: list[str]
    """List of supported language codes (e.g., ['de', 'en'])."""

    api_base_url: str | None = None
    """Base URL for the FDK API (if applicable)."""


class FdkPlugin(Protocol):
    """Protocol that all FDK plugins must implement.

    This defines the contract for FDK plugins. Each plugin represents
    a specific FDK system (e.g., SBB, another organization's FDK).

    Using Protocol (not ABC) follows Clean Architecture principles:
    - No explicit inheritance needed
    - Structural subtyping
    - Outer layers don't depend on inner layers

    Example:
        ```python
        class SbbFdkPlugin:
            metadata = PluginMetadata(
                name="sbb",
                version="1.0.0",
                display_name="SBB FDK",
                description="Swiss Federal Railways FDK",
                supported_languages=["de", "fr", "it", "en"],
            )

            def create_catalog_repository(self, config: dict[str, Any]) -> CatalogRepository:
                return SbbApiClient(config.get("base_url"))

            def create_cache_repository(self, config: dict[str, Any]) -> CacheRepository:
                return FileCacheRepository(config.get("cache_dir"))
        ```
    """

    metadata: PluginMetadata
    """Plugin metadata."""

    def create_catalog_repository(self, config: dict[str, Any]) -> CatalogRepository:
        """Create FDK-specific catalog repository (API client).

        This is a factory method that creates the vendor-specific
        implementation of CatalogRepository.

        Args:
            config: Plugin-specific configuration
                (e.g., API URL, credentials, timeouts)

        Returns:
            CatalogRepository implementation for this FDK

        Example:
            ```python
            # SBB Plugin
            def create_catalog_repository(self, config):
                return SbbApiClient(
                    base_url=config.get("base_url", "https://bim-fdk-api.app.sbb.ch"),
                    timeout=config.get("timeout", 30.0),
                )


            # Another FDK Plugin
            def create_catalog_repository(self, config):
                return OtherFdkClient(api_endpoint=config.get("endpoint"), api_key=config.get("api_key"))
            ```
        """
        ...

    def create_cache_repository(self, config: dict[str, Any]) -> CacheRepository | None:
        """Create cache repository (optional).

        Args:
            config: Cache configuration
                (e.g., cache directory, TTL, max size)

        Returns:
            CacheRepository implementation if plugin needs caching,
            None if plugin handles optimization internally (e.g., file-based, in-memory)

        Note:
            This is a Swiss compromise! 🇨🇭
            - Plugins that need caching (API-based) can provide cache
            - Plugins that don't need it (file-based, RAM-based) return None
            - Use Cases must handle None gracefully

        Examples:
            ```python
            # API-based plugin needs cache
            def create_cache_repository(self, config):
                return FileCacheRepository(config.get("cache_dir"))


            # File-based plugin doesn't need cache
            def create_cache_repository(self, config):
                return None  # Files are already on disk
            ```
        """
        ...

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate plugin configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            PluginConfigurationError: If configuration is invalid
        """
        ...
