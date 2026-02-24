"""Data platform configuration and technology capability routes."""
from fastapi import APIRouter

from backend.api.schemas import DataPlatformStackResponse, PlatformOption
from backend.config import settings

router = APIRouter(prefix="/data-platform", tags=["data-platform"])


@router.get("", response_model=DataPlatformStackResponse)
async def get_data_platform_stack() -> DataPlatformStackResponse:
    """Return supported data platform technologies and current backend choices."""
    return DataPlatformStackResponse(
        ingestion_options=[
            PlatformOption(name="Apache Kafka", category="streaming", description="Distributed event streaming platform"),
            PlatformOption(name="Redpanda", category="streaming", description="Kafka-compatible streaming data platform"),
            PlatformOption(name="Apache NiFi", category="etl", description="Visual ETL and data flow automation"),
        ],
        data_lake_options=[
            PlatformOption(name="Amazon S3", category="object-storage", description="AWS object storage for data lake workloads"),
            PlatformOption(name="Google Cloud Storage", category="object-storage", description="GCP object storage for analytics and AI"),
            PlatformOption(name="Azure Blob", category="object-storage", description="Azure object storage for large-scale datasets"),
        ],
        data_warehouse_options=[
            PlatformOption(name="Snowflake", category="cloud-data-warehouse", description="Elastic cloud data warehouse"),
            PlatformOption(name="BigQuery", category="cloud-data-warehouse", description="Serverless enterprise data warehouse on GCP"),
            PlatformOption(name="Amazon Redshift", category="cloud-data-warehouse", description="AWS managed petabyte-scale data warehouse"),
        ],
        feature_store_options=[
            PlatformOption(name="Feast", category="feature-store", description="Open source feature store for ML"),
            PlatformOption(name="Tecton", category="feature-store", description="Managed feature platform for production ML"),
        ],
        current={
            "data_ingestion": settings.DATA_INGESTION,
            "data_lake": settings.DATA_LAKE,
            "data_warehouse": settings.DATA_WAREHOUSE,
            "feature_store": settings.FEATURE_STORE,
        },
    )
