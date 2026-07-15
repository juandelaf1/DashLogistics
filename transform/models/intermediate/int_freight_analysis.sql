with shipping as (
    select * from {{ ref('stg_shipping_stats') }}
),
fuel as (
    select * from {{ ref('stg_fuel_prices') }}
),
merged as (
    select
        coalesce(s.state, f.state) as state,
        s.postal,
        s.rank,
        s.population,
        s.population_per_rank,
        coalesce(s.regular, f.regular) as regular,
        coalesce(s.mid_grade, f.mid_grade) as mid_grade,
        coalesce(s.premium, f.premium) as premium,
        coalesce(s.diesel, f.diesel) as diesel,
        s.pipeline_run_id,
        f.scraped_at
    from shipping s
    full outer join fuel f on s.state = f.state
)
select
    *,
    population / nullif(diesel * 100, 0) as efficiency_score,
    (population / nullif(population, 0)) * diesel as fuel_burden_index
from merged
