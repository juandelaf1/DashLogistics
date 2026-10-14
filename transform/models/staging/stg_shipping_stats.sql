select
    state,
    postal,
    rank,
    population,
    population_per_rank,
    regular,
    mid_grade,
    premium,
    diesel,
    pipeline_run_id
from {{ source('shipping_db', 'shipping_stats') }}
