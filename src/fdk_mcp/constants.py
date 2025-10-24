"""Constants for SBB FDK MCP server."""

import os
import sys
from pathlib import Path


# API Configuration
API_TIMEOUT = 30.0
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 1.0


def _get_cache_dir() -> Path:
    """Get the cache directory path."""
    if sys.platform == "win32":
        app_data = os.getenv("APPDATA")
        if not app_data:
            raise OSError("APPDATA environment variable is not set.")
        return Path(app_data) / "SBB_FDK_Cache"
    if sys.platform == "darwin":
        home = Path.home()
        return home / "Library" / "Caches" / "SBB_FDK_Cache"
    if sys.platform == "linux":
        home = Path.home()
        return home / ".cache" / "sbb_fdk_cache"
    return Path("cache")


def _ensure_cache_dir(path: Path) -> Path:
    """Get the cache directory path."""
    dir_path = path
    if path.is_file():
        dir_path = path.parent
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
    return path


# Cache Configuration
CACHE_DIR = _ensure_cache_dir(_get_cache_dir())
CACHE_OBJECTS_DIR = CACHE_DIR / "objects"
CACHE_METADATA_FILE = CACHE_DIR / "metadata.json"
CACHE_MAX_AGE_HOURS = 24

# Response Configuration
CHARACTER_LIMIT = 25000
DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# Language Configuration
DEFAULT_LANGUAGE = "de"
SUPPORTED_LANGUAGES = ["de", "fr", "it", "en"]

# Text Formatting
DESCRIPTION_PREVIEW_LENGTH = 200  # Max chars for description preview
PROPERTY_DESCRIPTION_LENGTH = 150  # Max chars for property description
MODELS_PREVIEW_COUNT = 3  # Number of models to show in preview
TRUNCATION_BUFFER = 500  # Buffer size when truncating long responses

# Retry Configuration
RETRY_BACKOFF_BASE = 2  # Base for exponential backoff (2^attempt)
