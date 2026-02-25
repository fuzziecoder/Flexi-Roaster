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


def test_architecture_contains_requested_layers():
    stack = ModernOrchestrationStack()

    architecture = stack.architecture()

    assert architecture["api_layer"]["name"] == "FastAPI"
    assert architecture["orchestration"]["name"] in {"temporal", "airflow"}
    assert architecture["execution"]["name"] == "kubernetes-jobs"
    assert architecture["distributed_compute"]["name"] == "ray"
    assert set(architecture["distributed_compute"]["config"]["alternatives"]) == {"spark", "dask"}
    assert "cockroachdb" in architecture["storage"]["database_alternatives"]
    assert architecture["security"]["authorization"] == "rbac"


def test_submit_execution_returns_envelope():
    stack = ModernOrchestrationStack()

    envelope = stack.submit_execution("pipeline-123", {"run_type": "full"})

    assert envelope["pipeline_id"] == "pipeline-123"
    assert envelope["status"] == "accepted"
    assert any(command["layer"] == "execution" for command in envelope["commands"])
