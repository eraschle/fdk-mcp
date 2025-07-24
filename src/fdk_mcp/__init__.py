"""
FDK MCP Server - Model Context Protocol Server for FDK (Fach-Daten-Katalog) data
"""

from .models import (
    FDKObject,
    FDKSearchCriteria, 
    FDKSearchResult,
    FDKReferenceAnalysis,
    FDKServerConfig,
    FDKServerStats
)
from .data_provider import FDKDataProvider
from .server import FDKMCPServer

__version__ = "0.1.0"
__all__ = [
    "FDKObject",
    "FDKSearchCriteria",
    "FDKSearchResult", 
    "FDKReferenceAnalysis",
    "FDKServerConfig",
    "FDKServerStats",
    "FDKDataProvider",
    "FDKMCPServer"
]