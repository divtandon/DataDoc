import asyncio
from pathlib import Path

from .. import config
from ..core import run_agent
from ..datahub_mcp_client import connect

TEMPLATE = (config.PROMPTS_DIR / "codegen_prompt.md").read_text()

WRITE_FILE_TOOL = {
    "write_file": {
        "name": "write_file",
        "description": "Write generated code to a file on disk, creating parent directories as needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    }
}


def _write_file(path: str, content: str) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return f"wrote {len(content)} bytes to {target}"


async def _generate(target: str, table: str, out_path: str, extra_instructions: str) -> str:
    config.require_config()
    prompt = TEMPLATE.format(
        target=target, table=table, out_path=out_path, extra_instructions=extra_instructions or "none"
    )
    async with connect() as session:
        return await run_agent(
            prompt,
            session,
            local_tools=WRITE_FILE_TOOL,
            local_handlers={"write_file": _write_file},
        )


def generate(target: str, table: str, out_path: str, extra_instructions: str = "") -> str:
    return asyncio.run(_generate(target, table, out_path, extra_instructions))
