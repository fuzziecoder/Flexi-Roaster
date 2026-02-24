from microservices import MicroserviceOrchestrator


def test_architecture_contains_required_services():
    orchestrator = MicroserviceOrchestrator()
    services = orchestrator.architecture()
    names = {item["name"] for item in services}

    assert names == {
        "pipeline-service",
        "execution-service",
        "ai-insights-service",
        "metrics-service",
        "notification-service",
    }


def test_unknown_service_raises_value_error():
    orchestrator = MicroserviceOrchestrator()

    try:
        orchestrator._require_service("unknown-service")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Unknown service" in str(exc)
