# Architecture

```
                    ┌─────────────────────┐
   CLI / caller ───▶│   agent/core.py      │
   "generate a dbt  │   Claude tool-use    │
   model for X"     │   loop               │
                    └──────────┬───────────┘
                               │ tools = DataHub MCP tools + write_file
                               ▼
                ┌──────────────────────────────┐
                │   DataHub MCP Server           │
                │   (search, get_schema,         │
                │   get_lineage, add_tag,        │
                │   update_description, ...)     │
                └──────────────┬─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   DataHub catalog    │
                    │   (schemas, lineage, │
                    │   glossary, quality) │
                    └─────────────────────┘
```

## Why this shape

The generation quality bar for this project is "works on the first try
because the agent looked up real schema and lineage before writing code" —
not "looks plausible." That means the DataHub MCP session has to be a first
class part of the tool-use loop, not a separate pre-fetch step: the model
decides what to look up (schema, then lineage, then glossary terms) based on
what the generation task actually needs, and can go back for more context if
the first lookup surfaces an unfamiliar upstream table.

`agent/core.py` runs a single Anthropic tool-use loop against two tool
sources merged into one list:

1. Whatever tools the connected DataHub MCP Server exposes (`list_tools()`
   at connection time — this project does not hardcode DataHub's tool
   surface, so it keeps working as DataHub ships more MCP tools).
2. A local `write_file` tool so the agent can persist generated code without
   needing filesystem access as an MCP tool.

`agent/generators/*.py` are thin wrappers that pick a target-framework
description and hand off to the shared loop in `common.py` — the difference
between generating a dbt model vs. an Airflow DAG vs. a migration is just
the prompt, not the orchestration.

## Write-back

Judging criteria reward projects that "contribute back to the graph," not
just read it. Because DataHub's own MCP tools (e.g. tagging a column,
updating a description) are already in the tool list the model sees, the
agent can call them directly mid-generation — e.g. tagging a column it
determines is PII while writing the migration that touches it. This is
gated by the system prompt (`agent/prompts/system_prompt.md`) to only act
on high-confidence findings.

## Known gaps / next steps

- `datahub_mcp_client.py` assumes a Streamable HTTP MCP endpoint. If your
  DataHub deployment only exposes stdio (e.g. a locally spawned MCP
  server process), swap `streamablehttp_client` for
  `mcp.client.stdio.stdio_client`.
- No retry/backoff around MCP or Anthropic calls yet.
- `examples/` needs at least one *real* generated artifact (not just the
  hand-authored illustrative one) once this is run against an actual
  DataHub instance — judges weight this.
