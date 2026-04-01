select
    cast(data_date as date) as data_date,
    url,
    query,
    impressions,
    clicks,
    sum_top_position,
    is_organic_shopping,
    is_product_snippets,
    is_merchant_listings
from {{ ref('seed_seo_pages') }}
