select
    cast(data_date as date) as data_date,
    site_url,
    query,
    search_type,
    impressions,
    clicks,
    sum_top_position
from {{ ref('seed_seo_performance') }}
