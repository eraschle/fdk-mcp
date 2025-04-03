import json
from pathlib import Path
from typing import Iterable


def load_catalog(root_path: Path, object_id: str) -> Iterable[dict]:
    """Return the catalog data from the given object ID."""
    results = root_path.glob(f"**/{object_id}*.json")
    if not results:
        raise FileNotFoundError(f"Object ID {object_id} not found in {root_path}")
    for result in results:
        with open(result, "r", encoding="utf-8") as file:
            yield json.load(file)


class McpFDKGateway(IMcpFDKGateway):
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)

    def object_info_by(self, object_id: str) -> dict:
        catalog = load_catalog(root_path=self.root_path, object_id=object_id)
        return catalog.get("name")

    def get_domain_name(self) -> str:
        catalog = load_catalog()
        return catalog.get("domainName")

    def get_description(self) -> str:
        catalog = load_catalog()
        return catalog.get("description")

    def get_structured_description(self) -> list:
        catalog = load_catalog()
        return catalog.get("structuredDescription")

    def get_image_id(self) -> str:
        catalog = load_catalog()
        return catalog.get("imageId")

    def get_creation_timestamp(self) -> str:
        catalog = load_catalog()
        return catalog.get("creationTimestamp")

    def get_component_relationships(self) -> list:
        catalog = load_catalog()
        return catalog.get("componentRelationships")

    def get_assembly_relationships(self) -> list:
        catalog = load_catalog()
        return catalog.get("assemblyRelationships")

    def get_release_history(self) -> list:
        catalog = load_catalog()
        return catalog.get("releaseHistory")

    def get_sia_phase_scopes(self) -> list:
        catalog = load_catalog()
        return catalog.get("siaPhaseScopes")

    def get_ifc_assignments(self) -> list:
        catalog = load_catalog()
        return catalog.get("ifcAssignments")

    def get_ebkp_concepts(self) -> list:
        catalog = load_catalog()
        return catalog.get("ebkpConcepts")

    def get_domain_models(self) -> list:
        catalog = load_catalog()
        return catalog.get("domainModels")

    def get_property_sets(self) -> list:
        catalog = load_catalog()
        return catalog.get("propertySets")

    def get_referenced_enumerations(self) -> list:
        catalog = load_catalog()
        return catalog.get("referencedEnumerations")
