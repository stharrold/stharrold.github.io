-- Phase-in step and regional weights for a 2022 reset (section 4.3 step 3; 42 CFR 425.601(f), 425.603(c)).
-- step = 1 + earlier agreement periods with a regionally adjusted benchmark, counted from distinct start dates in the
-- PY2016-PY2021 enrollment files: renewals starting 2017-01-01 through 2019-01-01, or any start on/after 2019-07-01.
with starts as (
    select distinct aco_id, start, period from {{ ref('enroll') }} where py between 2016 and 2021
),
adjusted as (
    select aco_id, count(distinct start) as n_adjusted
    from starts
    where (start between date '2017-01-01' and date '2019-01-01' and period >= 2) or start >= date '2019-07-01'
    group by aco_id
),
acos as (
    select aco_id from {{ ref('base') }} union select aco_id from {{ ref('validation_sample') }}
)
select
    aco_id,
    1 + coalesce(n_adjusted, 0) as step,
    case when 1 + coalesce(n_adjusted, 0) = 1 then 0.35 else 0.50 end as w_below,
    case 1 + coalesce(n_adjusted, 0) when 1 then 0.15 when 2 then 0.25 when 3 then 0.35 else 0.50 end as w_above
from acos
left join adjusted using (aco_id)
