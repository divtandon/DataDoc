from agent.generators.common import TEMPLATE


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
