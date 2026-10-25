-- National per-capita spending: assignable person-year weighted mean over counties with both values.
select year, type, sum(pc * person_years) / sum(person_years) as pc
from {{ ref('county') }}
where pc is not null and person_years > 0
group by year, type
