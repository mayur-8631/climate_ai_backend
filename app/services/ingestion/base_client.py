import httpx
from typing import Any, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import DataIngestionError


class ResilientHTTPClient:
    """Async HTTP client with exponential backoff and timeout handling."""

    def __init__(self, timeout_seconds: float = settings.REQUEST_TIMEOUT_SECONDS):
        self.timeout = timeout_seconds

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Status Error ({e.response.status_code}) fetching {url}: {e.response.text}")
                raise DataIngestionError(f"API returned status {e.response.status_code}", details=e.response.text)
            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.warning(f"Connection error fetching {url} (will retry): {str(e)}")
                raise

