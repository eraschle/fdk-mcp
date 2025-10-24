"""Catalog repository protocol - vendor-agnostic interface."""

from dataclasses import dataclass
from typing import Protocol

from ...models import LanguageCode
from ..entities import CatalogObject, ReleaseInfo


@dataclass
class CatalogResponse:
    """Response from catalog listing operation."""

    objects: list[CatalogObject]
    """List of catalog objects."""

    total_count: int
    """Total number of objects in catalog."""

    release: ReleaseInfo | None = None
    """Release information if available."""


class CatalogRepository(Protocol):
    """Protocol for catalog operations.

    This defines the interface that all FDK plugins must implement.
    It's vendor-agnostic - works with SBB FDK, other FDKs, or mock data.

    Using Protocol (not ABC) follows Clean Architecture's Dependency Rule:
    - Domain layer defines the interface
    - Outer layers (plugins) implement it
    - No explicit inheritance needed
    """

    async def fetch_all_objects(self, language: LanguageCode = "en") -> CatalogResponse:
        """Fetch all objects from catalog.

        Args:
            language: Language code (implementation-specific)

        Returns:
            CatalogResponse with objects and metadata

        Raises:
            CatalogError: On API/connection errors
        """
        ...

    async def fetch_object_by_id(self, object_id: str, language: LanguageCode = "en") -> CatalogObject:
        """Fetch specific object by ID.

        Args:
            object_id: Unique object identifier
            language: Language code (implementation-specific)

        Returns:
            CatalogObject with full details

        Raises:
            ObjectNotFoundError: If object doesn't exist
            CatalogError: On API/connection errors
        """
        ...

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of language codes (e.g., ['en', 'de', 'fr'])
        """
        ...
