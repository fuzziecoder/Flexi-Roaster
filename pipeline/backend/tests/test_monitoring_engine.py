from ai.monitoring_engine import ExecutionSignal, PipelineMonitoringEngine


def test_monitoring_snapshot_detects_patterns_and_spikes():
    engine = PipelineMonitoringEngine(window_minutes=60)

    for index in range(6):
        engine.ingest(
            ExecutionSignal(
                execution_id=f"exe-{index}",
                pipeline_id="pipe-1",
                status="failed" if index in (1, 5) else "completed",
                duration_seconds=20 + index,
                stage_failures=1 if index in (1, 5) else 0,
                retry_count=2 if index == 5 else 0,
                throughput_per_minute=100 if index < 5 else 40,
                latency_ms=200 if index < 5 else 900,
                cpu_percent=55 + index,
                memory_percent=45 + index,
                error_message="timeout" if index in (1, 5) else None,
            )
        )

    snapshot = engine.build_snapshot("pipe-1")

    assert snapshot.sampled_events == 6
    assert snapshot.failure_rate > 0
    assert snapshot.retry_frequency > 0
    assert snapshot.throughput_drop_detected is True
    assert snapshot.latency_spike_detected is True
    assert snapshot.dominant_error_patterns[0]["pattern"] == "timeout"
