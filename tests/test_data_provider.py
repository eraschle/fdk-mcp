"""
Tests for FDK Data Provider
"""

from unittest.mock import patch

from src.fdk_mcp.data_provider import FDKDataProvider
from src.fdk_mcp.models import FDKSearchCriteria, FDKServerConfig


class TestFDKDataProvider:
    """Test FDK Data Provider"""

    async def test_initialize_loads_json_files(self, test_config, sample_data_dir):
        """Test that initialization loads JSON files"""
        provider = FDKDataProvider(test_config)
        await provider.initialize()

        objects = await provider.get_all_objects()
        assert len(objects) > 0  # Should load sample data

        # Check that we have the expected sample objects
        object_ids = [obj.id for obj in objects]
        assert "OBJ_FB_1" in object_ids
        assert "OBJ_HB_015" in object_ids

        await provider.close()

    async def test_get_object_existing(self, data_provider):
        """Test getting an existing object"""
        obj = await data_provider.get_object("OBJ_FB_1")
        assert obj is not None
        assert obj.id == "OBJ_FB_1"
        assert obj.name == "Gleisrost"
        assert obj.domain_name == "Fahrbahn"

    async def test_get_object_nonexistent(self, data_provider):
        """Test getting a non-existent object"""
        obj = await data_provider.get_object("OBJ_NONEXISTENT_999")
        assert obj is None

    async def test_search_objects_by_name(self, data_provider):
        """Test searching objects by name pattern"""
        criteria = FDKSearchCriteria(name_pattern="Wand")
        result = await data_provider.search_objects(criteria)

        assert result.total_count == 1
        assert len(result.objects) == 1
        assert result.objects[0].name == "Wand"

    async def test_search_objects_by_domain(self, data_provider):
        """Test searching objects by domain"""
        criteria = FDKSearchCriteria(domain="Fahrbahn")
        result = await data_provider.search_objects(criteria)

        assert result.total_count >= 1
        for obj in result.objects:
            assert obj.domain_name == "Fahrbahn"

    async def test_search_objects_by_type(self, data_provider):
        """Test searching objects by object type"""
        criteria = FDKSearchCriteria(object_type="FB")
        result = await data_provider.search_objects(criteria)

        assert result.total_count >= 1
        for obj in result.objects:
            assert obj.object_type == "FB"

    async def test_search_objects_with_limit(self, data_provider):
        """Test search with limit"""
        criteria = FDKSearchCriteria(limit=2)
        result = await data_provider.search_objects(criteria)

        assert len(result.objects) <= 2

    async def test_get_domains(self, data_provider):
        """Test getting all domains"""
        domains = await data_provider.get_domains()
        assert isinstance(domains, list)
        assert len(domains) > 0
        assert "Fahrbahn" in domains
        assert "Hochbau" in domains

    async def test_get_object_types(self, data_provider):
        """Test getting all object types"""
        types = await data_provider.get_object_types()
        assert isinstance(types, list)
        assert len(types) > 0
        assert "FB" in types
        assert "HB" in types

    def test_extract_object_id_from_filename(self, data_provider):
        """Test extracting object ID from filename"""
        # Test valid filename
        object_id = data_provider.extract_object_id_from_filename(
            "OBJ_BR_1_Ansicht.png"
        )
        assert object_id == "OBJ_BR_1"

        # Test another valid filename
        object_id = data_provider.extract_object_id_from_filename(
            "OBJ_FB_23_Detail.jpg"
        )
        assert object_id == "OBJ_FB_23"

        # Test invalid filename
        object_id = data_provider.extract_object_id_from_filename(
            "invalid_filename.png"
        )
        assert object_id is None

    async def test_analyze_references(self, data_provider):
        """Test reference analysis"""
        analysis = await data_provider.analyze_references("OBJ_FB_1")

        assert analysis.object_id == "OBJ_FB_1"
        assert isinstance(analysis.referenced_by, list)
        assert isinstance(analysis.references_to, list)
        assert analysis.reference_count >= 0

    async def test_get_reference_network(self, data_provider):
        """Test getting reference network"""
        network = await data_provider.get_reference_network("OBJ_FB_1", max_depth=1)

        assert isinstance(network, dict)
        assert "OBJ_FB_1" in network

        # Check that the starting object has depth 0
        assert network["OBJ_FB_1"].depth_level == 0

    @patch("httpx.AsyncClient.get")
    async def test_api_fallback_disabled(self, mock_get, test_config):
        """Test that API fallback is disabled in test config"""
        # Ensure API fallback is disabled
        test_config.enable_api_fallback = False
        provider = FDKDataProvider(test_config)
        await provider.initialize()

        # Try to get a non-existent object
        obj = await provider.get_object("OBJ_NONEXISTENT_999")
        assert obj is None

        # Verify no API call was made
        mock_get.assert_not_called()

        await provider.close()

    async def test_matches_criteria(self, data_provider):
        """Test the _matches_criteria method"""
        # Get a sample object
        objects = await data_provider.get_all_objects()
        sample_obj = objects[0]

        # Test exact ID match
        criteria = FDKSearchCriteria(object_id=sample_obj.id)
        assert data_provider._matches_criteria(sample_obj, criteria)

        # Test case insensitive ID match
        criteria = FDKSearchCriteria(object_id=sample_obj.id.lower())
        assert data_provider._matches_criteria(sample_obj, criteria)

        # Test name pattern match
        criteria = FDKSearchCriteria(name_pattern=sample_obj.name[:3])
        assert data_provider._matches_criteria(sample_obj, criteria)

        # Test domain match
        criteria = FDKSearchCriteria(domain=sample_obj.domain_name)
        assert data_provider._matches_criteria(sample_obj, criteria)

        # Test object type match
        criteria = FDKSearchCriteria(object_type=sample_obj.object_type)
        assert data_provider._matches_criteria(sample_obj, criteria)

        # Test no match
        criteria = FDKSearchCriteria(object_id="NONEXISTENT")
        assert not data_provider._matches_criteria(sample_obj, criteria)


class TestFDKDataProviderErrorHandling:
    """Test error handling in FDK Data Provider"""

    async def test_missing_data_directory(self):
        """Test handling of missing data directory"""
        config = FDKServerConfig(data_directory="/nonexistent/path")
        provider = FDKDataProvider(config)

        # Should not raise exception
        await provider.initialize()

        # Should return empty list
        objects = await provider.get_all_objects()
        assert len(objects) == 0

        await provider.close()

    async def test_invalid_json_file(self, tmp_path, test_config):
        """Test handling of invalid JSON files"""
        # Create a temporary directory with invalid JSON
        invalid_json_file = tmp_path / "invalid.json"
        invalid_json_file.write_text('{"invalid": json}')

        # Update config to use temp directory
        config = FDKServerConfig(data_directory=str(tmp_path))
        provider = FDKDataProvider(config)

        # Should not raise exception
        await provider.initialize()

        # Should return empty list (invalid file ignored)
        objects = await provider.get_all_objects()
        assert len(objects) == 0

        await provider.close()
