# DataDoc, Explained

A plain-English guide to what this project actually is — written for
understanding and interview prep, not for judges or developers (that's what
`README.md` is for).

## The big picture

Two completely different pieces of software are involved here, doing jobs
neither one can do alone.

### DataHub — the library (you did not build this)

DataHub is an existing, open-source product (built by a company called
Acryl Data). Its only job is to be a **searchable map of a company's
data**: what tables exist, what columns they have, what feeds into what,
who owns what. That's it. DataHub has **no idea how to write code** — it's
a database with a nice UI on top, like a library's card catalog. It
doesn't write books, it just tells you where they are.

You didn't build DataHub. You installed a copy of it running on your own
laptop (inside Docker), and put example data into it — `raw_orders`,
`weekly_revenue_report`, and a few others — so there'd be something real
to look up.

### DataDoc — the program you actually built

DataDoc is the AI agent. It:

1. Asks DataHub "what does this table actually look like?"
2. Reads the real answer (real columns, real relationships between tables)
3. Uses that answer to **write actual code** — a SQL model, a pipeline, a
   migration — something DataHub itself cannot do
4. Sometimes writes new information back into DataHub (e.g. tagging a
   column it noticed was undocumented)

DataDoc has **zero data of its own**. It stores nothing. Every time it
runs, it asks DataHub fresh, on the spot. Without DataHub running, DataDoc
has nothing to look at — it would fail immediately, because it has no
catalog to fall back on.

## Why one can't replace the other

- **DataHub can't replace DataDoc** because DataHub cannot generate code.
  It can show you a table's schema, but it will never write a dbt model
  for you. That's a different kind of job entirely.
- **DataDoc can't replace DataHub** because DataDoc has no memory or
  storage of its own. It's not a database — it's a one-shot worker that
  needs somewhere real to look things up *every single time* it runs. If
  DataHub disappeared, DataDoc would have nothing to check against and
  would just be a plain AI guessing at column names again — exactly the
  problem this whole project exists to solve.
- **Renaming DataHub to "DataDoc" would misrepresent the project.** It
  would make it look like you built the catalog itself, when the actual
  (harder, more interesting) thing you built is the *agent* that uses an
  existing catalog intelligently. "I used DataHub and built an agent on
  top of it" is a stronger, truer answer than "I built my own catalog."

## The full architecture, one more time

```
You type a command
        │
        ▼
   cli.py  (picks which generator: dbt / airflow / migration)
        │
        ▼
   agent/core.py  ──▶ runs Claude (via the Claude Agent SDK,
        │              using your Claude Code subscription —
        │              not a separate paid API key)
        │
        ├──▶ DataHub MCP Server ──▶ DataHub itself
        │      (the connector that lets Claude "ask" DataHub questions —
        │       search for a table, read its schema, read its lineage,
        │       write a tag or description back)
        │
        └──▶ Claude Code's built-in Write tool
               (saves the generated code to a file on your disk)
```

**MCP (Model Context Protocol)** is just the name for the standard way an
AI agent and a tool like DataHub talk to each other — think of it as the
plug shape that lets any AI agent connect to any tool that supports it,
without needing custom one-off code for every combination.

## Key vocabulary, in one sentence each

| Term | Plain-English meaning |
|---|---|
| **DataHub** | The catalog — a searchable map of a company's tables |
| **DataDoc** | The agent you built that reads that map and writes code from it |
| **MCP Server** | The connector/translator that lets an AI agent talk to DataHub |
| **Schema** | The list of columns a table has, and their types |
| **Lineage** | What feeds into a table, and what depends on it downstream |
| **Write-back** | The agent updating DataHub itself, not just reading from it |
| **dbt model** | A SQL file that transforms raw data into something clean/usable |
| **Airflow DAG** | A scheduled pipeline that moves/processes data on a timer |
| **Migration** | A script that changes a database table's structure safely |
| **Claude Agent SDK** | The toolkit that lets Claude drive tools/write files as an agent, using your Claude Code login instead of a metered API key |

## The story of actually building it (your best interview material)

- Started by calling the Anthropic API directly with a paid key — switched
  to the Claude Agent SDK instead, so it runs on your existing Claude Code
  subscription for free.
- Along the way, found and fixed a real bug: the `mcp` Python library's
  API had changed (`tool.inputSchema` didn't exist anymore, it was
  `tool.input_schema`) — found by actually running the code and reading
  the real error, not by guessing.
- Discovered write-back was silently disabled even with a valid login,
  because of a separate flag (`TOOLS_IS_MUTATION_ENABLED`) that had to be
  turned on explicitly.
- Tested a fresh clone of the repo in an isolated folder and discovered
  file-writes were landing in a sandboxed, fake filesystem instead of the
  real one — investigated *why*, and figured out it was an artifact of
  running nested inside another AI agent session, not a bug in the project
  itself.
- Proved write-back was real (not just claimed) by independently querying
  DataHub's own API afterward, instead of trusting the agent's own summary.
- Proved the agent refuses to make things up, by pointing it at a table
  name that doesn't exist and confirming it said so instead of inventing
  a fake schema.

That last block — the debugging journey — is genuinely the strongest thing
to talk about in an interview. Anyone can describe a finished feature;
being able to describe *how you found and fixed a real bug* is what shows
you actually understand what you built.
