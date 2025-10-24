"""SBB FDK MCP Server - Model Context Protocol server for SBB FDK catalog queries."""

__version__ = "1.0.1"

# Re-export commonly used types and models
from .models import (
    # Type Definitions
    LanguageCode,
    SortField,
    SortOrder,
    GroupField,
    # Enums
    ResponseFormat,
    DetailLevel,
    # Input Models
    ListObjectsInput,
    GetObjectInput,
    SearchPropertiesInput,
    AdvancedSearchInput,
    GetCacheCoverageInput,
    GroupObjectsInput,
)

__all__ = [
    "__version__",
    # Type Definitions
    "LanguageCode",
    "SortField",
    "SortOrder",
    "GroupField",
    # Enums
    "ResponseFormat",
    "DetailLevel",
    # Input Models
    "ListObjectsInput",
    "GetObjectInput",
    "SearchPropertiesInput",
    "AdvancedSearchInput",
    "GetCacheCoverageInput",
    "GroupObjectsInput",
]
