# DataDoc

A metadata-aware code generation agent built for [Build with DataHub: The
Agent Hackathon](https://datahub.devpost.com/).

AI coding assistants are good at writing code, but when you ask one to write
code against *your* database, it has no idea what your tables actually look
like — it guesses at column names, guesses at what depends on what, and the
output looks right until it isn't.

DataDoc doesn't guess. Give it a table name and it reads the real schema,
lineage, and glossary context straight from **DataHub** (via the DataHub MCP
Server) before generating a single line of a dbt model, an Airflow DAG, or a
SQL migration. When it notices something the catalog is missing — an
undocumented column, a likely-PII field — it writes that back too, so the
catalog gets better with every run instead of just being read from.

## How it works

```
CLI ──▶ agent/generators/*.py ──▶ agent/core.py (claude_agent_sdk.query)
                                        │
                                        ├── DataHub MCP Server (schema, lineage, write-back)
                                        └── Claude Code's built-in Write tool
```

DataDoc drives the local **Claude Code CLI** via the Claude Agent SDK
(`agent/core.py`), with the DataHub MCP server wired in declaratively as a
tool source (`ClaudeAgentOptions.mcp_servers`). The model decides what to
look up and when — schema first, then lineage, then glossary terms — and
writes the generated code to disk with Claude Code's built-in `Write` tool.
This rides on your existing Claude Code/Pro subscription auth, not a
separate metered API key. See [docs/architecture.md](docs/architecture.md)
for the full picture, including why it's built this way.

## Verified, not just claimed

Everything below was actually run against a live DataHub instance and
independently checked — not just described:

- **Real generation, not templating.** Every file in `examples/` was
  produced end-to-end by the agent against a live catalog; nothing was
  hand-written after the fact. The output correctly reasons from lineage
  (e.g. filtering test orders because the only downstream consumer is a
  Finance-certified revenue rollup) and flags its own inferred assumptions
  for reviewer sign-off instead of stating them as fact.
- **Write-back confirmed independently.** Seeded a dataset with an
  undocumented, PII-looking column, ran the agent, then queried DataHub's
  GraphQL API directly (not the agent's own summary) and confirmed the
  description it wrote actually persisted in `editableSchemaMetadata`.
- **Refuses to fabricate.** Pointed at a table that doesn't exist in
  DataHub, the agent searches, finds nothing, says so explicitly, and
  writes no file — instead of inventing a plausible-looking schema.
- **Reproducible from a clean setup**, including a from-scratch run in a
  separate PowerShell session with no leftover state.

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

# seed the demo dataset pair (the built-in
# `datahub docker ingest-sample-data` is broken in some CLI versions)
python scripts/seed_local_sample_data.py

# optional: extend it into a 4-hop lineage chain (nicer for screenshots/demos)
python scripts/seed_richer_lineage.py

# optional: seed a dataset with an undocumented/PII column, to test write-back
python scripts/seed_writeback_test_data.py

# in a separate terminal: mint a local token and start the MCP server
python scripts/run_local_datahub_mcp.py
```

Then set `DATAHUB_MCP_URL=http://127.0.0.1:8000/mcp` in `.env` (no token
needed there — the local MCP HTTP transport isn't itself authenticated).

### Starting everything back up (already set up once)

Docker containers don't survive a reboot, so after restarting your machine
you'll need three things running before `cli.py` works. Use three separate
terminal windows:

**1. Docker Desktop** — open it from the Start menu and wait until it says
it's running.

**2. DataHub itself:**
```powershell
cd C:\Users\divya\Desktop\DataDoc
python -m datahub docker quickstart
```
This re-attaches to the existing containers (safe to run even if they're
already up) and waits for them to become healthy. Confirm with:
```powershell
curl -UseBasicParsing http://localhost:9002
```
The UI itself is at **http://localhost:9002** (login: `datahub` / `datahub`).

**3. The local MCP server** (leave this terminal open and running):
```powershell
cd C:\Users\divya\Desktop\DataDoc
.\.mcpserver-venv\Scripts\python.exe scripts\run_local_datahub_mcp.py
```
You'll know it worked when you see `Uvicorn running on http://127.0.0.1:8000`.
A browser check at `http://127.0.0.1:8000/health` should return `{"status":"ok"}`
(visiting `http://127.0.0.1:8000/` directly will 404 — that's expected, the
MCP endpoint only answers at `/mcp` over POST).

**Then, in a fourth terminal**, activate the venv and run `cli.py` as usual
(see Usage below).

## Usage

```bash
python cli.py dbt analytics.raw_orders --out models/staging/stg_orders.sql
python cli.py airflow analytics.raw_orders --out dags/orders_ingest.py
python cli.py migration analytics.raw_orders --out migrations/0001_add_region.sql
```

Each run prints a summary of what DataHub context was used, what design
decisions it made and why, and where the file landed.

## Project structure

```
DataDoc/
├── agent/
│   ├── core.py                    # claude_agent_sdk query() wired to the DataHub MCP server
│   ├── config.py
│   ├── prompts/                   # system prompt + codegen template
│   └── generators/                # dbt / airflow / migration generators
├── cli.py                         # entrypoint
├── scripts/
│   ├── run_local_datahub_mcp.py     # bootstrap the MCP server against a local quickstart
│   ├── seed_local_sample_data.py    # seed the core raw_orders / weekly_revenue_report pair
│   ├── seed_richer_lineage.py       # extend that into a 4-hop lineage chain
│   └── seed_writeback_test_data.py  # seed an undocumented/PII column to test write-back
├── examples/                      # real generated artifacts (see examples/README.md)
├── tests/
├── docs/architecture.md           # why it's built this way, known gaps
└── demo/script.md                 # plain-English demo walkthrough for a non-technical audience
```

## Status

Built for the DataHub Agent Hackathon ("Metadata-Aware Code Generation &
Development" track) and for my own learning — see
[docs/architecture.md](docs/architecture.md#known-gaps--next-steps) for
what's still rough around the edges.

## License

Apache 2.0 — see [LICENSE](LICENSE).
