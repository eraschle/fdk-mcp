"""
Tests for FDK models
"""

from src.fdk_mcp.models import (
    FDKComponentRelationship,
    FDKObject,
    FDKReferenceAnalysis,
    FDKSearchCriteria,
    FDKServerConfig,
)


class TestFDKObject:
    """Test FDK Object model"""

    def test_create_from_dict(self, sample_fdk_object_data):
        """Test creating FDKObject from dictionary"""
        obj = FDKObject(**sample_fdk_object_data)

        assert obj.id == "OBJ_TEST_1"
        assert obj.name == "Test Object"
        assert obj.domain_name == "Test Domain"
        assert obj.description == "A test object for unit testing"
        assert len(obj.component_relationships) == 1
        assert obj.component_relationships[0].id == "OBJ_TEST_2"

    def test_object_type_extraction(self, sample_fdk_object_data):
        """Test object type extraction from ID"""
        obj = FDKObject(**sample_fdk_object_data)
        assert obj.object_type == "TEST"

    def test_object_number_extraction(self, sample_fdk_object_data):
        """Test object number extraction from ID"""
        obj = FDKObject(**sample_fdk_object_data)
        assert obj.object_number == "1"

    def test_get_related_object_ids(self, sample_fdk_object_data):
        """Test getting related object IDs"""
        obj = FDKObject(**sample_fdk_object_data)
        related_ids = obj.get_related_object_ids()
        assert "OBJ_TEST_2" in related_ids

    def test_get_plain_description_with_structured(self, sample_fdk_object_data):
        """Test getting plain description from structured description"""
        obj = FDKObject(**sample_fdk_object_data)
        plain_desc = obj.get_plain_description()
        assert "This is a test object." in plain_desc

    def test_get_plain_description_fallback(self):
        """Test fallback to description when no structured description"""
        data = {
            "id": "OBJ_TEST_1",
            "name": "Test",
            "domainName": "Test",
            "description": "Simple description",
            "structuredDescription": [],
        }
        obj = FDKObject(**data)
        assert obj.get_plain_description() == "Simple description"


class TestFDKSearchCriteria:
    """Test FDK Search Criteria model"""

    def test_default_values(self):
        """Test default values"""
        criteria = FDKSearchCriteria()
        assert criteria.limit == 10
        assert criteria.include_relationships is True
        assert criteria.object_id is None

    def test_custom_values(self):
        """Test custom values"""
        criteria = FDKSearchCriteria(
            object_id="OBJ_FB_1", name_pattern="test", domain="Fahrbahn", limit=5
        )
        assert criteria.object_id == "OBJ_FB_1"
        assert criteria.name_pattern == "test"
        assert criteria.domain == "Fahrbahn"
        assert criteria.limit == 5


class TestFDKReferenceAnalysis:
    """Test FDK Reference Analysis model"""

    def test_create_analysis(self):
        """Test creating reference analysis"""
        analysis = FDKReferenceAnalysis(
            object_id="OBJ_FB_1",
            referenced_by=["OBJ_FB_2"],
            references_to=["OBJ_FB_3", "OBJ_FB_4"],
            reference_count=3,
        )

        assert analysis.object_id == "OBJ_FB_1"
        assert len(analysis.referenced_by) == 1
        assert len(analysis.references_to) == 2
        assert analysis.reference_count == 3
        assert analysis.depth_level == 0  # default


class TestFDKServerConfig:
    """Test FDK Server Configuration model"""

    def test_default_config(self):
        """Test default configuration values"""
        config = FDKServerConfig()
        assert config.data_directory == "data/sample"
        assert config.api_base_url == "https://bim-fdk-api.app.sbb.ch"
        assert config.api_language == "de"
        assert config.cache_ttl_seconds == 3600
        assert config.enable_api_fallback is True
        assert config.log_level == "INFO"

    def test_custom_config(self):
        """Test custom configuration values"""
        config = FDKServerConfig(
            data_directory="/custom/path",
            api_language="en",
            cache_ttl_seconds=7200,
            enable_api_fallback=False,
            log_level="DEBUG",
        )
        assert config.data_directory == "/custom/path"
        assert config.api_language == "en"
        assert config.cache_ttl_seconds == 7200
        assert config.enable_api_fallback is False
        assert config.log_level == "DEBUG"


class TestFDKComponentRelationship:
    """Test FDK Component Relationship model"""

    def test_create_relationship(self):
        """Test creating component relationship"""
        rel = FDKComponentRelationship(id="OBJ_FB_1", name="Gleisrost")
        assert rel.id == "OBJ_FB_1"
        assert rel.name == "Gleisrost"
