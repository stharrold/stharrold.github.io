-- Share s of assignable beneficiaries (425.601(a)(5)(v)): sum over counties of (ACO person-years / county assignable
-- person-years), weighted by the ACO's share of its total person-years in each county.
with county_total as (
    select state_id, county_id, sum(person_years) as person_years
    from {{ ref('county') }} where year = 2021 group by state_id, county_id
),
aco_county as (
    select distinct aco_id, state_id, county_id, tot_ab_psn_yrs from {{ ref('assign') }} where tot_ab_psn_yrs > 0
)
select a.aco_id, sum(a.tot_ab_psn_yrs * (a.tot_ab_psn_yrs / t.person_years)) / sum(a.tot_ab_psn_yrs) as s
from aco_county as a
join county_total as t using (state_id, county_id)
where t.person_years > 0
group by a.aco_id
