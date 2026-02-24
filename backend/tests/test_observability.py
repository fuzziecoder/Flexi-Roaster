import asyncio

from backend.api.routes.observability import (
    ObservabilityEventRequest,
    dispatch_observability_event,
    get_observability_integrations,
    prometheus_metrics,
)


def test_observability_integrations_endpoint_contains_required_providers():
    body = asyncio.run(get_observability_integrations())
    assert 'integrations' in body
    assert 'metrics_logs' in body['integrations']
    assert 'ml_monitoring' in body['integrations']
    assert 'alerting' in body['integrations']
    assert 'prometheus' in body['integrations']['metrics_logs']
    assert 'evidently_ai' in body['integrations']['ml_monitoring']
    assert 'pagerduty' in body['integrations']['alerting']


def test_prometheus_scrape_endpoint_exposes_metrics_payload():
    response = asyncio.run(prometheus_metrics())
    assert response.status_code == 200
    assert 'text/plain' in response.media_type


def test_dispatch_ml_monitoring_event_returns_provider_statuses():
    request = ObservabilityEventRequest(
        category='ml_monitoring',
        event_name='drift_detected',
        severity='warning',
        payload={'pipeline_id': 'pipe-1', 'drift_score': 0.18},
    )
    body = asyncio.run(dispatch_observability_event(request))
    assert body['category'] == 'ml_monitoring'
    assert 'evidently_ai' in body['providers']
    assert 'arize_ai' in body['providers']
    assert 'fiddler_ai' in body['providers']
