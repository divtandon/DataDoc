from .common import generate

TARGET = "Airflow DAG (TaskFlow API, sensible schedule and retries inferred from lineage)"


def generate_airflow_dag(table: str, out_path: str, extra_instructions: str = "") -> str:
    return generate(TARGET, table, out_path, extra_instructions)
