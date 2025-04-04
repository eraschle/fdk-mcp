import json
from pathlib import Path

from context import IFdkContext


def _register_catalog(current: Path) -> dict[str, Path]:
    elems = {}
    for path in current.iterdir():
        if path.is_dir():
            elems.update(_register_catalog(path))
        elif path.is_file() and path.suffix == ".json":
            object_id = path.with_suffix("").name
            elems[object_id] = path
    return elems


class JsonFdkContext(IFdkContext):
    def __init__(self, root_path: str):
        self.catalogs: dict[str, Path | dict] = {}
        self.catalogs.update(_register_catalog(Path(root_path)))

    def _catalog_by(self, obj_id: str) -> dict:
        data = self.catalogs.get(obj_id, {})
        if isinstance(data, Path):
            with open(data, "r", encoding="utf-8") as jf:
                data = json.load(jf)
                self.catalogs[obj_id] = data
        return data

    def info_by(self, object_id: str) -> dict:
        data = self._catalog_by(object_id)
        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "domainName": data.get("domainName"),
            "description": data.get("description"),
            "imageId": data.get("imageId"),
            "timestamp": data.get("creationTimestamp"),
        }

    def get_structured_description(self, object_id: str) -> dict:
        catalog = self._catalog_by(object_id)
        return catalog.get("structuredDescription", {})

    def get_component_relationships(self, object_id: str) -> list[dict]:
        catalog = self._catalog_by(object_id)
        return catalog.get("componentRelationships", [])

    def get_assembly_relationships(self, object_id: str) -> list[dict]:
        catalog = self._catalog_by(object_id)
        return catalog.get("assemblyRelationships", [])

    def get_release_history(self, object_id: str) -> list[dict]:
        catalog = self._catalog_by(object_id)
        return catalog.get("releaseHistory", [])

    def get_sia_phase_scopes(self, object_id: str) -> list[dict]:
        catalog = self._catalog_by(object_id)
        return catalog.get("siaPhaseScopes", [])

    def get_ifc_assignments(self, object_id: str) -> list[dict]:
        catalog = self._catalog_by(object_id)
        return catalog.get("ifcAssignments", [])

    def get_ebkp_concepts(self, object_id: str) -> list[dict]:
        catalog = self._catalog_by(object_id)
        return catalog.get("ebkpConcepts", [])

    def get_domain_models(self, object_id: str) -> list[dict]:
        catalog = self._catalog_by(object_id)
        return catalog.get("domainModels", [])

    def get_property_sets(self, object_id: str) -> list[dict]:
        catalog = self._catalog_by(object_id)
        return catalog.get("propertySets", [])

    def get_referenced_enumerations(self, object_id: str) -> list:
        catalog = self._catalog_by(object_id)
        return catalog.get("referencedEnumerations", [])
