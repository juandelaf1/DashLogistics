select
    state,
    regular,
    mid_grade,
    premium,
    diesel,
    scraped_at,
    pipeline_run_id
from {{ source('shipping_db', 'fuel_prices') }}
