with source as (
    select * from {{ ref('opendata_airquality') }}
)

select
    trim(city) as city,
    trim(country) as country,
    trim(location) as location,
    lower(trim(parameter)) as parameter,
    cast(value as double) as measurement_value,
    trim(unit) as unit,
    cast(date_utc as timestamp) as measured_at_utc
from source

