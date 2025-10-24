"""Dependency Injection Container for FDK MCP Server."""

import os
import sys
from pathlib import Path
from typing import Any

from ...domain.repositories import CacheRepository, CatalogRepository
from ...plugins.base import FdkPlugin
from ...plugins.sbb import SbbFdkPlugin
from .plugin_registry import PluginRegistry


class Container:
    """Dependency Injection Container.

    Central orchestrator that wires together all application components
    following Clean Architecture principles.

    Responsibilities:
    1. Initialize and manage plugin registry
    2. Load configuration from environment variables
    3. Create repository instances via active plugin
    4. Instantiate use cases with injected dependencies

    Design Principles:
    - Dependency Inversion: Components depend on abstractions (protocols)
    - Single Responsibility: Only responsible for dependency creation/injection
    - Open/Closed: Easy to add new plugins without modifying container
    - Configuration Management: Environment variables with sensible defaults

    Example:
        ```python
        # Simple usage with defaults
        container = Container()
        use_case = container.get_use_case(ListObjectsUseCase)
        response = await use_case.execute(request)

        # Override plugin and configuration
        container = Container(plugin_name="sbb", config={"base_url": "http://localhost:8000", "timeout": 10.0})

        # Get repository directly
        catalog = container.get_catalog_repository()
        objects = await catalog.list_objects()
        ```
    """

    def __init__(self, plugin_name: str | None = None, config: dict[str, Any] | None = None) -> None:
        """Initialize dependency injection container.

        Args:
            plugin_name: Name of plugin to use (e.g., "sbb").
                        Overrides FDK_PLUGIN environment variable.
                        Defaults to "sbb" if not specified.
            config: Optional configuration dictionary.
                   Overrides environment variables if provided.
                   Use this for testing or custom configurations.

        Raises:
            PluginNotFoundError: If specified plugin is not registered
            PluginConfigurationError: If configuration is invalid

        Example:
            ```python
            # Use defaults (SBB plugin, env vars)
            container = Container()

            # Override plugin
            container = Container(plugin_name="sbb")

            # Override configuration
            container = Container(
                config={"base_url": "http://test.example.com", "cache_dir": "/tmp/test_cache", "timeout": 10.0}
            )

            # Override both
            container = Container(plugin_name="sbb", config={"base_url": "http://localhost:8000"})
            ```
        """
        # Setup plugin registry and register all available plugins
        self.registry = PluginRegistry()
        self._register_plugins()

        # Load configuration (env vars or provided config)
        self._config = config if config is not None else self._load_config()

        # Get active plugin (from parameter, env var, or default to "sbb")
        active_plugin_name = plugin_name or os.getenv("FDK_PLUGIN", "sbb")
        self.plugin: FdkPlugin = self.registry.get_plugin(active_plugin_name)

        # Validate configuration
        self.plugin.validate_config(self._config)

        # Create repositories via plugin factory methods
        self.catalog_repo: CatalogRepository = self.plugin.create_catalog_repository(self._config)
        self.cache_repo: CacheRepository | None = self.plugin.create_cache_repository(self._config)

    def _register_plugins(self) -> None:
        """Register all available FDK plugins.

        This is where new plugins are added to the system.
        Following Open/Closed principle: open for extension by adding
        new plugins, closed for modification of existing logic.

        Example:
            To add a new plugin:
            ```python
            self.registry.register(SbbFdkPlugin())
            self.registry.register(OtherFdkPlugin())  # Add new plugin here
            ```
        """
        # Register SBB plugin (Swiss Federal Railways)
        self.registry.register(SbbFdkPlugin())

        # TODO: Register additional FDK plugins here as they become available
        # Example:
        # self.registry.register(ExampleFdkPlugin())
        # self.registry.register(AnotherFdkPlugin())

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from environment variables.

        Reads configuration from environment with sensible defaults.
        This follows 12-factor app principles for configuration management.

        Environment Variables:
        - FDK_API_URL: Base URL for FDK API (plugin-specific default if not set)
        - FDK_CACHE_DIR: Cache directory path (platform-specific default if not set)
        - FDK_TIMEOUT: Request timeout in seconds (default: 30.0)
        - FDK_CACHE_MAX_AGE_HOURS: Cache freshness threshold (default: 24)
        - FDK_MAX_CONCURRENT: Max concurrent requests (default: 10)
        - FDK_MAX_RETRIES: Max retry attempts (default: 3)
        - FDK_RETRY_DELAY: Delay between retries in seconds (default: 1.0)

        Returns:
            Configuration dictionary with all settings

        Example:
            ```bash
            # Set environment variables
            export FDK_API_URL="http://localhost:8000"
            export FDK_CACHE_DIR="/tmp/fdk_cache"
            export FDK_TIMEOUT="10.0"

            # Configuration will be loaded automatically
            container = Container()
            ```
        """
        return {
            # API configuration
            "base_url": os.getenv("FDK_API_URL"),  # None = use plugin default
            "timeout": float(os.getenv("FDK_TIMEOUT", "30.0")),
            "max_retries": int(os.getenv("FDK_MAX_RETRIES", "3")),
            "retry_delay": float(os.getenv("FDK_RETRY_DELAY", "1.0")),
            # Cache configuration
            "cache_dir": os.getenv("FDK_CACHE_DIR") or self._get_default_cache_dir(),
            "cache_max_age_hours": int(os.getenv("FDK_CACHE_MAX_AGE_HOURS", "24")),
            # Performance configuration
            "max_concurrent": int(os.getenv("FDK_MAX_CONCURRENT", "10")),
        }

    def _get_default_cache_dir(self) -> Path:
        """Get platform-specific default cache directory.

        Follows platform conventions for cache directories:
        - Windows: %APPDATA%/FDK_MCP_Cache
        - macOS: ~/Library/Caches/FDK_MCP_Cache
        - Linux: ~/.cache/fdk_mcp_cache

        Returns:
            Path to default cache directory

        Raises:
            OSError: If APPDATA is not set on Windows

        Example:
            ```python
            # Windows
            # C:/Users/username/AppData/Roaming/FDK_MCP_Cache

            # macOS
            # /Users/username/Library/Caches/FDK_MCP_Cache

            # Linux
            # /home/username/.cache/fdk_mcp_cache
            ```
        """
        if sys.platform == "win32":
            app_data = os.getenv("APPDATA")
            if not app_data:
                raise OSError("APPDATA environment variable is not set")
            return Path(app_data) / "FDK_MCP_Cache"

        elif sys.platform == "darwin":
            return Path.home() / "Library" / "Caches" / "FDK_MCP_Cache"

        elif sys.platform == "linux":
            return Path.home() / ".cache" / "fdk_mcp_cache"

        else:
            # Fallback for other platforms
            return Path.home() / ".fdk_mcp_cache"

    def get_use_case(self, use_case_class: type[Any]) -> Any:
        """Create use case instance with injected dependencies.

        This is the primary method for getting use case instances.
        Dependencies (repositories) are automatically injected via constructor.

        Args:
            use_case_class: Use case class to instantiate.
                           Must accept catalog_repo and cache_repo parameters.

        Returns:
            Use case instance with repositories injected

        Example:
            ```python
            from fdk_mcp.use_cases import ListObjectsUseCase, GetObjectUseCase, SearchPropertiesUseCase

            container = Container()

            # Create use case instances
            list_use_case = container.get_use_case(ListObjectsUseCase)
            get_use_case = container.get_use_case(GetObjectUseCase)
            search_use_case = container.get_use_case(SearchPropertiesUseCase)

            # Execute use cases
            list_response = await list_use_case.execute(list_request)
            get_response = await get_use_case.execute(get_request)
            search_response = await search_use_case.execute(search_request)
            ```
        """
        return use_case_class(
            catalog_repo=self.catalog_repo,
            cache_repo=self.cache_repo,  # Can be None for file-based plugins
        )

    def get_catalog_repository(self) -> CatalogRepository:
        """Get catalog repository instance.

        Use this when you need direct access to the catalog repository
        instead of going through a use case.

        Returns:
            CatalogRepository instance (vendor-specific implementation)

        Example:
            ```python
            container = Container()
            catalog = container.get_catalog_repository()

            # Direct repository access
            objects = await catalog.list_objects()
            obj = await catalog.get_object("123")
            ```
        """
        return self.catalog_repo

    def get_cache_repository(self) -> CacheRepository | None:
        """Get cache repository instance.

        Returns None if the active plugin doesn't provide caching
        (e.g., file-based plugins that don't need additional caching).

        Returns:
            CacheRepository instance or None if caching not available

        Example:
            ```python
            container = Container()
            cache = container.get_cache_repository()

            if cache is not None:
                # Cache available - use it
                cached_obj = cache.get_cached_object("123")
                if cached_obj is None:
                    # Fetch from catalog and cache it
                    obj = await catalog.get_object("123")
                    cache.save_object("123", obj)
            else:
                # No caching - fetch directly
                obj = await catalog.get_object("123")
            ```
        """
        return self.cache_repo

    def get_plugin_info(self) -> dict[str, Any]:
        """Get information about the active plugin.

        Returns metadata about the currently active plugin,
        useful for debugging, logging, or displaying to users.

        Returns:
            Dictionary with plugin metadata:
            - name: Plugin identifier
            - version: Plugin version
            - display_name: Human-readable name
            - description: Plugin description
            - supported_languages: List of language codes
            - api_base_url: API base URL (if applicable)
            - has_cache: Whether caching is available

        Example:
            ```python
            container = Container()
            info = container.get_plugin_info()

            # {
            #     "name": "sbb",
            #     "version": "1.0.0",
            #     "display_name": "SBB FDK",
            #     "description": "Swiss Federal Railways Facility Data Catalog",
            #     "supported_languages": ["de", "fr", "it", "en"],
            #     "api_base_url": "https://bim-fdk-api.app.sbb.ch",
            #     "has_cache": True
            # }
            ```
        """
        metadata = self.plugin.metadata
        return {
            "name": metadata.name,
            "version": metadata.version,
            "display_name": metadata.display_name,
            "description": metadata.description,
            "supported_languages": metadata.supported_languages,
            "api_base_url": metadata.api_base_url,
            "has_cache": self.cache_repo is not None,
        }

    def list_available_plugins(self) -> list[str]:
        """List all registered plugin names.

        Returns:
            List of plugin names available in the registry

        Example:
            ```python
            container = Container()
            plugins = container.list_available_plugins()
            # ["sbb", "other_fdk"]
            ```
        """
        return self.registry.list_plugins()
