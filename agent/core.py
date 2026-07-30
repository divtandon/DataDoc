import json

import anthropic

from . import config
from .datahub_mcp_client import mcp_tools_to_anthropic_schema

SYSTEM_PROMPT = (config.PROMPTS_DIR / "system_prompt.md").read_text()

_client = None


def _anthropic_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


async def run_agent(task_prompt: str, mcp_session, local_tools: dict[str, dict], local_handlers: dict) -> str:
    """Drive a Claude tool-use loop where tools come from two sources:

    - the live DataHub MCP session (search, schema, lineage, write-back)
    - local tools this process owns (e.g. writing a file to disk)

    Returns the final text response once Claude stops requesting tool calls.
    """
    mcp_tools = mcp_tools_to_anthropic_schema(await mcp_session.list_tools())
    tools = mcp_tools + list(local_tools.values())
    mcp_tool_names = {t["name"] for t in mcp_tools}

    messages = [{"role": "user", "content": task_prompt}]
    client = _anthropic_client()

    while True:
        response = client.messages.create(
            model=config.MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            if block.name in mcp_tool_names:
                mcp_result = await mcp_session.call_tool(block.name, block.input)
                content = "".join(
                    part.text for part in mcp_result.content if getattr(part, "type", None) == "text"
                )
            elif block.name in local_handlers:
                content = local_handlers[block.name](**block.input)
            else:
                content = json.dumps({"error": f"unknown tool {block.name}"})

            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": content}
            )

        messages.append({"role": "user", "content": tool_results})
