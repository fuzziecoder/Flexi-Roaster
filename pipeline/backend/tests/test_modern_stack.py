from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


module_path = Path(__file__).resolve().parents[1] / "core" / "modern_stack.py"
spec = spec_from_file_location("modern_stack", module_path)
modern_stack = module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = modern_stack
spec.loader.exec_module(modern_stack)
ModernOrchestrationStack = modern_stack.ModernOrchestrationStack
settings = modern_stack.settings


def test_architecture_contains_requested_layers():
    stack = ModernOrchestrationStack()

    architecture = stack.architecture()

    assert architecture["api_layer"]["name"] == "FastAPI"
    assert architecture["orchestration"]["name"] in {"temporal", "airflow"}
    assert architecture["execution"]["name"] == "kubernetes-jobs"
    assert architecture["distributed_compute"]["name"] in {"ray", "spark", "dask", "celery"}
    assert architecture["security"]["authorization"] == "rbac"


def test_submit_execution_returns_envelope():
    stack = ModernOrchestrationStack()

    envelope = stack.submit_execution("pipeline-123", {"run_type": "full"})

    assert envelope["pipeline_id"] == "pipeline-123"
    assert envelope["status"] == "accepted"
    assert any(command["layer"] == "execution" for command in envelope["commands"])


def test_architecture_supports_pulsar_spark_and_cockroachdb(monkeypatch):
    monkeypatch.setattr(settings, "EVENT_BACKEND", "pulsar")
    monkeypatch.setattr(settings, "PULSAR_ENABLED", True)
    monkeypatch.setattr(settings, "DISTRIBUTED_COMPUTE_BACKEND", "spark")
    monkeypatch.setattr(settings, "SPARK_ENABLED", True)
    monkeypatch.setattr(settings, "DATABASE_BACKEND", "cockroachdb")

    stack = ModernOrchestrationStack()
    architecture = stack.architecture()

    assert architecture["event_layer"]["name"] == "pulsar"
    assert architecture["event_layer"]["config"]["multi_tenant"] is True
    assert architecture["distributed_compute"]["name"] == "spark"
    assert architecture["storage"]["database"]["engine"] == "cockroachdb"


def test_submit_execution_supports_rabbitmq_and_dask(monkeypatch):
    monkeypatch.setattr(settings, "EVENT_BACKEND", "rabbitmq")
    monkeypatch.setattr(settings, "RABBITMQ_ENABLED", True)
    monkeypatch.setattr(settings, "DISTRIBUTED_COMPUTE_BACKEND", "dask")
    monkeypatch.setattr(settings, "DASK_ENABLED", True)

    stack = ModernOrchestrationStack()
    envelope = stack.submit_execution("pipeline-abc", {})

    assert any(
        command["layer"] == "event_layer"
        and command["engine"] == "rabbitmq"
        and command["action"] == "publish_event"
        for command in envelope["commands"]
    )
    assert any(
        command["layer"] == "distributed_compute"
        and command["engine"] == "dask"
        and command["action"] == "submit_dask_job"
        for command in envelope["commands"]
    )
