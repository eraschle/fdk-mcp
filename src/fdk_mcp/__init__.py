"""
FDK MCP Server - Model Context Protocol Server for FDK (Fach-Daten-Katalog) data
"""

from .data_provider import FDKDataProvider
from .models import (
    FDKObject,
    FDKReferenceAnalysis,
    FDKSearchCriteria,
    FDKSearchResult,
    FDKServerConfig,
    FDKServerStats,
)
from .server import FDKMCPServer

__version__ = "0.1.0"
__all__ = [
    "FDKDataProvider",
    "FDKMCPServer",
    "FDKObject",
    "FDKReferenceAnalysis",
    "FDKSearchCriteria",
    "FDKSearchResult",
    "FDKServerConfig",
    "FDKServerStats",
]
