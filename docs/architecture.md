# Architecture

```
                    ┌─────────────────────┐
   CLI / caller ───▶│   agent/core.py      │
   "generate a dbt  │   claude_agent_sdk   │
   model for X"     │   query()            │
                    └──────────┬───────────┘
                               │ runs the local Claude Code CLI session
                               │ (Pro/Max subscription auth, no API key)
                               ▼
                    ┌─────────────────────┐
                    │   Claude Code CLI    │
                    │   built-in Write     │
                    │   tool + DataHub MCP │
                    │   tools (declared    │
                    │   via mcp_servers)   │
                    └──────────┬───────────┘
                               │
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
not "looks plausible." That means the DataHub MCP connection has to be a
first-class part of the same tool-use loop the model reasons in, not a
separate pre-fetch step: the model decides what to look up (schema, then
lineage, then glossary terms) based on what the generation task actually
needs, and can go back for more context if the first lookup surfaces an
unfamiliar upstream table.

`agent/core.py` drives this through the **Claude Agent SDK**
(`claude_agent_sdk.query`), which runs the request through the local Claude
Code CLI rather than calling the Anthropic API directly with a metered key.
Two things fall out of that:

1. **Auth rides on the Claude Code/Pro subscription**, not a separate
   pay-per-token API key — `claude login` once, and DataDoc just works.
2. **File writes use Claude Code's built-in `Write` tool** instead of a
   custom local tool. The `DATAHUB_MCP_URL` server is declared via
   `ClaudeAgentOptions.mcp_servers`, so its tools (search, schema, lineage,
   tagging, ...) show up in the same tool list the model already has —
   DataDoc doesn't hardcode DataHub's tool surface, so it keeps working as
   DataHub ships more MCP tools.

`agent/generators/*.py` are thin wrappers that pick a target-framework
description and hand off to the shared prompt-building logic in
`common.py` — the difference between generating a dbt model vs. an Airflow
DAG vs. a migration is just the prompt, not the orchestration.

Because this shells out to the `claude` CLI, running DataDoc requires
Claude Code installed and authenticated (`claude login`) on the machine
that runs it — not just a Python venv and an API key. That's a deliberate
trade-off: it avoids per-token API billing entirely, at the cost of judges
needing the same local setup to reproduce a run.

## Write-back

Judging criteria reward projects that "contribute back to the graph," not
just read it. Because DataHub's own MCP tools (e.g. tagging a column,
updating a description) are already in the tool list the model sees, the
agent can call them directly mid-generation — e.g. tagging a column it
determines is PII while writing the migration that touches it. This is
gated by the system prompt (`agent/prompts/system_prompt.md`) to only act
on high-confidence findings, and by the MCP server's own
`TOOLS_IS_MUTATION_ENABLED` flag (see `scripts/run_local_datahub_mcp.py`).

## Known gaps / next steps

- No retry/backoff around the DataHub MCP connection yet.
- `examples/` needs at least one *real* generated artifact (not just the
  hand-authored illustrative one) once this is run end-to-end — judges
  weight this.
- `disallowed_tools` in `agent/core.py` blocks `Bash`/`WebSearch`/`WebFetch`
  to keep the agent scoped to codegen + DataHub lookups; revisit if a
  future generator legitimately needs one of those.
