select
    cohort_month,
    months_since_first_purchase,
    new_customers,
    returning_customers,
    retention_rate,
    cohort_revenue
from {{ ref('seed_customer_retention') }}
