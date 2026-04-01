select
    cast(report_date as date) as report_date,
    account_name,
    campaign_name,
    campaign_status,
    channel_type,
    device,
    ad_network_type,
    impressions,
    clicks,
    cost,
    conversions,
    conversions_value
from {{ ref('seed_google_ads_performance') }}
