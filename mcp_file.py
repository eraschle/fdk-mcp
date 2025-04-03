from typing import Protocol, Callable, Any, Dict
import json
import os


class IMcpFDKGateway(Protocol):
    pass


def load_catalog() -> dict:
    """Lädt und parst die JSON-Datei aus dem docs-Verzeichnis."""
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "docs", "example.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class McpFDKGateway(IMcpFDKGateway):
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}
        self.resources: Dict[str, Callable[..., Any]] = {}

    def add_tool(self, route: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[route] = func
            return func
        return decorator

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func
        return decorator

    def resource(self, route: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.resources[route] = func
            return func
        return decorator
        
    def get_id(self) -> str:
        catalog = load_catalog()
        return catalog.get("id")
        
    def get_name(self) -> str:
        catalog = load_catalog()
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

mcp = McpFDKGateway()


@mcp.tool()
def get_catalog() -> dict:
    """Liefert den gesamten Katalog aus docs/example.json."""
    return load_catalog()


@mcp.tool()
def list_property_sets() -> list:
    """Gibt eine Liste der PropertySets zurück."""
    catalog = load_catalog()
    return catalog.get("propertySets", [])


@mcp.resource("/catalog/{object_id}")
def get_catalog_object(object_id: str) -> dict:
    """
    Sucht im Katalog nach einem Objekt mit der angegebenen ID.
    Liefert das Objekt oder eine Fehlermeldung.
    """
    catalog = load_catalog()
    if catalog.get("id") == object_id:
        return catalog
    else:
        return {"error": f"Objekt mit id '{object_id}' nicht gefunden"}
