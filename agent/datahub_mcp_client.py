from contextlib import asynccontextmanager

import httpx2
from mcp.client import Client
from mcp.client.streamable_http import streamable_http_client

from . import config


@asynccontextmanager
async def connect():
    """Open an MCP client session against the DataHub MCP Server.

    DataHub Cloud/self-hosted exposes catalog operations (search, schema,
    lineage, quality, and metadata write-back) as MCP tools. Everything
    the agent knows about a dataset comes through this session, not from
    a local cache, so generated code reflects the live catalog.
    """
    headers = {"Authorization": f"Bearer {config.DATAHUB_MCP_TOKEN}"} if config.DATAHUB_MCP_TOKEN else {}
    http_client = httpx2.AsyncClient(headers=headers)
    transport = streamable_http_client(config.DATAHUB_MCP_URL, http_client=http_client)
    async with Client(transport) as client:
        yield client


def mcp_tools_to_anthropic_schema(list_tools_result) -> list[dict]:
    return [
        {
            "name": tool.name,
            "description": tool.description or "",
            "input_schema": tool.input_schema,
        }
        for tool in list_tools_result.tools
    ]
