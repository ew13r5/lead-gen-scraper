from __future__ import annotations

import json
import logging
from typing import AsyncIterator

import redis
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class RedisPublisher:
    """Sync Redis publisher for Celery tasks."""

    def __init__(self, redis_url: str) -> None:
        self._redis = redis.Redis.from_url(redis_url)

    def publish(self, channel: str, message: dict) -> None:
        self._redis.publish(channel, json.dumps(message))


class RedisSubscriber:
    """Async Redis subscriber for WebSocket endpoints."""

    def __init__(self, redis_url: str) -> None:
        self._redis = aioredis.from_url(redis_url)
        self._pubsub = self._redis.pubsub()

    async def subscribe(self, channel: str) -> None:
        await self._pubsub.subscribe(channel)

    async def listen(self) -> AsyncIterator[dict]:
        async for message in self._pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    yield data
                except (json.JSONDecodeError, TypeError):
                    logger.warning("Invalid JSON in pub/sub message")

    async def unsubscribe(self, channel: str) -> None:
        await self._pubsub.unsubscribe(channel)

    async def close(self) -> None:
        await self._pubsub.close()
        await self._redis.close()
