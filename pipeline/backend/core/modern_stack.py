"""Modern advanced orchestration stack primitives.

Implements a configurable orchestration profile that combines:
- FastAPI API layer
- Airflow/Temporal orchestrators
- Pluggable eventing (Kafka/Pulsar/RabbitMQ/NATS)
- Kubernetes jobs for execution
- Ray/Spark/Dask for distributed compute
- PostgreSQL/CockroachDB/MongoDB/Cassandra + object storage persistence
- Pluggable distributed compute (Ray/Spark/Dask/Celery)
- Pluggable storage (PostgreSQL/CockroachDB/MongoDB/Cassandra) + object storage
- Prometheus/Grafana/ELK observability
- JWT + RBAC + secrets manager security
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from config import settings


@dataclass
class StackComponent:
    name: str
    enabled: bool
    config: Dict[str, Any]


class ModernOrchestrationStack:
    """Service layer for the high-end orchestration stack."""

    def _event_layer(self) -> Dict[str, Any]:
        backend = settings.EVENT_BACKEND.lower()

        if backend == "pulsar":
            return StackComponent(
                name="pulsar",
                enabled=settings.PULSAR_ENABLED,
                config={
                    "service_url": settings.PULSAR_SERVICE_URL,
                    "topic": settings.PULSAR_EXECUTION_TOPIC,
                    "tenant": settings.PULSAR_TENANT,
                    "namespace": settings.PULSAR_NAMESPACE,
                    "geo_replication_regions": settings.PULSAR_GEO_REPLICATION_REGIONS,
                    "multi_tenant": True,
                },
            ).__dict__

        if backend == "rabbitmq":
            return StackComponent(
                name="rabbitmq",
                enabled=settings.RABBITMQ_ENABLED,
                config={
                    "url": settings.RABBITMQ_URL,
                    "exchange": settings.RABBITMQ_EXCHANGE,
                    "queue": settings.RABBITMQ_QUEUE,
                },
            ).__dict__

        if backend == "nats":
            return StackComponent(
                name="nats",
                enabled=settings.NATS_ENABLED,
                config={
                    "servers": settings.NATS_SERVERS,
                    "subject": settings.NATS_SUBJECT,
                },
            ).__dict__

        return StackComponent(
            name="kafka",
            enabled=settings.KAFKA_ENABLED,
            config={
                "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "topic": settings.KAFKA_EXECUTION_TOPIC,
            },
        ).__dict__

    def _distributed_compute(self) -> Dict[str, Any]:
        backend = settings.DISTRIBUTED_COMPUTE_BACKEND.lower()

        if backend == "spark":
            return StackComponent(
                name="spark",
                enabled=settings.SPARK_ENABLED,
                config={
                    "master_url": settings.SPARK_MASTER_URL,
                    "app_name": settings.SPARK_APP_NAME,
                    "supports_batch": True,
                    "supports_streaming": settings.SPARK_STREAMING_ENABLED,
                },
            ).__dict__

        if backend == "dask":
            return StackComponent(
                name="dask",
                enabled=settings.DASK_ENABLED,
                config={
                    "scheduler_address": settings.DASK_SCHEDULER_ADDRESS,
                    "dashboard_url": settings.DASK_DASHBOARD_URL,
                    "python_native": True,
                },
            ).__dict__

        if backend == "celery":
            return StackComponent(
                name="celery",
                enabled=True,
                config={
                    "broker_url": settings.CELERY_BROKER_URL,
                    "result_backend": settings.CELERY_RESULT_BACKEND,
                    "task_queue": settings.CELERY_TASK_QUEUE,
                },
            ).__dict__

        return StackComponent(
            name="ray",
            enabled=settings.RAY_ENABLED,
            config={
                "dashboard_url": settings.RAY_DASHBOARD_URL,
                "entrypoint": settings.RAY_JOB_ENTRYPOINT,
            },
        ).__dict__

    def _storage(self) -> Dict[str, Any]:
        backend = settings.DATABASE_BACKEND.lower()
        database_config: Dict[str, Any]

        if backend == "cockroachdb":
            database_config = {
                "engine": "cockroachdb",
                "url": settings.COCKROACHDB_URL,
                "strong_consistency": True,
                "high_availability": True,
            }
        elif backend == "mongodb":
            database_config = {
                "engine": "mongodb",
                "url": settings.MONGODB_URL,
                "flexible_schema": True,
            }
        elif backend == "cassandra":
            database_config = {
                "engine": "cassandra",
                "contact_points": settings.CASSANDRA_CONTACT_POINTS,
                "keyspace": settings.CASSANDRA_KEYSPACE,
                "high_write_workloads": True,
            }
        else:
            database_config = {
                "engine": "postgresql",
                "url": settings.DATABASE_URL,
            }

        return {
            "database": database_config,
            "object_storage": {
                "enabled": settings.OBJECT_STORAGE_ENABLED,
                "bucket": settings.OBJECT_STORAGE_BUCKET,
                "endpoint": settings.OBJECT_STORAGE_ENDPOINT,
            },
        }

    def architecture(self) -> Dict[str, Any]:
        """Return stack topology and active configuration."""
        return {
            "api_layer": StackComponent(
                name="FastAPI",
                enabled=True,
                config={"base_path": settings.API_PREFIX},
            ).__dict__,
            "orchestration": StackComponent(
                name=settings.ORCHESTRATION_ENGINE,
                enabled=True,
                config={
                    "temporal_enabled": settings.TEMPORAL_ENABLED,
                    "temporal_address": settings.TEMPORAL_ADDRESS,
                    "namespace": settings.TEMPORAL_NAMESPACE,
                    "task_queue": settings.TEMPORAL_TASK_QUEUE,
                },
            ).__dict__,
            "event_layer": self._event_layer(),
            "execution": StackComponent(
                name="kubernetes-jobs",
                enabled=True,
                config={
                    "namespace": settings.KUBERNETES_NAMESPACE,
                    "default_image": settings.KUBERNETES_JOB_IMAGE,
                    "service_account": settings.KUBERNETES_SERVICE_ACCOUNT,
                },
            ).__dict__,
            "distributed_compute": StackComponent(
                name="ray",
                enabled=settings.RAY_ENABLED,
                config={
                    "dashboard_url": settings.RAY_DASHBOARD_URL,
                    "entrypoint": settings.RAY_JOB_ENTRYPOINT,
                    "alternatives": ["spark", "dask"],
                },
            ).__dict__,
            "storage": {
                "database": "postgresql",
                "database_alternatives": ["cockroachdb", "mongodb", "cassandra"],
                "object_storage": {
                    "enabled": settings.OBJECT_STORAGE_ENABLED,
                    "bucket": settings.OBJECT_STORAGE_BUCKET,
                    "endpoint": settings.OBJECT_STORAGE_ENDPOINT,
                },
            },
            "distributed_compute": self._distributed_compute(),
            "storage": self._storage(),
            "monitoring": {
                "metrics": ["prometheus", "grafana"],
                "logs": ["elasticsearch", "logstash", "kibana"],
            },
            "security": {
                "auth": "jwt",
                "authorization": "rbac",
                "secrets_provider": settings.SECRETS_PROVIDER,
            },
        }

    def submit_execution(self, pipeline_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a stack-aware execution command envelope.

        This API intentionally stays transport-agnostic and returns metadata that
        can be consumed by workers/connectors for Airflow/Temporal/Kubernetes/Ray.
        """
        execution_id = f"exec-{uuid4()}"
        now = datetime.now(tz=timezone.utc).isoformat()

        commands: List[Dict[str, Any]] = [
            {
                "layer": "orchestration",
                "engine": settings.ORCHESTRATION_ENGINE,
                "action": "start_workflow",
            },
            {
                "layer": "execution",
                "engine": "kubernetes-jobs",
                "action": "submit_job",
                "namespace": settings.KUBERNETES_NAMESPACE,
                "image": settings.KUBERNETES_JOB_IMAGE,
            },
        ]

        if settings.RAY_ENABLED:
            commands.append(
                {
                    "layer": "distributed_compute",
                    "engine": "ray",
                    "action": "submit_ray_job",
                    "dashboard": settings.RAY_DASHBOARD_URL,
                }
            )
        else:
            commands.append(
                {
                    "layer": "distributed_compute",
                    "engine": "spark",
                    "action": "submit_spark_job",
                }
            )

        if settings.KAFKA_ENABLED:
            commands.append(
                {
                    "layer": "event_layer",
                    "engine": "kafka",
                    "action": "publish_event",
                    "topic": settings.KAFKA_EXECUTION_TOPIC,
                }
            )
        compute = self._distributed_compute()
        if compute["enabled"]:
            compute_command = {
                "layer": "distributed_compute",
                "engine": compute["name"],
                "action": f"submit_{compute['name']}_job",
            }
            if compute["name"] == "ray":
                compute_command["dashboard"] = settings.RAY_DASHBOARD_URL
            if compute["name"] == "spark":
                compute_command["master_url"] = settings.SPARK_MASTER_URL
            if compute["name"] == "dask":
                compute_command["scheduler_address"] = settings.DASK_SCHEDULER_ADDRESS
            commands.append(compute_command)

        event_layer = self._event_layer()
        if event_layer["enabled"]:
            event_command = {
                "layer": "event_layer",
                "engine": event_layer["name"],
                "action": "publish_event",
            }
            if event_layer["name"] == "kafka":
                event_command["topic"] = settings.KAFKA_EXECUTION_TOPIC
            if event_layer["name"] == "pulsar":
                event_command["topic"] = settings.PULSAR_EXECUTION_TOPIC
            if event_layer["name"] == "rabbitmq":
                event_command["exchange"] = settings.RABBITMQ_EXCHANGE
                event_command["routing_key"] = settings.RABBITMQ_QUEUE
            if event_layer["name"] == "nats":
                event_command["subject"] = settings.NATS_SUBJECT
            commands.append(event_command)

        return {
            "execution_id": execution_id,
            "pipeline_id": pipeline_id,
            "submitted_at": now,
            "status": "accepted",
            "commands": commands,
            "payload": payload,
        }
