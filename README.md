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

A single Claude tool-use loop (`agent/core.py`) is handed two sets of tools:
DataHub's own MCP tools (search, schema, lineage, tagging, ...) and one
local `write_file` tool. The model decides what to look up and when, then
writes the generated code to disk. See [docs/architecture.md](docs/architecture.md)
for the full picture.

```
CLI ──▶ agent/generators/*.py ──▶ agent/core.py (tool-use loop)
                                        │
                                        ├── DataHub MCP Server (schema, lineage, write-back)
                                        └── local write_file tool
```

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env        # fill in ANTHROPIC_API_KEY, DATAHUB_MCP_URL, DATAHUB_MCP_TOKEN
```

`DATAHUB_MCP_URL` is your DataHub instance's MCP endpoint (DataHub Cloud
exposes this at `https://<tenant>.acryl.io/api/mcp`; self-hosted setups
follow the [MCP Server docs](https://docs.datahub.com)).

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
│   ├── core.py                # Claude tool-use loop (MCP tools + local tools)
│   ├── datahub_mcp_client.py  # MCP session against the DataHub MCP Server
│   ├── config.py
│   ├── prompts/               # system prompt + codegen template
│   └── generators/            # dbt / airflow / migration generators
├── cli.py                     # entrypoint
├── examples/                  # sample generated artifacts
├── tests/
├── docs/architecture.md
└── demo/script.md             # shot list for the submission video
```

## Status

Early scaffold — see [docs/architecture.md](docs/architecture.md#known-gaps--next-steps)
for what's stubbed vs. real. Built for the DataHub Agent Hackathon
("Metadata-Aware Code Generation & Development" track) and for my own
learning.

## License

Apache 2.0 — see [LICENSE](LICENSE).
