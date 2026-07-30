from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from . import config


@asynccontextmanager
async def connect():
    """Open an MCP session against the DataHub MCP Server.

    DataHub Cloud/self-hosted exposes catalog operations (search, schema,
    lineage, quality, and metadata write-back) as MCP tools. Everything
    the agent knows about a dataset comes through this session, not from
    a local cache, so generated code reflects the live catalog.
    """
    headers = {"Authorization": f"Bearer {config.DATAHUB_MCP_TOKEN}"} if config.DATAHUB_MCP_TOKEN else {}
    async with streamablehttp_client(config.DATAHUB_MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


def mcp_tools_to_anthropic_schema(list_tools_result) -> list[dict]:
    return [
        {
            "name": tool.name,
            "description": tool.description or "",
            "input_schema": tool.inputSchema,
        }
        for tool in list_tools_result.tools
    ]
