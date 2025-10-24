"""SBB API Client - Implements CatalogRepository for SBB FDK."""

import asyncio
from typing import Any, cast

import httpx

from ...domain.entities import CatalogObject
from ...domain.repositories import CatalogResponse
from ...models import LanguageCode
from ..base.exceptions import CatalogError, ObjectNotFoundError
from .sbb_mapper import SbbMapper
from .sbb_models import SbbApiObjectsResponse, SbbDetailObject


class SbbApiClient:
    """SBB FDK API client implementation.

    This implements the CatalogRepository protocol for the SBB FDK API.
    It handles SBB-specific API calls and uses SbbMapper to convert
    SBB data structures to domain entities.
    """

    def __init__(
        self,
        base_url: str = "https://bim-fdk-api.app.sbb.ch",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize SBB API client.

        Args:
            base_url: Base URL for SBB FDK API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.mapper = SbbMapper()

    async def _request_with_retry(self, url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        """Make API request with retry logic.

        Args:
            url: URL to request
            params: Optional query parameters

        Returns:
            JSON response as dictionary

        Raises:
            CatalogError: On HTTP errors after retries
            ObjectNotFoundError: On 404 errors
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=self.timeout)
                    response.raise_for_status()
                    return response.json()

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 404:
                    # 404 is not retryable
                    raise ObjectNotFoundError(url) from e

                # Retry on other errors
                if attempt < self.max_retries - 1:
                    backoff_delay = self.retry_delay * (2**attempt)
                    await asyncio.sleep(backoff_delay)

            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        # All retries failed
        raise CatalogError(f"API request failed after {self.max_retries} attempts") from last_error

    async def fetch_all_objects(self, language: LanguageCode = "de") -> CatalogResponse:
        """Fetch all objects from SBB FDK API.

        Args:
            language: Language code (de/fr/it/en)

        Returns:
            CatalogResponse with domain objects

        Raises:
            CatalogError: On API errors
        """
        url = f"{self.base_url}/objects"
        params = {"language": language}

        sbb_response = await self._request_with_retry(url, params)
        sbb_typed = cast(SbbApiObjectsResponse, sbb_response)

        # Use mapper to convert SBB response to domain response
        return self.mapper.map_api_response(sbb_typed)

    async def fetch_object_by_id(self, object_id: str, language: LanguageCode = "de") -> CatalogObject:
        """Fetch specific object from SBB FDK API.

        Args:
            object_id: SBB object ID (e.g., "OBJ_BR_1")
            language: Language code (de/fr/it/en)

        Returns:
            Domain CatalogObject with full details

        Raises:
            ObjectNotFoundError: If object doesn't exist
            CatalogError: On API errors
        """
        url = f"{self.base_url}/objects/{object_id}"
        params = {"language": language}

        sbb_response = await self._request_with_retry(url, params)
        sbb_detail = cast(SbbDetailObject, sbb_response)

        # Use mapper to convert SBB detail to domain object
        return self.mapper.map_detail_to_catalog_object(sbb_detail)

    def get_supported_languages(self) -> list[str]:
        """Get SBB FDK supported languages.

        Returns:
            List of language codes
        """
        return ["de", "fr", "it", "en"]
