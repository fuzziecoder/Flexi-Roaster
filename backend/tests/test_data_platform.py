import asyncio

from backend.api.routes.data_platform import get_data_platform_stack
from backend.config import settings


def test_data_platform_stack_response_contains_required_options():
    response = asyncio.run(get_data_platform_stack())

    ingestion = {item.name for item in response.ingestion_options}
    assert {"Apache Kafka", "Redpanda", "Apache NiFi"}.issubset(ingestion)

    data_lake = {item.name for item in response.data_lake_options}
    assert {"Amazon S3", "Google Cloud Storage", "Azure Blob"}.issubset(data_lake)

    warehouses = {item.name for item in response.data_warehouse_options}
    assert {"Snowflake", "BigQuery", "Amazon Redshift"}.issubset(warehouses)

    feature_stores = {item.name for item in response.feature_store_options}
    assert {"Feast", "Tecton"}.issubset(feature_stores)


def test_data_platform_stack_includes_current_backend_configuration():
    response = asyncio.run(get_data_platform_stack())

    assert response.current["data_ingestion"] == settings.DATA_INGESTION
    assert response.current["data_lake"] == settings.DATA_LAKE
    assert response.current["data_warehouse"] == settings.DATA_WAREHOUSE
    assert response.current["feature_store"] == settings.FEATURE_STORE
