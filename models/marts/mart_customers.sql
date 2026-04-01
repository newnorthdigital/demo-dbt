select
    cast(order_date as date) as order_date,
    new_customers,
    returning_customers,
    total_customers,
    new_customer_revenue,
    returning_customer_revenue,
    new_customer_revenue + returning_customer_revenue as total_revenue,
    new_customer_aov,
    returning_customer_aov,
    new_customer_items,
    returning_customer_items,
    customer_lifetime_value
from {{ ref('seed_customers') }}
