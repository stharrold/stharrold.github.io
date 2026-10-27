-- PY2021 person-year shares sum to 1 for every ACO whose shares are all known (section 4.3 step 4).
{{ config(tags=["full"]) }}
select aco_id
from {{ ref('shares') }}
group by aco_id
having bool_and(share is not null) and abs(sum(share) - 1) > 1e-9
