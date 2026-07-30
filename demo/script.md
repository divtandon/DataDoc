# Demo script — plain-English version

For an audience with zero context: no DataHub, no dbt, no "MCP." Assume they
just know "AI" and "database." Written to be read almost word-for-word while
recording, timed for under 3 minutes.

---

## 0. The one-sentence pitch (say this first, before showing anything)

> "AI coding assistants are great at writing code, but when you ask one to
> write code for *your* database, it just guesses at what your data looks
> like. I built an agent that looks at the real database first, then writes
> the code — so it's actually right, not just plausible."

## 1. Show the problem (15 sec)

Open a plain ChatGPT/Claude window and type:

> "Write me a SQL query that summarizes our orders table by region."

Let it answer. Point out: *it just made up column names* — it has no idea
what your `orders` table actually contains. That's the problem.

## 2. Show the "map" of your data (30 sec)

Switch to the DataHub web UI (`http://localhost:9002`), open the
`analytics.raw_orders` table.

> "This is DataHub — think of it like a map of every table in a company's
> database: what columns it has, where the data comes from, and what other
> reports depend on it. Companies like Netflix and Pinterest use this so
> people (and now AI agents) can actually find and trust the right data."

Point at the schema (real columns: `order_id`, `customer_id`, `status`,
etc.) and the lineage graph (`raw_orders` → `weekly_revenue_report`).

> "See this arrow? This orders table feeds directly into a revenue report
> that Finance uses. That's the kind of thing a plain AI would have no way
> of knowing."

## 3. Run the agent (60 sec) — the core of the demo

Switch to a terminal.

> "Now watch what happens when my agent, DataDoc, does the same job."

Run:
```bash
python cli.py dbt analytics.raw_orders --out examples/live_demo.sql
```

While it runs, narrate:

> "Right now it's calling into DataHub itself — looking up the real columns,
> checking what depends on this table — before it writes a single line of
> code."

When it finishes, read its summary output out loud (it names the exact
DataHub context it used).

## 4. Show the receipts (45 sec)

Open the generated `examples/live_demo.sql` file.

> "Every column name here is real — pulled straight from DataHub, nothing
> guessed. And look — it noticed this table feeds a Finance revenue report,
> so it automatically excluded test orders so they don't pollute real
> revenue numbers. It figured that out from the data's real context, not
> because I told it to."

Optionally scroll to the header comment block, which literally states what
DataHub context was used — visual proof it's not black-box.

## 5. Close (15 sec)

> "That's DataDoc: an agent that reads your real data catalog before it
> writes code, so the output works the first time instead of needing three
> rounds of fixes. Repo's linked below."

---

## Cheat sheet: jargon → plain English (keep handy while answering questions)

| Term | Say instead |
|---|---|
| DataHub | "a map / catalog of all our data tables" |
| MCP server | "the connector that lets the AI talk to that map" |
| Schema | "what columns a table has" |
| Lineage | "what feeds into a table, and what it feeds into" |
| dbt model | "a SQL file that transforms raw data into something useful" |
| Write-back | "the agent updating the map itself when it learns something new" |

## What to have open/ready before recording

- [ ] Local DataHub running (`http://localhost:9002` loads)
- [ ] Local MCP server running (`scripts/run_local_datahub_mcp.py`)
- [ ] Terminal in the project folder, venv activated
- [ ] `analytics.raw_orders` page open in DataHub in a browser tab
- [ ] A plain Claude/ChatGPT tab open for the "before" comparison in step 1
