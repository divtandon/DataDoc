"""Seed a small, realistic dataset into a local DataHub quickstart instance.

`datahub docker ingest-sample-data` is broken in the currently pinned CLI
version (raises `KeyError: 'c'` from its own recipe), so this seeds exactly
the dataset our README/demo/examples already reference instead: it doubles
as a working substitute and keeps the whole project's narrative consistent.

Usage:
    DATAHUB_GMS_URL=http://localhost:8080 python scripts/seed_local_sample_data.py
"""

import os

from datahub.ingestion.graph.config import ClientMode
from datahub.sdk import Dataset
from datahub.sdk.main_client import DataHubClient

GMS_URL = os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080")
PLATFORM = "snowflake"

ORDERS_SCHEMA = [
    ("order_id", "varchar", "Primary key"),
    ("customer_id", "varchar", "FK to customers table"),
    ("status", "varchar", "Order status: pending, shipped, cancelled, test"),
    ("order_total_cents", "bigint", "Order total in cents"),
    ("placed_at", "timestamp", "When the order was placed"),
    ("region", "varchar", "Sales region"),
]

REVENUE_REPORT_SCHEMA = [
    ("region", "varchar", "Sales region"),
    ("week_start", "timestamp", "Start of the reporting week"),
    ("total_revenue", "double", "Sum of order_total for the week"),
]


def main() -> None:
    client = DataHubClient.from_env(client_mode=ClientMode.SDK)

    orders = Dataset(
        platform=PLATFORM,
        name="analytics.raw_orders",
        description="Raw customer orders, loaded from the checkout service.",
        schema=ORDERS_SCHEMA,
    )
    client.entities.upsert(orders)

    revenue_report = Dataset(
        platform=PLATFORM,
        name="analytics.weekly_revenue_report",
        description="Certified weekly revenue rollup used by Finance.",
        schema=REVENUE_REPORT_SCHEMA,
        upstreams=[orders.urn],
        subtype="Dashboard",
    )
    client.entities.upsert(revenue_report)

    print(f"Seeded {orders.urn} and {revenue_report.urn} against {GMS_URL}")


if __name__ == "__main__":
    main()
