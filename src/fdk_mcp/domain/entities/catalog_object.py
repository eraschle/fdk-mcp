"""Catalog object entity - vendor-agnostic."""

from dataclasses import dataclass, field
from typing import Any

from .property_set import PropertySet


@dataclass
class CatalogObject:
    """A catalog object/item from any FDK system.

    This is the central domain entity that represents objects from any FDK,
    regardless of their specific structure or field names.

    Examples:
        - SBB FDK: Bridge, Tunnel, Track
        - Other FDK: Building, Component, Material
    """

    id: str
    """Unique object identifier (vendor-specific format)."""

    name: str
    """Object name/title."""

    domain: str
    """Object domain/category (e.g., 'Bridges', 'Buildings')."""

    description: str | None = None
    """Object description."""

    image_id: str | None = None
    """Image/thumbnail identifier."""

    property_sets: list[PropertySet] = field(default_factory=list)
    """List of property sets containing object attributes."""

    relationships: dict[str, list[str]] = field(default_factory=dict)
    """Related object IDs grouped by relationship type."""

    classifications: list[str] = field(default_factory=list)
    """Classification codes (e.g., IFC classes, eBKP codes)."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional vendor-specific metadata that doesn't fit standard fields."""

    def get_property_set(self, name: str) -> PropertySet | None:
        """Get property set by name.

        Args:
            name: Property set name to search for

        Returns:
            PropertySet if found, None otherwise
        """
        name_lower = name.lower()
        for pset in self.property_sets:
            if pset.name.lower() == name_lower:
                return pset
        return None

    def get_property(self, property_name: str, pset_name: str | None = None) -> Any | None:
        """Get property value by name.

        Args:
            property_name: Name of the property to find
            pset_name: Optional property set name to narrow search

        Returns:
            Property value if found, None otherwise
        """
        # Search in specific property set
        if pset_name:
            pset = self.get_property_set(pset_name)
            if pset:
                prop = pset.get_property(property_name)
                return prop.value if prop else None
            return None

        # Search in all property sets
        for pset in self.property_sets:
            prop = pset.get_property(property_name)
            if prop:
                return prop.value

        return None

    def has_property_sets(self) -> bool:
        """Check if object has detailed property sets.

        Returns:
            True if object has property sets (detail object), False otherwise (summary)
        """
        return len(self.property_sets) > 0

    def __str__(self) -> str:
        """Human-readable representation."""
        parts = [f"{self.name} ({self.id})"]
        if self.domain:
            parts.append(f"- Domain: {self.domain}")
        if self.property_sets:
            parts.append(f"- Properties: {len(self.property_sets)} sets")
        return " ".join(parts)
