"""Release information entity - vendor-agnostic."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseInfo:
    """Version/release information for a catalog.

    This is vendor-agnostic and works with any FDK system.
    """

    name: str
    """Release/version name (e.g., '2024.1', 'v1.5')."""

    date: str
    """Release date in ISO format (e.g., '2024-01-15')."""

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.name} ({self.date})"
