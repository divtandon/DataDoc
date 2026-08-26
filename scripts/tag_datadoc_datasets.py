"""Tag every dataset DataDoc has touched with a "DataDoc" tag, so the
project's name is visible directly in the DataHub UI (Summary/Columns page
of each dataset) -- useful for demos/screenshots.

Only sets the tags aspect; doesn't touch schema, description, or lineage
on these datasets.

Usage:
    DATAHUB_GMS_URL=http://localhost:8080 python scripts/tag_datadoc_datasets.py
"""

import os

from datahub.ingestion.graph.config import ClientMode
from datahub.sdk import Dataset
from datahub.sdk.main_client import DataHubClient

GMS_URL = os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080")

DATASETS = [
    "analytics.checkout_events",
    "analytics.raw_orders",
    "analytics.weekly_revenue_report",
    "analytics.exec_revenue_dashboard",
    "analytics.customer_signups",
]


def main() -> None:
    client = DataHubClient.from_env(client_mode=ClientMode.SDK)

    for name in DATASETS:
        dataset = Dataset(platform="snowflake", name=name, tags=["urn:li:tag:DataDoc"])
        client.entities.upsert(dataset)
        print(f"Tagged {dataset.urn} with DataDoc")


if __name__ == "__main__":
    main()
