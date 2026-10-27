-- Regional service area spending by ACO, year and type, weighting counties by the ACO's 2021 person-years of that type
-- (425.601(d)): risk-standardized county spending, county spending / county mean risk score (425.601(c)(4)); the
-- weighted mean county risk score (fallback when the ACO's own score is hidden); and unadjusted spending (robustness).
select
    a.aco_id, c.year, a.type,
    sum(a.ab_person_years * c.pc / c.risk) / sum(a.ab_person_years) as pc_std,
    sum(a.ab_person_years * c.risk) / sum(a.ab_person_years) as risk,
    sum(a.ab_person_years * c.pc) / sum(a.ab_person_years) as pc_unadjusted
from {{ ref('assign') }} as a
join {{ ref('county') }} as c using (state_id, county_id, type)
where a.ab_person_years > 0 and c.pc is not null and c.risk > 0
group by a.aco_id, c.year, a.type
