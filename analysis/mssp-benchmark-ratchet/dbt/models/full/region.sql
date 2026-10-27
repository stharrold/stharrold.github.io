-- Step 2: regional spending adjusted to the ACO's own case mix (425.601(a)(8)(i)(C)): risk-standardized regional
-- spending x the ACO's mean prospective CMS-HCC score for the type and year; if that score is hidden, the region's
-- weighted mean county score is used and the value is flagged (section 3).
select
    r.aco_id, r.year, r.type,
    r.pc_std * coalesce(p.risk, r.risk) as pc,
    p.risk is null as risk_imputed,
    r.pc_unadjusted
from {{ ref('region_std') }} as r
left join {{ ref('res_pc') }} as p on p.aco_id = r.aco_id and p.py = r.year and p.type = r.type
