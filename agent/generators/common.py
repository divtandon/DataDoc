import asyncio

from .. import config
from ..core import run_agent

TEMPLATE = (config.PROMPTS_DIR / "codegen_prompt.md").read_text()


async def _generate(target: str, table: str, out_path: str, extra_instructions: str) -> str:
    config.require_config()
    prompt = TEMPLATE.format(
        target=target, table=table, out_path=out_path, extra_instructions=extra_instructions or "none"
    )
    return await run_agent(prompt)


def generate(target: str, table: str, out_path: str, extra_instructions: str = "") -> str:
    return asyncio.run(_generate(target, table, out_path, extra_instructions))
