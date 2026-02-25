from backend.events.publisher import EventPublisher


class _StubFuture:
    pass


class _StubProducer:
    def __init__(self, *args, **kwargs):
        self.sent = []

    def send(self, topic, key=None, value=None):
        self.sent.append({"topic": topic, "key": key, "value": value})
        return _StubFuture()

    def flush(self, timeout=None):
        return None


def test_publish_adds_stream_backend(monkeypatch):
    monkeypatch.setattr("backend.events.publisher.KafkaProducer", _StubProducer)
    monkeypatch.setattr("backend.events.publisher.settings.ENABLE_EVENT_STREAMING", True)
    monkeypatch.setattr("backend.events.publisher.settings.EVENT_STREAM_BACKEND", "redpanda")

    publisher = EventPublisher()
    publisher.publish("pipeline.created", "pipeline-1", {"id": "pipeline-1"})

    sent = publisher._producer.sent  # type: ignore[attr-defined]
    assert sent[0]["topic"] == "pipeline.created"
    assert sent[0]["value"]["stream_backend"] == "redpanda"


def test_publish_noop_when_streaming_disabled(monkeypatch):
    monkeypatch.setattr("backend.events.publisher.settings.ENABLE_EVENT_STREAMING", False)
    publisher = EventPublisher()
    publisher.publish("execution.started", "execution-1", {"id": "execution-1"})

    assert publisher._producer is None
