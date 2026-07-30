# Demo video shot list (<3 min)

1. **Hook (10s)** — "Agents that generate data code usually guess at column
   names. DataDoc doesn't guess — it reads DataHub first."
2. **Show the catalog (20s)** — open DataHub, show the target table
   (`analytics.raw_orders`), its schema, and its lineage into
   `weekly_revenue_report`.
3. **Run the agent (60s)** — terminal:
   `python cli.py dbt analytics.raw_orders --out models/staging/stg_orders.sql`
   Narrate the tool calls as they stream: schema lookup, lineage lookup,
   then file write.
4. **Show the output (30s)** — open the generated `.sql` file, point out it
   uses real column names and references the actual upstream source — no
   hallucinated fields.
5. **Show the write-back (20s)** — back in DataHub, show a column that got
   tagged/described by the agent as a side effect.
6. **Close (10s)** — recap: schema + lineage in, correct-on-first-try code
   out, and the catalog gets richer with every run.
