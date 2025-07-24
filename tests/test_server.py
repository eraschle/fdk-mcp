"""
Tests for FDK MCP Server
"""

import json

import pytest

from src.fdk_mcp.server import FDKMCPServer


class TestFDKMCPServer:
    """Test FDK MCP Server"""

    @pytest.fixture
    async def server(self, test_config):
        """Create server for testing"""
        server = FDKMCPServer(test_config)
        await server.run()
        yield server
        await server.cleanup()

    async def test_server_initialization(self, test_config):
        """Test server initialization"""
        server = FDKMCPServer(test_config)
        assert server.config == test_config
        assert server.server is not None
        assert server.data_provider is not None

    async def test_handle_get_fdk_object_valid(self, server):
        """Test getting a valid FDK object"""
        arguments = {"object_id": "OBJ_FB_1"}
        result = await server._handle_get_fdk_object(arguments)

        assert result.content is not None
        assert len(result.content) == 1

        # Parse the JSON response
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert response_data["id"] == "OBJ_FB_1"
        assert response_data["name"] == "Gleisrost"
        assert response_data["domain"] == "Fahrbahn"
        assert "description" in response_data

    async def test_handle_get_fdk_object_invalid(self, server):
        """Test getting an invalid FDK object"""
        arguments = {"object_id": "OBJ_NONEXISTENT_999"}
        result = await server._handle_get_fdk_object(arguments)

        assert result.content is not None
        assert "Object not found" in result.content[0].text

    async def test_handle_get_fdk_object_missing_id(self, server):
        """Test getting FDK object without ID"""
        arguments = {}
        result = await server._handle_get_fdk_object(arguments)

        assert result.content is not None
        assert "object_id is required" in result.content[0].text

    async def test_handle_search_fdk_objects(self, server):
        """Test searching FDK objects"""
        arguments = {"name_pattern": "Gleisrost", "limit": 5}
        result = await server._handle_search_fdk_objects(arguments)

        assert result.content is not None
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert "total_count" in response_data
        assert "objects" in response_data
        assert response_data["total_count"] >= 1

    async def test_handle_extract_object_id_valid(self, server):
        """Test extracting object ID from valid filename"""
        arguments = {"filename": "OBJ_BR_1_Ansicht.png"}
        result = await server._handle_extract_object_id(arguments)

        assert result.content is not None
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert response_data["filename"] == "OBJ_BR_1_Ansicht.png"
        assert response_data["extracted_object_id"] == "OBJ_BR_1"
        assert response_data["success"] is True

    async def test_handle_extract_object_id_invalid(self, server):
        """Test extracting object ID from invalid filename"""
        arguments = {"filename": "invalid_filename.png"}
        result = await server._handle_extract_object_id(arguments)

        assert result.content is not None
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert response_data["extracted_object_id"] is None

    async def test_handle_analyze_references(self, server):
        """Test analyzing references"""
        arguments = {"object_id": "OBJ_FB_1", "max_depth": 2}
        result = await server._handle_analyze_references(arguments)

        assert result.content is not None
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert response_data["object_id"] == "OBJ_FB_1"
        assert "referenced_by" in response_data
        assert "references_to" in response_data
        assert "reference_count" in response_data

    async def test_handle_get_reference_network(self, server):
        """Test getting reference network"""
        arguments = {"start_object_id": "OBJ_FB_1", "max_depth": 1}
        result = await server._handle_get_reference_network(arguments)

        assert result.content is not None
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert response_data["start_object_id"] == "OBJ_FB_1"
        assert response_data["max_depth"] == 1
        assert "network" in response_data
        assert "OBJ_FB_1" in response_data["network"]

    async def test_handle_get_domains(self, server):
        """Test getting domains"""
        arguments = {}
        result = await server._handle_get_domains(arguments)

        assert result.content is not None
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert "domains" in response_data
        assert "count" in response_data
        assert isinstance(response_data["domains"], list)
        assert response_data["count"] > 0

    async def test_handle_get_object_types(self, server):
        """Test getting object types"""
        arguments = {}
        result = await server._handle_get_object_types(arguments)

        assert result.content is not None
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert "object_types" in response_data
        assert "count" in response_data
        assert isinstance(response_data["object_types"], list)
        assert response_data["count"] > 0

    async def test_handle_get_all_objects_summary(self, server):
        """Test getting all objects in summary mode"""
        arguments = {"summary_only": True}
        result = await server._handle_get_all_objects(arguments)

        assert result.content is not None
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert "total_count" in response_data
        assert "objects" in response_data
        assert response_data["total_count"] > 0

        # Check that objects have summary fields only
        if response_data["objects"]:
            first_obj = response_data["objects"][0]
            expected_fields = {"id", "name", "domain", "object_type"}
            assert set(first_obj.keys()) == expected_fields

    async def test_handle_get_all_objects_full(self, server):
        """Test getting all objects in full mode"""
        arguments = {"summary_only": False}
        result = await server._handle_get_all_objects(arguments)

        assert result.content is not None
        response_text = result.content[0].text
        response_data = json.loads(response_text)

        assert "total_count" in response_data
        assert "objects" in response_data

        # Check that objects have full data
        if response_data["objects"]:
            first_obj = response_data["objects"][0]
            assert "id" in first_obj
            assert "description" in first_obj
            # Should have more fields than summary


class TestFDKMCPServerErrorHandling:
    """Test error handling in MCP Server"""

    async def test_handle_invalid_tool_call(self, test_config):
        """Test handling invalid tool calls"""
        server = FDKMCPServer(test_config)
        await server.run()

        # Test with a mock handler call that should trigger unknown tool error
        # We'll simulate this by directly testing the error path

        # Since the handler is registered as a decorator, we can't easily test
        # the unknown tool path directly. Instead, test with invalid arguments.
        result = await server._handle_analyze_references({"invalid_arg": "test"})

        assert result.content is not None
        assert "object_id is required" in result.content[0].text  # pyright: ignore[reportAttributeAccessIssue]

        await server.cleanup()

    async def test_handle_missing_required_argument(self, test_config):
        """Test handling missing required arguments"""
        server = FDKMCPServer(test_config)
        await server.run()

        # Test missing object_id for analyze_references
        arguments = {"max_depth": 3}  # missing object_id
        result = await server._handle_analyze_references(arguments)

        assert result.content is not None
        assert "object_id is required" in result.content[0].text  # pyright: ignore[reportAttributeAccessIssue]

        await server.cleanup()
