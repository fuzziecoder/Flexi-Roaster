"""Kafka-backed event publisher with graceful fallback for local/dev environments."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
import json
import logging

from backend.config import settings

logger = logging.getLogger(__name__)

try:
    from kafka import KafkaProducer  # type: ignore
except ImportError:  # pragma: no cover - optional dependency at runtime
    KafkaProducer = None


class EventPublisher:
    """Publish domain events for pipelines and executions."""

    def __init__(self):
        self._producer: Optional[Any] = None

    @property
    def enabled(self) -> bool:
        """Whether event streaming is enabled in config."""
        return settings.ENABLE_EVENT_STREAMING

    def _ensure_producer(self) -> Optional[Any]:
        if not self.enabled:
            return None

        if self._producer is not None:
            return self._producer

        if KafkaProducer is None:
            logger.warning("Event streaming enabled but kafka-python is not installed.")
            return None

        try:
            self._producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=settings.KAFKA_CLIENT_ID,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                key_serializer=lambda value: value.encode("utf-8") if value else None,
            )
            return self._producer
        except Exception as exc:  # pragma: no cover - depends on external broker
            logger.warning("Failed to initialize Kafka producer: %s", exc)
            return None

    def publish(self, topic: str, key: Optional[str], payload: Dict[str, Any]) -> None:
        """Publish a single event with standard envelope metadata."""
        event = {
            "event_type": topic,
            "published_at": datetime.now().isoformat(),
            "payload": payload,
        }

        producer = self._ensure_producer()
        if producer is None:
            logger.info("[event-fallback] topic=%s key=%s payload=%s", topic, key, event)
            return

        try:
            producer.send(topic, key=key, value=event)
            producer.flush(timeout=2)
        except Exception as exc:  # pragma: no cover - depends on external broker
            logger.warning("Failed publishing event topic=%s key=%s error=%s", topic, key, exc)


_event_publisher = EventPublisher()


def get_event_publisher() -> EventPublisher:
    """Return singleton event publisher."""
    return _event_publisher
