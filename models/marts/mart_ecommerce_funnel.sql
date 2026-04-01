select
    cast(event_date as date) as event_date,
    device_category,
    channel_grouping,
    sessions,
    product_views,
    add_to_cart,
    begin_checkout,
    purchases,
    revenue
from {{ ref('seed_ecommerce_funnel') }}
