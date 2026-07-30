# Sample outputs

Real artifacts generated end-to-end by DataDoc against a live local DataHub
instance (`analytics.raw_orders` → `analytics.weekly_revenue_report`, seeded
via `scripts/seed_local_sample_data.py`):

- `dbt_model_orders_generated.sql` — staging model + `schema.yml`
- `airflow_dag_orders_generated.py` — ingestion DAG
- `migration_orders_generated.sql` — additive column migration

Every column name, type, and design decision in these three came from
DataHub's real schema/lineage, not a guess — see the header comments in
each file for exactly what context was used.

`dbt_model_orders.sql` is the original hand-authored illustration from
before the agent existed, kept for reference.
