"""
Redis dependency for FastAPI.

Provides async Redis client for caching.
"""

from collections.abc import AsyncGenerator

import redis.asyncio as redis

from api.config import settings


async def get_redis() -> AsyncGenerator[redis.Redis]:
    """
    Get async Redis client.

    Yields:
        Redis client instance
    """
    client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.close()
