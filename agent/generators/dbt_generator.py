from .common import generate

TARGET = "dbt transformation model (SQL using ref()/source(), plus a schema.yml entry)"


def generate_dbt_model(table: str, out_path: str, extra_instructions: str = "") -> str:
    return generate(TARGET, table, out_path, extra_instructions)
