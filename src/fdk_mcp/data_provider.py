"""
FDK Data Provider - Handles loading FDK objects from JSON files and API
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

import httpx

from .models import FDKObject, FDKSearchCriteria, FDKSearchResult, FDKServerConfig, FDKReferenceAnalysis


class FDKDataProvider:
    """Provider for FDK object data from JSON files and API"""

    def __init__(self, config: FDKServerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._objects: Dict[str, FDKObject] = {}
        self._cache: Dict[str, tuple[FDKObject, datetime]] = {}
        self._loaded = False
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def initialize(self) -> None:
        """Initialize the data provider by loading JSON files"""
        if self._loaded:
            return

        await self._load_json_files()
        self._loaded = True
        self.logger.info(f"Loaded {len(self._objects)} FDK objects from JSON files")

    async def _load_json_files(self) -> None:
        """Load all JSON files from the data directory"""
        data_path = Path(self.config.data_directory)
        if not data_path.exists():
            self.logger.warning(f"Data directory does not exist: {data_path}")
            return

        json_files = list(data_path.glob("*.json"))
        self.logger.info(f"Found {len(json_files)} JSON files")

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                fdk_object = FDKObject(**data)
                self._objects[fdk_object.id] = fdk_object
                self.logger.debug(f"Loaded object: {fdk_object.id} - {fdk_object.name}")
                
            except Exception as e:
                self.logger.error(f"Error loading {json_file}: {e}")

    async def get_object(self, object_id: str) -> Optional[FDKObject]:
        """Get a specific FDK object by ID"""
        await self.initialize()
        
        # Check local objects first
        if object_id in self._objects:
            return self._objects[object_id]
        
        # Check cache
        if object_id in self._cache:
            cached_object, cached_time = self._cache[object_id]
            if datetime.now() - cached_time < timedelta(seconds=self.config.cache_ttl_seconds):
                return cached_object
            else:
                # Remove expired cache entry
                del self._cache[object_id]
        
        # Try API if enabled
        if self.config.enable_api_fallback:
            api_object = await self._fetch_from_api(object_id)
            if api_object:
                self._cache[object_id] = (api_object, datetime.now())
                return api_object
        
        return None

    async def _fetch_from_api(self, object_id: str) -> Optional[FDKObject]:
        """Fetch object from the SBB FDK API"""
        try:
            url = f"{self.config.api_base_url}/objects/{object_id}"
            params = {"language": self.config.api_language}
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return FDKObject(**data)
            
        except Exception as e:
            self.logger.error(f"API request failed for {object_id}: {e}")
            return None

    async def search_objects(self, criteria: FDKSearchCriteria) -> FDKSearchResult:
        """Search for FDK objects based on criteria"""
        await self.initialize()
        
        matching_objects = []
        
        for obj in self._objects.values():
            if self._matches_criteria(obj, criteria):
                matching_objects.append(obj)
        
        # Sort by ID for consistent results
        matching_objects.sort(key=lambda x: x.id)
        
        # Apply limit
        if criteria.limit > 0:
            matching_objects = matching_objects[:criteria.limit]
        
        return FDKSearchResult(
            objects=matching_objects,
            total_count=len(matching_objects),
            search_criteria=criteria
        )

    def _matches_criteria(self, obj: FDKObject, criteria: FDKSearchCriteria) -> bool:
        """Check if an object matches the search criteria"""
        if criteria.object_id and criteria.object_id.upper() != obj.id.upper():
            return False
        
        if criteria.name_pattern:
            pattern = criteria.name_pattern.lower()
            if pattern not in obj.name.lower():
                return False
        
        if criteria.domain and criteria.domain.lower() != obj.domain_name.lower():
            return False
        
        if criteria.object_type and criteria.object_type.upper() != obj.object_type.upper():
            return False
        
        return True

    async def get_all_objects(self) -> List[FDKObject]:
        """Get all loaded FDK objects"""
        await self.initialize()
        return list(self._objects.values())

    async def get_domains(self) -> List[str]:
        """Get all available domains"""
        await self.initialize()
        domains = set()
        for obj in self._objects.values():
            domains.add(obj.domain_name)
        return sorted(list(domains))

    async def get_object_types(self) -> List[str]:
        """Get all available object types"""
        await self.initialize()
        types = set()
        for obj in self._objects.values():
            types.add(obj.object_type)
        return sorted(list(types))

    def extract_object_id_from_filename(self, filename: str) -> Optional[str]:
        """Extract FDK object ID from filename (e.g., OBJ_BR_1_xxx.png -> OBJ_BR_1)"""
        try:
            # Remove file extension
            base_name = Path(filename).stem
            parts = base_name.split("_")
            
            # Look for pattern: OBJ_XX_Y where XX is letters and Y is number
            if len(parts) >= 3 and parts[0] == "OBJ":
                return f"{parts[0]}_{parts[1]}_{parts[2]}"
                
        except Exception as e:
            self.logger.error(f"Error extracting object ID from {filename}: {e}")
        
        return None

    async def analyze_references(self, object_id: str, max_depth: int = 3) -> FDKReferenceAnalysis:
        """Analyze reference relationships for an object"""
        await self.initialize()
        
        analysis = FDKReferenceAnalysis(object_id=object_id)
        
        # Find objects that reference this one (referenced_by)
        for obj in self._objects.values():
            related_ids = obj.get_related_object_ids()
            if object_id in related_ids:
                analysis.referenced_by.append(obj.id)
        
        # Find objects this one references (references_to)
        if object_id in self._objects:
            target_obj = self._objects[object_id]
            analysis.references_to = target_obj.get_related_object_ids()
        
        analysis.reference_count = len(analysis.referenced_by) + len(analysis.references_to)
        
        return analysis

    async def get_reference_network(self, start_object_id: str, max_depth: int = 2) -> Dict[str, FDKReferenceAnalysis]:
        """Get a network of references starting from an object"""
        await self.initialize()
        
        network = {}
        visited = set()
        to_process = [(start_object_id, 0)]
        
        while to_process:
            current_id, depth = to_process.pop(0)
            
            if current_id in visited or depth > max_depth:
                continue
                
            visited.add(current_id)
            analysis = await self.analyze_references(current_id, max_depth)
            analysis.depth_level = depth
            network[current_id] = analysis
            
            # Add related objects to process
            if depth < max_depth:
                for related_id in analysis.references_to + analysis.referenced_by:
                    if related_id not in visited:
                        to_process.append((related_id, depth + 1))
        
        return network

    async def close(self) -> None:
        """Close the data provider and cleanup resources"""
        await self.http_client.aclose()