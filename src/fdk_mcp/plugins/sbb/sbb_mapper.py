"""SBB Mapper - Transform between SBB models and domain entities."""

from ...domain.entities import CatalogObject, Property, PropertySet, ReleaseInfo
from ...domain.repositories import CatalogResponse
from .sbb_models import (
    SbbApiObjectsResponse,
    SbbDetailObject,
    SbbObjectSummary,
    SbbProperty,
    SbbPropertySet,
    SbbReleaseInfo,
)


class SbbMapper:
    """Maps between SBB-specific models and domain entities.

    This is the adapter layer that translates SBB's specific
    data structure into our vendor-agnostic domain model.
    """

    def map_release_info(self, sbb_release: SbbReleaseInfo) -> ReleaseInfo:
        """Map SBB release info to domain release info.

        Args:
            sbb_release: SBB-specific release info

        Returns:
            Domain ReleaseInfo
        """
        return ReleaseInfo(name=sbb_release["name"], date=sbb_release["date"])

    def map_property(self, sbb_prop: SbbProperty) -> Property:
        """Map SBB property to domain property.

        Args:
            sbb_prop: SBB-specific property

        Returns:
            Domain Property
        """
        return Property(
            id=sbb_prop["id"],
            name=sbb_prop["name"],
            unit=sbb_prop.get("unit"),
            description=sbb_prop.get("description"),
            data_type=sbb_prop.get("format", {}).get("type"),
            metadata={"fdkId": sbb_prop.get("format", {}).get("fdkId"), "example": sbb_prop.get("example")},
        )

    def map_property_set(self, sbb_pset: SbbPropertySet) -> PropertySet:
        """Map SBB property set to domain property set.

        Args:
            sbb_pset: SBB-specific property set

        Returns:
            Domain PropertySet
        """
        properties = [self.map_property(prop) for prop in sbb_pset.get("properties", [])]

        return PropertySet(id=sbb_pset["id"], name=sbb_pset["name"], properties=properties)

    def map_summary_to_catalog_object(self, sbb_obj: SbbObjectSummary) -> CatalogObject:
        """Map SBB object summary to domain catalog object.

        This creates a "lightweight" catalog object without property sets.

        Args:
            sbb_obj: SBB-specific object summary

        Returns:
            Domain CatalogObject (summary level)
        """
        # Extract IFC classifications
        classifications = [ifc["ifcClass"] for ifc in sbb_obj.get("ifcClassAssignments", [])]

        return CatalogObject(
            id=sbb_obj["id"],
            name=sbb_obj["name"],
            domain=sbb_obj["domainName"],
            image_id=sbb_obj.get("imageId"),
            classifications=classifications,
            metadata={
                "domainSequence": sbb_obj.get("domainSequence"),
                "sequenceObjectGroup": sbb_obj.get("sequenceObjectGroup"),
                "nameObjectGroup": sbb_obj.get("nameObjectGroup"),
                "nameSubgroup": sbb_obj.get("nameSubgroup"),
                "domainModel": sbb_obj.get("domainModel"),
            },
        )

    def map_detail_to_catalog_object(self, sbb_obj: SbbDetailObject) -> CatalogObject:
        """Map SBB detail object to domain catalog object.

        This creates a "full" catalog object with property sets and relationships.

        Args:
            sbb_obj: SBB-specific detail object

        Returns:
            Domain CatalogObject (detail level)
        """
        # Map property sets
        property_sets = [self.map_property_set(pset) for pset in sbb_obj.get("propertySets", [])]

        # Extract relationships
        relationships: dict[str, list[str]] = {}
        if component_rels := sbb_obj.get("componentRelationships"):
            relationships["components"] = [rel.get("id", "") for rel in component_rels]
        if assembly_rels := sbb_obj.get("assemblyRelationships"):
            relationships["assemblies"] = [rel.get("id", "") for rel in assembly_rels]

        # Extract classifications (IFC + eBKP)
        classifications = []
        if ifc_assignments := sbb_obj.get("ifcAssignments"):
            classifications.extend([ifc.get("ifcClass", "") for ifc in ifc_assignments])
        if ebkp_concepts := sbb_obj.get("ebkpConcepts"):
            classifications.extend([ebkp.get("code", "") for ebkp in ebkp_concepts])

        return CatalogObject(
            id=sbb_obj["id"],
            name=sbb_obj["name"],
            domain=sbb_obj["domainName"],
            description=sbb_obj.get("description"),
            image_id=sbb_obj.get("imageId"),
            property_sets=property_sets,
            relationships=relationships,
            classifications=classifications,
            metadata={
                "aksCode": sbb_obj.get("aksCode"),
                "creationTimestamp": sbb_obj.get("creationTimestamp"),
                "structuredDescription": sbb_obj.get("structuredDescription"),
                "releaseHistory": sbb_obj.get("releaseHistory"),
                "siaPhaseScopes": sbb_obj.get("siaPhaseScopes"),
                "domainModels": sbb_obj.get("domainModels"),
                "referencedEnumerations": sbb_obj.get("referencedEnumerations"),
            },
        )

    def map_api_response(self, sbb_response: SbbApiObjectsResponse) -> CatalogResponse:
        """Map SBB API response to domain catalog response.

        Args:
            sbb_response: SBB-specific API response

        Returns:
            Domain CatalogResponse
        """
        # Map all summaries to catalog objects
        objects = [self.map_summary_to_catalog_object(summary) for summary in sbb_response.get("summaries", [])]

        # Map release info
        release = None
        if sbb_release := sbb_response.get("release"):
            release = self.map_release_info(sbb_release)

        return CatalogResponse(objects=objects, total_count=sbb_response.get("count", len(objects)), release=release)
