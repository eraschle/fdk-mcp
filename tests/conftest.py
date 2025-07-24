"""
Pytest configuration and fixtures
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any

import pytest

from src.fdk_mcp import FDKDataProvider, FDKServerConfig


@pytest.fixture
def sample_data_dir() -> Path:
    """Return path to sample data directory"""
    return Path("data/sample")


@pytest.fixture
def test_config(sample_data_dir: Path) -> FDKServerConfig:
    """Create test configuration"""
    return FDKServerConfig(
        data_directory=str(sample_data_dir),
        api_base_url="https://bim-fdk-api.app.sbb.ch",
        api_language="de",
        cache_ttl_seconds=3600,
        enable_api_fallback=False,  # Disable API for tests
        max_search_results=100,
        log_level="DEBUG",
    )


@pytest.fixture
async def data_provider(test_config: FDKServerConfig) -> AsyncGenerator[Any, Any]:
    """Create and initialize a data provider for testing"""
    provider = FDKDataProvider(test_config)
    await provider.initialize()
    yield provider
    await provider.close()


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_fdk_object_data() -> dict:
    """Sample FDK object data for testing"""
    return {
        "id": "OBJ_TEST_1",
        "name": "Test Object",
        "domainName": "Test Domain",
        "description": "A test object for unit testing",
        "structuredDescription": [
            {"type": "paragraph", "content": "This is a test object."}
        ],
        "imageId": "test-image-id",
        "creationTimestamp": "2025-01-01T00:00:00.000Z",
        "componentRelationships": [{"id": "OBJ_TEST_2", "name": "Related Test Object"}],
        "assemblyRelationships": [],
    }
