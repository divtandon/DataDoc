"""Seed a dataset with an undocumented, PII-looking column, to test that
DataDoc actually writes metadata back to DataHub when it finds one -- not
just reads. Separate from seed_local_sample_data.py so it doesn't disturb
the raw_orders/weekly_revenue_report pair the main demo uses.

Usage:
    DATAHUB_GMS_URL=http://localhost:8080 python scripts/seed_writeback_test_data.py
"""

import os

from datahub.ingestion.graph.config import ClientMode
from datahub.sdk import Dataset
from datahub.sdk.main_client import DataHubClient

GMS_URL = os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080")

# Deliberately undocumented columns, including an obvious PII field, to see
# whether the agent notices and writes back a tag/description with high
# confidence -- per its system prompt's write-back rule.
SIGNUPS_SCHEMA = [
    ("signup_id", "varchar", "Primary key"),
    ("customer_email", "varchar", ""),
    ("signup_source", "varchar", ""),
    ("created_at", "timestamp", "When the signup record was created"),
]


def main() -> None:
    client = DataHubClient.from_env(client_mode=ClientMode.SDK)

    signups = Dataset(
        platform="snowflake",
        name="analytics.customer_signups",
        description="Customer signup events from the marketing site.",
        schema=SIGNUPS_SCHEMA,
    )
    client.entities.upsert(signups)

    print(f"Seeded {signups.urn} against {GMS_URL} (customer_email left undocumented on purpose)")


if __name__ == "__main__":
    main()
