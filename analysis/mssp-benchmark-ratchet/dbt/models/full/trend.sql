-- Expected benchmark gain from a 2022 reset (section 4.3 steps 1-6), for base ACOs and the validation sample.
-- A type with zero PY2021 share contributes nothing; a type with positive share and an input still missing after the
-- section 3 rules makes the ACO's result missing, so sums below are guarded rather than silently skipping NULLs.
-- Step 1: trend factor to 2021 dollars, s x national growth + (1 - s) x regional growth, with regional growth from
-- risk-standardized regional spending (425.601(a)(5)(iii), (c), (d)).
select
    r.aco_id, r.year, r.type,
    s.s * (n21.pc / n.pc) + (1 - s.s) * (r21.pc_std / r.pc_std) as factor
from {{ ref('region_std') }} as r
join {{ ref('region_std') }} as r21 on r21.aco_id = r.aco_id and r21.type = r.type and r21.year = 2021
join {{ ref('national') }} as n on n.year = r.year and n.type = r.type
join {{ ref('national') }} as n21 on n21.year = 2021 and n21.type = r.type
join {{ ref('share_s') }} as s on s.aco_id = r.aco_id
