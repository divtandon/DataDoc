"""Extend the demo lineage graph for a more visually interesting screenshot:

  checkout_events -> raw_orders -> weekly_revenue_report -> exec_revenue_dashboard

Purely cosmetic/demo -- doesn't change what DataDoc's generators reference.

Usage:
    DATAHUB_GMS_URL=http://localhost:8080 python scripts/seed_richer_lineage.py
"""

import os

from datahub.ingestion.graph.config import ClientMode
from datahub.sdk import Dataset
from datahub.sdk.main_client import DataHubClient

GMS_URL = os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080")

CHECKOUT_EVENTS_SCHEMA = [
    ("event_id", "varchar", "Primary key"),
    ("order_id", "varchar", "Order this checkout event belongs to"),
    ("event_type", "varchar", "e.g. cart_created, payment_authorized, order_placed"),
    ("occurred_at", "timestamp", "When the event was emitted"),
]

EXEC_DASHBOARD_SCHEMA = [
    ("week_start", "timestamp", "Start of the reporting week"),
    ("total_revenue", "double", "Total revenue across all regions for the week"),
    ("region_count", "bigint", "Number of regions with reported revenue"),
]


def main() -> None:
    client = DataHubClient.from_env(client_mode=ClientMode.SDK)

    checkout_events = Dataset(
        platform="snowflake",
        name="analytics.checkout_events",
        description="Raw event stream from the checkout service, before aggregation into orders.",
        schema=CHECKOUT_EVENTS_SCHEMA,
    )
    client.entities.upsert(checkout_events)

    raw_orders = Dataset(
        platform="snowflake",
        name="analytics.raw_orders",
        description="Raw customer orders, loaded from the checkout service.",
        schema=[
            ("order_id", "varchar", "Primary key"),
            ("customer_id", "varchar", "FK to customers table"),
            ("status", "varchar", "Order status: pending, shipped, cancelled, test"),
            ("order_total_cents", "bigint", "Order total in cents"),
            ("placed_at", "timestamp", "When the order was placed"),
            ("region", "varchar", "Sales region"),
        ],
        upstreams=[checkout_events.urn],
    )
    client.entities.upsert(raw_orders)

    exec_dashboard = Dataset(
        platform="snowflake",
        name="analytics.exec_revenue_dashboard",
        description="Executive summary rollup of weekly revenue across all regions.",
        schema=EXEC_DASHBOARD_SCHEMA,
        upstreams=["urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.weekly_revenue_report,PROD)"],
        subtype="Dashboard",
    )
    client.entities.upsert(exec_dashboard)

    print(f"Extended lineage: {checkout_events.urn} -> raw_orders -> weekly_revenue_report -> {exec_dashboard.urn}")


if __name__ == "__main__":
    main()
