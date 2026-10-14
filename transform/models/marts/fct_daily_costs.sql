with shipping as (
    select * from {{ ref('stg_shipping_stats') }}
),
fuel as (
    select * from {{ ref('stg_fuel_prices') }}
)
select
    coalesce(s.state, f.state) as state,
    s.population,
    f.regular,
    f.mid_grade,
    f.premium,
    f.diesel,
    f.scraped_at,
    round((s.population / 1000000.0) * f.diesel, 2) as estimated_daily_diesel_cost_millions,
    round((s.population / 1000000.0) * f.regular, 2) as estimated_daily_gas_cost_millions,
    s.pipeline_run_id
from shipping s
left join fuel f on s.state = f.state
