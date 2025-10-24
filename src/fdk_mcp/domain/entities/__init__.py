"""Domain entities - vendor-agnostic business objects."""

from .catalog_object import CatalogObject
from .property_set import Property, PropertySet
from .release_info import ReleaseInfo


__all__ = [
    "CatalogObject",
    "Property",
    "PropertySet",
    "ReleaseInfo",
]
