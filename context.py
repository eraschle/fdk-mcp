from typing import Protocol


class IFdkContext(Protocol):
    def info_by(self, object_id: str) -> dict:
        """Object information by object ID.
        These are the values: id, name, domainName, description,
        imageId and creation timestamp.

        return: dict
        """
        ...

    def get_structured_description(self, object_id: str) -> dict:
        """Get the structured description of the object."""
        ...

    def get_component_relationships(self, object_id: str) -> list[dict]:
        """Get the component relationships of the object."""
        ...

    def get_assembly_relationships(self, object_id: str) -> list[dict]:
        """Get the assembly relationships of the object."""
        ...

    def get_release_history(self, object_id: str) -> list[dict]:
        """Get the release history of the object."""
        ...

    def get_sia_phase_scopes(self, object_id: str) -> list[dict]:
        """Get the SIA phase scopes of the object."""
        ...

    def get_ifc_assignments(self, object_id: str) -> list[dict]:
        """Get the IFC assignments of the object."""
        ...

    def get_ebkp_concepts(self, object_id: str) -> list[dict]:
        """Get the EBKP concepts of the object."""
        ...

    def get_domain_models(self, object_id: str) -> list[dict]:
        """Get the domain models of the object."""
        ...

    def get_property_sets(self, object_id: str) -> list[dict]:
        """Get the property sets of the object."""
        ...

    def get_referenced_enumerations(self, object_id: str) -> list:
        """Get the referenced enumerations of the object."""
        ...
