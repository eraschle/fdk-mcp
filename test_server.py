#!/usr/bin/env python3
"""
Simple test script for FDK MCP Server
"""

import asyncio
import json
from src.fdk_mcp import FDKDataProvider, FDKServerConfig, FDKSearchCriteria


async def test_data_provider():
    """Test the FDK data provider functionality"""
    print("=== Testing FDK Data Provider ===")
    
    config = FDKServerConfig(data_directory='data/sample')
    provider = FDKDataProvider(config)
    
    try:
        await provider.initialize()
        
        # Test 1: Get all objects
        objects = await provider.get_all_objects()
        print(f"\n1. Loaded {len(objects)} objects:")
        for obj in objects:
            print(f"   - {obj.id}: {obj.name} ({obj.domain_name})")
        
        # Test 2: Get specific object
        obj = await provider.get_object("OBJ_FB_1")
        if obj:
            print(f"\n2. Retrieved object: {obj.id} - {obj.name}")
            print(f"   Description: {obj.description[:100]}...")
        
        # Test 3: Search objects
        criteria = FDKSearchCriteria(name_pattern="Wand", limit=5)
        result = await provider.search_objects(criteria)
        print(f"\n3. Search for 'Wand' found {result.total_count} objects:")
        for obj in result.objects:
            print(f"   - {obj.id}: {obj.name}")
        
        # Test 4: Reference analysis
        analysis = await provider.analyze_references("OBJ_FB_1")
        print(f"\n4. Reference analysis for {analysis.object_id}:")
        print(f"   References to {len(analysis.references_to)} objects")
        print(f"   Referenced by {len(analysis.referenced_by)} objects")
        
        # Test 5: Get domains and types
        domains = await provider.get_domains()
        types = await provider.get_object_types()
        print(f"\n5. Available domains: {domains}")
        print(f"   Available types: {types}")
        
        print("\n=== All tests passed! ===")
        
    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(test_data_provider())