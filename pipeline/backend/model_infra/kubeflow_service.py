"""Kubeflow pipeline compilation and run submission helpers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from config import settings


@dataclass
class KubeflowService:
    """Minimal orchestration service for Kubeflow Pipelines."""

    host: str = "http://localhost:3000"

    def compile_pipeline(self, module_path: str, function_name: str, output_path: str) -> Dict[str, Any]:
        """Compile a Python KFP pipeline function into YAML."""
        try:
            import importlib.util
            from kfp import compiler  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Kubeflow Pipelines SDK is not installed. Install with `pip install kfp` to compile pipelines."
            ) from exc

        spec = importlib.util.spec_from_file_location("flexiroaster_kfp_module", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load module from path: {module_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        pipeline_fn = getattr(module, function_name, None)
        if pipeline_fn is None:
            raise RuntimeError(f"Pipeline function `{function_name}` was not found in `{module_path}`")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        compiler.Compiler().compile(pipeline_func=pipeline_fn, package_path=str(output))

        return {
            "status": "compiled",
            "pipeline_function": function_name,
            "module_path": module_path,
            "output_path": str(output),
        }

    def submit_run(self, pipeline_package_path: str, run_name: str, experiment_name: str) -> Dict[str, Any]:
        """Submit a compiled pipeline package to Kubeflow Pipelines."""
        try:
            from kfp import Client  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Kubeflow Pipelines SDK is not installed. Install with `pip install kfp` to submit runs."
            ) from exc

        client = Client(host=self.host)
        experiment = client.create_experiment(name=experiment_name)
        run = client.run_pipeline(
            experiment_id=experiment.experiment_id,
            job_name=run_name,
            pipeline_package_path=pipeline_package_path,
        )

        return {
            "status": "submitted",
            "run_id": run.run_id,
            "run_name": run_name,
            "experiment_name": experiment_name,
            "host": self.host,
        }


kubeflow_service = KubeflowService(host=settings.KUBEFLOW_HOST)
