"""
Thin synchronous and asynchronous clients for the Voyage AI embeddings REST API.

Uses httpx (already in requirements) instead of the voyageai SDK,
which is incompatible with Python 3.14.
"""

import asyncio
import time

import httpx

_BASE_URL = "https://api.voyageai.com/v1"
_MAX_RETRIES = 6
_RETRY_BASE = 15.0  # seconds; doubles each attempt


def _retry_delay(attempt: int) -> float:
    return min(_RETRY_BASE * (2 ** attempt), 120.0)


class VoyageClient:
    """Synchronous Voyage AI client for use in scripts and the indexer."""

    def __init__(self, api_key: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def embed(self, inputs: list[str], model: str, input_type: str) -> list[list[float]]:
        for attempt in range(_MAX_RETRIES):
            response = httpx.post(
                f"{_BASE_URL}/embeddings",
                headers=self._headers,
                json={"input": inputs, "model": model, "input_type": input_type},
                timeout=120.0,
            )
            if response.status_code == 429 and attempt < _MAX_RETRIES - 1:
                delay = _retry_delay(attempt)
                time.sleep(delay)
                continue
            response.raise_for_status()
            return [item["embedding"] for item in response.json()["data"]]
        response.raise_for_status()  # final attempt failed
        return []  # unreachable


class AsyncVoyageClient:
    """Async Voyage AI client for use in FastAPI route handlers."""

    def __init__(self, api_key: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def embed(self, inputs: list[str], model: str, input_type: str) -> list[list[float]]:
        for attempt in range(_MAX_RETRIES):
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{_BASE_URL}/embeddings",
                    headers=self._headers,
                    json={"input": inputs, "model": model, "input_type": input_type},
                )
            if response.status_code == 429 and attempt < _MAX_RETRIES - 1:
                await asyncio.sleep(_retry_delay(attempt))
                continue
            response.raise_for_status()
            return [item["embedding"] for item in response.json()["data"]]
        response.raise_for_status()
        return []  # unreachable
