with shipping as (
    select * from {{ ref('stg_shipping_stats') }}
)
select
    state,
    postal,
    rank,
    population,
    case
        when state in ('CT','ME','MA','NH','RI','VT','NJ','NY','PA') then 'Northeast'
        when state in ('DE','FL','GA','MD','NC','SC','VA','WV','AL','KY','MS','TN','AR','LA','OK','TX') then 'South'
        when state in ('IL','IN','MI','OH','WI','IA','KS','MN','MO','NE','ND','SD') then 'Midwest'
        when state in ('AZ','CO','ID','MT','NV','NM','UT','WY','AK','CA','HI','OR','WA') then 'West'
        else 'Unknown'
    end as region,
    current_timestamp as dbt_loaded_at
from shipping
