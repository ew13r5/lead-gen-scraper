from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from api.pubsub import RedisPublisher


class TestRedisPublisher:
    @patch("api.pubsub.redis")
    def test_publish_sends_json(self, mock_redis_mod):
        mock_conn = MagicMock()
        mock_redis_mod.Redis.from_url.return_value = mock_conn

        pub = RedisPublisher("redis://localhost:6379/0")
        pub.publish("test:channel", {"type": "progress", "value": 42})

        mock_conn.publish.assert_called_once()
        channel, data = mock_conn.publish.call_args[0]
        assert channel == "test:channel"
        parsed = json.loads(data)
        assert parsed["type"] == "progress"
        assert parsed["value"] == 42

    @patch("api.pubsub.redis")
    def test_publish_serializes_nested(self, mock_redis_mod):
        mock_conn = MagicMock()
        mock_redis_mod.Redis.from_url.return_value = mock_conn

        pub = RedisPublisher("redis://localhost:6379/0")
        pub.publish("ch", {"nested": {"key": "val"}})

        data = json.loads(mock_conn.publish.call_args[0][1])
        assert data["nested"]["key"] == "val"
