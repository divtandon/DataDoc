from .common import generate

TARGET = "reversible SQL schema migration (explicit up and down steps)"


def generate_migration(table: str, out_path: str, extra_instructions: str = "") -> str:
    return generate(TARGET, table, out_path, extra_instructions)
