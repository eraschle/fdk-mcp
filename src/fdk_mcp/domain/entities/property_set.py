"""Property and PropertySet entities - vendor-agnostic."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Property:
    """A single property/attribute of a catalog object.

    This is vendor-agnostic and represents properties from any FDK system.
    """

    id: str
    """Unique property identifier."""

    name: str
    """Property name (e.g., 'Width', 'Material')."""

    value: Any | None = None
    """Property value (can be string, number, etc.)."""

    unit: str | None = None
    """Unit of measurement (e.g., 'm', 'kg')."""

    description: str | None = None
    """Property description."""

    data_type: str | None = None
    """Data type (e.g., 'string', 'number', 'boolean')."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional vendor-specific metadata."""

    def __str__(self) -> str:
        """Human-readable representation."""
        parts = [self.name]
        if self.value is not None:
            parts.append(f"= {self.value}")
        if self.unit:
            parts.append(self.unit)
        return " ".join(parts)


@dataclass
class PropertySet:
    """A group of related properties.

    This is vendor-agnostic and represents property sets from any FDK system.
    """

    id: str
    """Unique property set identifier."""

    name: str
    """Property set name (e.g., 'Pset_WallCommon', 'Dimensions')."""

    properties: list[Property] = field(default_factory=list)
    """List of properties in this set."""

    description: str | None = None
    """Property set description."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional vendor-specific metadata."""

    def get_property(self, name: str) -> Property | None:
        """Get property by name.

        Args:
            name: Property name to search for

        Returns:
            Property if found, None otherwise
        """
        for prop in self.properties:
            if prop.name.lower() == name.lower():
                return prop
        return None

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.name} ({len(self.properties)} properties)"
