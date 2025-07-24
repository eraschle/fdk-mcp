"""
Data Models für 3D Modellsucher App
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ImageFile:
    """Represents a single image file with metadata"""

    path: str
    name: str
    display_name: str
    size: int
    modified_time: datetime
    dimensions: tuple[int, int] | None = None
    fachbereich: str = ""
    object_folder: str = ""

    @classmethod
    def from_path(cls, path: str, base_path: str = "") -> "ImageFile":
        """Create ImageFile from file path"""
        try:
            stat = os.stat(path)
            name = os.path.basename(path)

            # Extract display name
            base_name = os.path.splitext(name)[0]
            display_name = cls._extract_display_name(base_name)

            # Extract fachbereich and object folder
            fachbereich, object_folder = cls._extract_folder_info(path, base_path)

            return cls(
                path=path,
                name=name,
                display_name=display_name,
                size=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                fachbereich=fachbereich,
                object_folder=object_folder,
            )
        except Exception:
            # Fallback for problematic files
            return cls(
                path=path,
                name=os.path.basename(path),
                display_name=os.path.basename(path),
                size=0,
                modified_time=datetime.now(),
                fachbereich="Unbekannt",
                object_folder="Unbekanntes Objekt",
            )

    @staticmethod
    def _extract_display_name(base_name: str) -> str:
        """Extract display name by removing OBJ prefix pattern"""
        try:
            name_parts = base_name.split("_")
            name_parts = name_parts[2:]
            if name_parts and name_parts[0] != "RSRG":
                name_parts = name_parts[1:]
            return " ".join(name_parts) if name_parts else base_name
        except Exception:
            return base_name

    @staticmethod
    def _extract_folder_info(path: str, base_path: str) -> tuple[str, str]:
        """Extract fachbereich and object folder from path"""
        try:
            root_dir = os.path.dirname(path)
            relative_path = os.path.relpath(root_dir, base_path)
            path_parts = relative_path.split(os.path.sep)

            fachbereich = (
                path_parts[0] if len(path_parts) > 0 and path_parts[0] != "." else ""
            )

            if len(path_parts) > 1:
                object_folder = path_parts[1]
            elif len(path_parts) == 1 and path_parts[0] != ".":
                object_folder = f"Objekte in '{path_parts[0]}'"
            else:
                object_folder = "Unbekanntes Objekt"

            return fachbereich, object_folder
        except Exception:
            return "", "Unbekanntes Objekt"

    def get_formatted_size(self) -> str:
        """Get human-readable file size"""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024**2:
            return f"{self.size / 1024:.1f} KB"
        else:
            return f"{self.size / (1024**2):.1f} MB"

    def get_tooltip_content(self) -> str:
        """Generate tooltip content with metadata"""
        dimensions_str = (
            f"{self.dimensions[0]}x{self.dimensions[1]} px"
            if self.dimensions
            else "Unbekannt"
        )

        return (
            f"Datei: {self.name}\n"
            f"Pfad: {self.path}\n"
            f"Größe: {self.get_formatted_size()}\n"
            f"Dimensionen: {dimensions_str}\n"
            f"Geändert: {self.modified_time.strftime('%d.%m.%Y %H:%M')}"
        )


@dataclass
class SearchResult:
    """Represents search results grouped by object folder"""

    images_by_object: dict[str, list[ImageFile]]
    total_count: int
    search_path: str
    search_time: datetime

    def get_images_for_fachbereich(
        self, fachbereich: str
    ) -> dict[str, list[ImageFile]]:
        """Filter images by fachbereich"""
        if not fachbereich or fachbereich == "Alle Fachbereiche":
            return self.images_by_object.copy()

        filtered = {}
        for object_folder, images in self.images_by_object.items():
            matching_images = [img for img in images if img.fachbereich == fachbereich]
            if matching_images:
                filtered[object_folder] = matching_images

        return filtered

    def filter_by_name(
        self, search_term: str, fachbereich: str = ""
    ) -> dict[str, list[ImageFile]]:
        """Filter images by name search term and optional fachbereich"""
        base_groups = self.get_images_for_fachbereich(fachbereich)

        if not search_term:
            return base_groups

        search_parts = [part.lower() for part in search_term.split()]
        filtered = {}

        for object_folder, images in base_groups.items():
            matching_images = []
            for img in images:
                if any(part in img.name.lower() for part in search_parts):
                    matching_images.append(img)

            if matching_images:
                filtered[object_folder] = matching_images

        return filtered


@dataclass
class AppConfig:
    """Application configuration"""

    cache_size: int = 500
    max_workers: int = 4
    image_size: tuple[int, int] = (150, 150)
    window_size: str = "1920x1080"
    default_path: str = "%RSRG_BIBLIOTHEK%\\3D Objekte"
    supported_formats: list[str] = field(default_factory=list)

    # API Feature settings
    enable_api_panel: bool = True  # Enable by default for testing
    api_base_url: str = "https://bim-fdk-api.app.sbb.ch"
    api_language: str = "de"
    api_cache_ttl: int = 3600  # seconds
    api_timeout: int = 10  # seconds
    api_panel_width: int = 400  # pixels
    api_sash_position: int = -1  # Saved sash position (-1 = use default)

    def __post_init__(self):
        if not self.supported_formats:
            self.supported_formats = ["*.png", "*.jpg", "*.jpeg"]


@dataclass
class CacheItem:
    """Represents a cached image item"""

    image_file: ImageFile
    image_data: Any  # ImageTk.PhotoImage
    access_time: datetime
    load_time: datetime


@dataclass
class FDKProperty:
    """Represents a single property from FDK API"""

    name: str
    value: str | int | float | bool | None
    description: str = ""
    unit: str = ""
    data_type: str = ""


@dataclass
class FDKPropertySet:
    """Represents a property set from FDK API"""

    name: str
    properties: dict[str, FDKProperty]
    description: str = ""

    @classmethod
    def from_api_data(cls, name: str, data: dict) -> "FDKPropertySet":
        """Create PropertySet from API data"""
        properties = {}

        for prop_name, prop_data in data.items():
            if isinstance(prop_data, dict) and "value" in prop_data:
                properties[prop_name] = FDKProperty(
                    name=prop_name,
                    value=prop_data.get("value"),
                    description=prop_data.get("description", ""),
                    unit=prop_data.get("unit", ""),
                    data_type=prop_data.get("dataType", ""),
                )
            else:
                # Simple value - ensure it's a supported type
                if isinstance(prop_data, (str, int, float, bool)) or prop_data is None:
                    value = prop_data
                else:
                    # Convert complex types to string
                    value = str(prop_data)

                properties[prop_name] = FDKProperty(
                    name=prop_name,
                    value=value,
                    description="",
                    unit="",
                    data_type=type(prop_data).__name__
                    if prop_data is not None
                    else "null",
                )

        return cls(
            name=name,
            properties=properties,
            description=data.get("description", "") if isinstance(data, dict) else "",
        )


@dataclass
class FDKIFCAssignment:
    """Represents IFC assignment data from FDK API"""

    version: str
    ifc_class: str
    description: str = ""


@dataclass
class FDKObject:
    """Represents a complete FDK object from the API"""

    object_id: str
    name: str
    domain: str
    aks_code: str
    description: str
    summary: str
    homepage_url: str
    property_sets: dict[str, FDKPropertySet]
    properties: dict[str, FDKProperty]
    ifc_assignments: list[FDKIFCAssignment]
    created_at: datetime
    last_updated: datetime

    @classmethod
    def from_api_response(cls, data: dict) -> "FDKObject":
        """Create FDKObject from API response data"""
        object_id = data.get("id", "")
        name = data.get("name", "")
        domain = data.get("domain", "")
        aks_code = data.get("aksCode", "")
        description = data.get("description", "")
        summary = data.get("summary", "")
        homepage_url = data.get("homepageUrl", "")

        # Parse property sets
        property_sets = {}
        psets_data = data.get("propertySets", [])
        for pset_data in psets_data:
            pset_name = pset_data.get("name", "")
            if not pset_name:
                continue
            property_sets[pset_name] = FDKPropertySet.from_api_data(
                pset_name, pset_data
            )

        # Parse individual properties
        properties = {}
        props_data = data.get("properties", {})
        for prop_name, prop_value in props_data.items():
            # Ensure value is a supported type
            if isinstance(prop_value, (str, int, float, bool)) or prop_value is None:
                value = prop_value
            else:
                # Convert complex types to string
                value = str(prop_value)

            properties[prop_name] = FDKProperty(
                name=prop_name,
                value=value,
                data_type=type(prop_value).__name__
                if prop_value is not None
                else "null",
            )

        # Parse IFC assignments
        ifc_assignments = []
        ifc_data = data.get("ifcAssignments", [])
        for ifc_item in ifc_data:
            if isinstance(ifc_item, dict):
                ifc_assignments.append(
                    FDKIFCAssignment(
                        version=ifc_item.get("version", ""),
                        ifc_class=ifc_item.get("ifcClass", ""),
                        description=ifc_item.get("description", ""),
                    )
                )

        return cls(
            object_id=object_id,
            name=name,
            domain=domain,
            aks_code=aks_code,
            description=description,
            summary=summary,
            homepage_url=homepage_url,
            property_sets=property_sets,
            properties=properties,
            ifc_assignments=ifc_assignments,
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

    @staticmethod
    def extract_object_id_from_filename(filename: str) -> str | None:
        """Extract FDK object ID from image filename (e.g., OBJ_BR_1_xxx.png -> OBJ_BR_1)"""
        try:
            base_name = os.path.splitext(filename)[0]
            parts = base_name.split("_")

            # Look for pattern: OBJ_XX_Y where XX is letters and Y is number
            if len(parts) >= 3 and parts[0] == "OBJ":
                # Return OBJ_XX_Y format
                return f"{parts[0]}_{parts[1]}_{parts[2]}"
        except Exception:
            pass
        return None
