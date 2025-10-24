"""SBB-specific type definitions.

These are the original SBB FDK data structures as returned by the API.
They will be mapped to domain entities by the SBB mapper.
"""

from typing import Any, TypedDict


# API Response Types
class SbbReleaseInfo(TypedDict):
    """SBB-specific release version information."""

    name: str
    date: str


class SbbDomainModel(TypedDict):
    """SBB-specific domain model reference."""

    id: str
    name: str


class SbbIfcClassAssignment(TypedDict):
    """SBB-specific IFC class assignment."""

    version: str
    ifcClass: str


class SbbObjectSummary(TypedDict):
    """SBB-specific object summary from /objects endpoint."""

    id: str
    name: str
    domainName: str
    domainSequence: int
    sequenceObjectGroup: int
    domainModel: list[SbbDomainModel]
    nameObjectGroup: str
    nameSubgroup: str
    imageId: str
    ifcClassAssignments: list[SbbIfcClassAssignment]


class SbbPropertyFormat(TypedDict):
    """SBB-specific property format definition."""

    type: str
    fdkId: str | None
    name: str


class SbbProperty(TypedDict):
    """SBB-specific property definition."""

    id: str
    format: SbbPropertyFormat
    name: str
    unit: str
    description: str
    example: str


class SbbPropertySet(TypedDict):
    """SBB-specific property set containing multiple properties."""

    id: str
    name: str
    properties: list[SbbProperty]


class SbbDetailObject(TypedDict):
    """SBB-specific complete object details from /objects/{id} endpoint."""

    # Base fields from ObjectSummary
    id: str
    name: str
    domainName: str
    imageId: str
    # Additional detail fields
    description: str
    structuredDescription: list[dict[str, Any]]
    aksCode: str
    creationTimestamp: str
    componentRelationships: list[dict[str, str]]
    assemblyRelationships: list[dict[str, str]]
    releaseHistory: list[dict[str, Any]]
    siaPhaseScopes: list[dict[str, Any]]
    ifcAssignments: list[dict[str, str]]
    ebkpConcepts: list[dict[str, str]]
    domainModels: list[SbbDomainModel]
    propertySets: list[SbbPropertySet]
    referencedEnumerations: list[dict[str, Any]]


class SbbApiObjectsResponse(TypedDict):
    """SBB-specific response from /objects endpoint."""

    count: int
    summaries: list[SbbObjectSummary]
    release: SbbReleaseInfo
