from __future__ import annotations

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.pubsub import RedisSubscriber
from config import Settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/tasks/{task_id}/progress")
async def task_progress_ws(websocket: WebSocket, task_id: str) -> None:
    await websocket.accept()

    settings = Settings()
    subscriber = RedisSubscriber(settings.redis_url)
    channel = f"task:{task_id}:events"

    try:
        await subscriber.subscribe(channel)

        async for message in subscriber.listen():
            await websocket.send_json(message)

            msg_type = message.get("type")
            if msg_type in ("task_completed", "task_failed"):
                break

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected for task %s", task_id)
    except Exception:
        logger.exception("WebSocket error for task %s", task_id)
    finally:
        await subscriber.unsubscribe(channel)
        await subscriber.close()
