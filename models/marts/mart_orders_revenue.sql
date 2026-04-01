select
    cast(order_date as date) as order_date,
    channel,
    sessions,
    orders,
    new_customer_orders,
    returning_customer_orders,
    gross_revenue,
    amount_refunded,
    gross_revenue - amount_refunded as net_revenue,
    units_sold,
    units_returned,
    cogs,
    gross_revenue - amount_refunded - cogs as gross_profit,
    ad_spend
from {{ ref('seed_orders_revenue') }}
