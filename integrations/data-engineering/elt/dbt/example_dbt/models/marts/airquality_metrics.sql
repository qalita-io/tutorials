select
    city,
    parameter,
    unit,
    count(*) as measurement_count,
    avg(measurement_value) as avg_value,
    min(measurement_value) as min_value,
    max(measurement_value) as max_value
from {{ ref('stg_airquality') }}
group by 1,2,3

