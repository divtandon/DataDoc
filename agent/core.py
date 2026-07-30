from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query

from . import config

SYSTEM_PROMPT = (config.PROMPTS_DIR / "system_prompt.md").read_text()


def _datahub_mcp_server() -> dict:
    server: dict = {"type": "http", "url": config.DATAHUB_MCP_URL}
    if config.DATAHUB_MCP_TOKEN:
        server["headers"] = {"Authorization": f"Bearer {config.DATAHUB_MCP_TOKEN}"}
    return {"datahub": server}


async def run_agent(task_prompt: str) -> str:
    """Run one codegen task through the local Claude Code CLI session.

    Rides on Claude Code's own subscription auth instead of a metered
    Anthropic API key. The DataHub MCP server is wired in via
    ClaudeAgentOptions.mcp_servers; Claude Code's built-in Write tool
    persists generated files, and DataHub's own MCP tools supply
    schema/lineage context and, when confident, write metadata back to
    the catalog.
    """
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers=_datahub_mcp_server(),
        disallowed_tools=["Bash", "WebSearch", "WebFetch"],
        permission_mode="bypassPermissions",
        cwd=str(config.ROOT_DIR),
        model=config.MODEL or None,
    )

    final_text: list[str] = []
    async for message in query(prompt=task_prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    final_text.append(block.text)

    return "".join(final_text)
