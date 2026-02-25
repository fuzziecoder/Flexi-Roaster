from core.enterprise_orchestration import (
    AutoScalingAdvisor,
    DependencyGraphOptimizer,
    DynamicDAGGenerator,
    SLAMonitor,
)


def test_dynamic_dag_generation_from_metadata():
    metadata = {
        "stages": [
            {"id": "extract", "intent": "extract"},
            {"id": "transform", "intent": "transform"},
            {"id": "load", "intent": "load"},
        ]
    }

    spec = DynamicDAGGenerator().generate(metadata)

    assert len(spec.stages) == 3
    assert spec.stages[0]["type"] == "input"
    assert spec.stages[1]["dependencies"] == ["extract"]
    assert spec.parallel_groups == [["extract"], ["transform"], ["load"]]


def test_dependency_optimizer_parallel_groups():
    stages = [
        {"id": "a", "dependencies": []},
        {"id": "b", "dependencies": ["a"]},
        {"id": "c", "dependencies": ["a"]},
        {"id": "d", "dependencies": ["b", "c"]},
    ]

    spec = DependencyGraphOptimizer().optimize(stages)

    assert spec.parallel_groups == [["a"], ["b", "c"], ["d"]]


def test_sla_monitor_alerts_when_threshold_exceeded():
    monitor = SLAMonitor()

    alert = monitor.evaluate_stage(
        execution_id="exec-1",
        pipeline_id="pipe-1",
        stage_id="stage-1",
        duration_seconds=15,
        threshold_seconds=10,
    )

    assert alert is not None
    assert alert["event"] == "sla_violation"


def test_auto_scaling_recommends_scale_up():
    recommendation = AutoScalingAdvisor().recommend_workers(queue_size=40, active_workers=2)

    assert recommendation["recommended_workers"] >= 3
    assert recommendation["scale_action"] == "up"
