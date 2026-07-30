import argparse
import sys

from agent.generators.airflow_generator import generate_airflow_dag
from agent.generators.dbt_generator import generate_dbt_model
from agent.generators.migration_generator import generate_migration

GENERATORS = {
    "dbt": generate_dbt_model,
    "airflow": generate_airflow_dag,
    "migration": generate_migration,
}


def main() -> None:
    # Windows consoles default stdout to cp1252, which can't encode characters
    # Claude sometimes uses in its summaries (arrows, em dashes, ...).
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        prog="datadoc",
        description="Generate production data code from live DataHub metadata.",
    )
    parser.add_argument("kind", choices=GENERATORS.keys(), help="type of artifact to generate")
    parser.add_argument("table", help="fully qualified dataset name as known to DataHub")
    parser.add_argument("--out", required=True, help="output file path")
    parser.add_argument("--instructions", default="", help="extra free-text instructions")
    args = parser.parse_args()

    try:
        result = GENERATORS[args.kind](args.table, args.out, args.instructions)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print(result)


if __name__ == "__main__":
    main()
