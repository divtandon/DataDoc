# DataDoc

A metadata-aware code generation agent built for [Build with DataHub: The
Agent Hackathon](https://datahub.devpost.com/). DataDoc reads a dataset's
real schema, lineage, and glossary context straight from DataHub via the
**DataHub MCP Server** before generating dbt models, Airflow DAGs, or SQL
migrations — so the output references real columns and real upstream tables
instead of guessing.

Where useful, it writes back to the DataHub graph too (e.g. tagging a column
it's confident is PII), so the next person or agent inherits what it found.

## How it works

DataDoc drives the local **Claude Code CLI** via the Claude Agent SDK
(`agent/core.py`), with the DataHub MCP server wired in as a tool source.
The model decides what to look up and when, then writes the generated code
to disk with Claude Code's built-in `Write` tool. This rides on your
existing Claude Code/Pro subscription auth — no separate metered API key
needed. See [docs/architecture.md](docs/architecture.md) for the full
picture.

```
CLI ──▶ agent/generators/*.py ──▶ agent/core.py (claude_agent_sdk.query)
                                        │
                                        ├── DataHub MCP Server (schema, lineage, write-back)
                                        └── Claude Code's built-in Write tool
```

## Setup

Requires Python 3.11+ and the [Claude Code CLI](https://claude.com/claude-code)
installed and logged in (`claude login`) with an active Pro/Max
subscription.

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env        # fill in DATAHUB_MCP_URL, DATAHUB_MCP_TOKEN
```

`DATAHUB_MCP_URL` is your DataHub instance's MCP endpoint (DataHub Cloud
exposes this at `https://<tenant>.acryl.io/api/mcp`; self-hosted setups
follow the [MCP Server docs](https://docs.datahub.com)).

### Local self-hosted DataHub

No DataHub instance handy? Spin one up locally:

```bash
pip install acryl-datahub
datahub docker quickstart

# seed a couple of realistic sample datasets (the built-in
# `datahub docker ingest-sample-data` is broken in some CLI versions)
python scripts/seed_local_sample_data.py

# in a separate terminal: mint a local token and start the MCP server
python scripts/run_local_datahub_mcp.py
```

Then set `DATAHUB_MCP_URL=http://127.0.0.1:8000/mcp` in `.env` (no token
needed there — the local MCP HTTP transport isn't itself authenticated).

## Usage

```bash
python cli.py dbt analytics.raw_orders --out models/staging/stg_orders.sql
python cli.py airflow analytics.raw_orders --out dags/orders_ingest.py
python cli.py migration analytics.raw_orders --out migrations/0001_add_region.sql
```

Each run prints a summary of what DataHub context was used and where the
file landed.

## Project structure

```
DataDoc/
├── agent/
│   ├── core.py                # claude_agent_sdk query() wired to the DataHub MCP server
│   ├── config.py
│   ├── prompts/                # system prompt + codegen template
│   └── generators/             # dbt / airflow / migration generators
├── cli.py                      # entrypoint
├── scripts/
│   ├── run_local_datahub_mcp.py  # bootstrap the MCP server against a local quickstart
│   └── seed_local_sample_data.py # seed sample datasets for local dev
├── examples/                   # sample generated artifacts
├── tests/
├── docs/architecture.md
└── demo/script.md              # shot list for the submission video
```

## Status

Early scaffold — see [docs/architecture.md](docs/architecture.md#known-gaps--next-steps)
for what's stubbed vs. real. Built for the DataHub Agent Hackathon
("Metadata-Aware Code Generation & Development" track) and for my own
learning.

## License

Apache 2.0 — see [LICENSE](LICENSE).
