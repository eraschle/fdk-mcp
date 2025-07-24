"""
FDK Data Models for MCP Server
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class FDKComponentRelationship(BaseModel):
    """A component relationship in the FDK object"""
    id: str
    name: str


class FDKAssemblyRelationship(BaseModel):
    """An assembly relationship in the FDK object"""
    id: str
    name: str


class FDKStructuredDescriptionItem(BaseModel):
    """A structured description item"""
    type: str
    content: Union[str, List[str]]


class FDKObject(BaseModel):
    """Complete FDK Object representation"""
    id: str
    name: str
    domain_name: str = Field(alias="domainName")
    description: str
    structured_description: List[FDKStructuredDescriptionItem] = Field(
        alias="structuredDescription", default_factory=list
    )
    image_id: Optional[str] = Field(alias="imageId", default=None)
    creation_timestamp: Optional[str] = Field(alias="creationTimestamp", default=None)
    component_relationships: List[FDKComponentRelationship] = Field(
        alias="componentRelationships", default_factory=list
    )
    assembly_relationships: List[FDKAssemblyRelationship] = Field(
        alias="assemblyRelationships", default_factory=list
    )
    # Additional fields that might exist in the data
    summary: Optional[str] = None
    aks_code: Optional[str] = Field(alias="aksCode", default=None)
    homepage_url: Optional[str] = Field(alias="homepageUrl", default=None)
    properties: Dict[str, Any] = Field(default_factory=dict)
    property_sets: List[Dict[str, Any]] = Field(alias="propertySets", default_factory=list)
    ifc_assignments: List[Dict[str, Any]] = Field(alias="ifcAssignments", default_factory=list)

    class Config:
        validate_by_name = True
        populate_by_name = True

    @property
    def object_type(self) -> str:
        """Extract object type from ID (e.g., 'FB' from 'OBJ_FB_1')"""
        parts = self.id.split("_")
        if len(parts) >= 2:
            return parts[1]
        return "UNKNOWN"

    @property
    def object_number(self) -> str:
        """Extract object number from ID (e.g., '1' from 'OBJ_FB_1')"""
        parts = self.id.split("_")
        if len(parts) >= 3:
            return parts[2]
        return "0"

    def get_related_object_ids(self) -> List[str]:
        """Get all related object IDs from relationships"""
        related_ids = []
        for rel in self.component_relationships:
            related_ids.append(rel.id)
        for rel in self.assembly_relationships:
            related_ids.append(rel.id)
        return related_ids

    def get_plain_description(self) -> str:
        """Get description without structured markup"""
        if self.structured_description:
            parts = []
            for item in self.structured_description:
                if isinstance(item.content, str):
                    parts.append(item.content)
                elif isinstance(item.content, list):
                    parts.extend(item.content)
            return "\n\n".join(parts)
        return self.description


class FDKSearchCriteria(BaseModel):
    """Search criteria for FDK objects"""
    object_id: Optional[str] = None
    name_pattern: Optional[str] = None
    domain: Optional[str] = None
    object_type: Optional[str] = None
    limit: int = 10
    include_relationships: bool = True


class FDKSearchResult(BaseModel):
    """Search result containing FDK objects"""
    objects: List[FDKObject]
    total_count: int
    search_criteria: FDKSearchCriteria
    search_timestamp: datetime = Field(default_factory=datetime.now)


class FDKReferenceAnalysis(BaseModel):
    """Analysis of references between FDK objects"""
    object_id: str
    referenced_by: List[str] = Field(default_factory=list)  # Objects that reference this one
    references_to: List[str] = Field(default_factory=list)  # Objects this one references
    reference_count: int = 0
    depth_level: int = 0  # How deep in the reference tree


class FDKDomainStats(BaseModel):
    """Statistics for a specific domain"""
    domain_name: str
    object_count: int
    object_types: Dict[str, int] = Field(default_factory=dict)
    most_referenced: List[str] = Field(default_factory=list)


class FDKServerConfig(BaseModel):
    """Configuration for the FDK MCP Server"""
    data_directory: str = "data/sample"
    api_base_url: str = "https://bim-fdk-api.app.sbb.ch"
    api_language: str = "de"
    cache_ttl_seconds: int = 3600
    enable_api_fallback: bool = True
    max_search_results: int = 100
    log_level: str = "INFO"


class FDKServerStats(BaseModel):
    """Server statistics"""
    objects_loaded: int = 0
    api_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    domains: Dict[str, FDKDomainStats] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)