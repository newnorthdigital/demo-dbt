select
    cast(session_date as date) as session_date,
    session_source,
    session_medium,
    session_campaign,
    session_default_channel_grouping,
    device_category,
    country,
    landing_page_path,
    sessions,
    engaged_sessions,
    revenue,
    page_views,
    add_to_cart_events,
    begin_checkout_events,
    purchase_events,
    transactions
from {{ ref('seed_daily_performance') }}
