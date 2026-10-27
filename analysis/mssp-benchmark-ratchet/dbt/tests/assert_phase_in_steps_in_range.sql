{{ config(tags=["enrollment"]) }}
select aco_id
from {{ ref('phase_in') }}
where step < 1 or step > 6 or w_below not in (0.35, 0.50) or w_above not in (0.15, 0.25, 0.35, 0.50)
