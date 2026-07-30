from pathlib import Path

from agent.generators.common import TEMPLATE, _write_file


def test_codegen_template_formats_with_expected_fields():
    prompt = TEMPLATE.format(
        target="dbt transformation model",
        table="analytics.raw_orders",
        out_path="examples/out.sql",
        extra_instructions="none",
    )
    assert "analytics.raw_orders" in prompt
    assert "examples/out.sql" in prompt
    assert "dbt transformation model" in prompt


def test_write_file_creates_parent_dirs(tmp_path):
    target = tmp_path / "nested" / "dir" / "out.sql"
    result = _write_file(str(target), "select 1")
    assert target.read_text() == "select 1"
    assert "wrote" in result
