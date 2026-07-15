with intermediate as (
    select * from {{ ref('int_freight_analysis') }}
)
select
    state,
    postal,
    rank,
    population,
    regular,
    mid_grade,
    premium,
    diesel,
    fuel_burden_index,
    efficiency_score,
    case
        when percent_rank() over (order by efficiency_score) >= 0.75 then 'Top Tier'
        when percent_rank() over (order by efficiency_score) >= 0.50 then 'Mid Tier'
        when percent_rank() over (order by efficiency_score) >= 0.25 then 'Low Tier'
        else 'Bottom Tier'
    end as efficiency_tier,
    pipeline_run_id
from intermediate
order by efficiency_score desc
