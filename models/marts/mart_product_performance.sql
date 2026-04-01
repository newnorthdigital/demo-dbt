select
    cast(order_date as date) as order_date,
    product_name,
    category,
    item_price,
    units_sold,
    revenue,
    units_returned,
    refund_amount,
    cogs,
    revenue - refund_amount - cogs as margin,
    repeat_order_pct
from {{ ref('seed_product_performance') }}
