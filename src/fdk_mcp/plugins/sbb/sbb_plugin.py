"""SBB FDK Plugin - Main plugin class."""

from pathlib import Path
from typing import Any

from ...domain.repositories import CacheRepository, CatalogRepository
from ...infrastructure.cache import FileCacheRepository  # We'll create this
from ..base import PluginMetadata
from .sbb_api_client import SbbApiClient


class SbbFdkPlugin:
    """SBB FDK Plugin implementation.

    This plugin provides access to the Swiss Federal Railways (SBB)
    Facility Data Catalog (FDK) API.

    It implements the FdkPlugin protocol without explicit inheritance,
    following Clean Architecture's structural subtyping principle.
    """

    metadata = PluginMetadata(
        name="sbb",
        version="1.0.0",
        display_name="SBB FDK",
        description="Swiss Federal Railways Facility Data Catalog",
        supported_languages=["de", "fr", "it", "en"],
        api_base_url="https://bim-fdk-api.app.sbb.ch",
    )

    def create_catalog_repository(self, config: dict[str, Any]) -> CatalogRepository:
        """Create SBB API client.

        Args:
            config: Configuration dict with optional keys:
                - base_url: API base URL (default: SBB prod)
                - timeout: Request timeout in seconds (default: 30.0)
                - max_retries: Max retry attempts (default: 3)
                - retry_delay: Delay between retries (default: 1.0)

        Returns:
            SbbApiClient that implements CatalogRepository
        """
        base_url = config.get("base_url") or self.metadata.api_base_url
        if base_url is None:
            raise ValueError("API base_url must be provided in config or metadata")

        return SbbApiClient(
            base_url=str(base_url),
            timeout=config.get("timeout", 30.0),
            max_retries=config.get("max_retries", 3),
            retry_delay=config.get("retry_delay", 1.0),
        )

    def get_cache_path(self, config: dict[str, Any]) -> Path:
        # Get cache directory
        cache_dir = config.get("cache_dir")
        if cache_dir:
            return Path(cache_dir)
        return self._get_default_cache_dir()

    def create_cache_repository(self, config: dict[str, Any]) -> CacheRepository | None:
        """Create file-based cache repository for SBB data.

        SBB FDK is API-based, so caching is beneficial for performance.

        Args:
            config: Configuration dict with optional keys:
                - cache_dir: Cache directory path
                - cache_max_age_hours: Cache freshness threshold (default: 24)

        Returns:
            FileCacheRepository for caching SBB data,
            or None if caching is disabled in config
        """
        # Allow disabling cache via config
        if config.get("disable_cache", False):
            return None

        cache_path = self.get_cache_path(config)

        return FileCacheRepository(cache_dir=cache_path, max_age_hours=config.get("cache_max_age_hours", 24))

    def _get_default_cache_dir(self) -> Path:
        """Get platform-specific default cache directory.

        Returns:
            Path to default cache directory
        """
        import sys

        if sys.platform == "win32":
            import os

            app_data = os.getenv("APPDATA")
            if not app_data:
                raise OSError("APPDATA environment variable is not set")
            return Path(app_data) / "SBB_FDK_Cache"

        elif sys.platform == "darwin":
            return Path.home() / "Library" / "Caches" / "SBB_FDK_Cache"

        elif sys.platform == "linux":
            return Path.home() / ".cache" / "sbb_fdk_cache"

        else:
            # Fallback
            return Path("cache")

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate SBB plugin configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            PluginConfigurationError: If configuration is invalid
        """
        # Validate base_url if provided
        if base_url := config.get("base_url"):
            if not isinstance(base_url, str) or not base_url.startswith("http"):
                from ..base.exceptions import PluginConfigurationError

                raise PluginConfigurationError(f"Invalid base_url: {base_url}")

        # Validate timeout
        if timeout := config.get("timeout"):
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                from ..base.exceptions import PluginConfigurationError

                raise PluginConfigurationError(f"Invalid timeout: {timeout}")

        # Validate cache_max_age_hours
        if max_age := config.get("cache_max_age_hours"):
            if not isinstance(max_age, (int, float)) or max_age <= 0:
                from ..base.exceptions import PluginConfigurationError

                raise PluginConfigurationError(f"Invalid cache_max_age_hours: {max_age}")

        return True
