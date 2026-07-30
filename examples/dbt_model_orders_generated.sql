-- ============================================================================
-- Model: stg_orders
-- Source dataset (DataHub): urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.raw_orders,PROD)
--
-- DataHub context used to generate this model:
--   Description : "Raw customer orders, loaded from the checkout service."
--   Columns (verified via DataHub schema, none invented):
--     - order_id           varchar   "Primary key"
--     - customer_id        varchar   "FK to customers table"
--     - order_total_cents  bigint    "Order total in cents"
--     - placed_at           timestamp "When the order was placed"
--     - region              varchar   "Sales region"
--     - status              varchar   "Order status: pending, shipped, cancelled, test"
--   Upstream lineage  : none registered in DataHub (raw_orders is the root/source table)
--   Downstream lineage: analytics.weekly_revenue_report (Finance-certified weekly revenue rollup)
--   Owners            : none set in DataHub
--   Glossary terms/tags: none set in DataHub (no PII tags present; no PII columns identified)
--
-- Note: `status` includes a "test" value per its DataHub column description. Since the sole
-- known downstream consumer (analytics.weekly_revenue_report) is a Finance-certified revenue
-- rollup, this staging model filters out test orders so they don't leak into revenue reporting.
-- Flag/remove this filter if `weekly_revenue_report` is confirmed to want test rows.
-- ============================================================================

with source as (

    select * from {{ source('analytics', 'raw_orders') }}

),

renamed as (

    select
        order_id,
        customer_id,
        status,
        region,
        placed_at,
        order_total_cents,
        order_total_cents / 100.0 as order_total_dollars

    from source
    where status != 'test'  -- exclude test orders from downstream revenue reporting

)

select * from renamed


-- ============================================================================
-- schema.yml
-- (Place alongside this model, e.g. models/staging/orders/_orders__models.yml)
-- ============================================================================
/*
version: 2

sources:
  - name: analytics
    schema: analytics
    tables:
      - name: raw_orders
        description: "Raw customer orders, loaded from the checkout service."
        columns:
          - name: order_id
            description: "Primary key"
            tests:
              - unique
              - not_null
          - name: customer_id
            description: "FK to customers table"
            tests:
              - not_null
          - name: order_total_cents
            description: "Order total in cents"
          - name: placed_at
            description: "When the order was placed"
          - name: region
            description: "Sales region"
          - name: status
            description: "Order status: pending, shipped, cancelled, test"

models:
  - name: stg_orders
    description: >
      Staging model for raw customer orders (source: analytics.raw_orders,
      loaded from the checkout service). Excludes test orders (status = 'test')
      since the known downstream consumer, analytics.weekly_revenue_report,
      is a Finance-certified revenue rollup.
    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - unique
          - not_null
      - name: customer_id
        description: "FK to customers table"
        tests:
          - not_null
      - name: status
        description: "Order status: pending, shipped, cancelled (test rows filtered out)"
        tests:
          - accepted_values:
              values: ['pending', 'shipped', 'cancelled']
      - name: region
        description: "Sales region"
      - name: placed_at
        description: "When the order was placed"
      - name: order_total_cents
        description: "Order total in cents"
      - name: order_total_dollars
        description: "Order total converted to dollars (order_total_cents / 100.0)"
*/
