-- County spending, national means, regional service area spending, and the share s (section 4.3 steps 1-2).
create or replace table county as
with raw as (
    select 2019 as year, * exclude (year) from raw_county_2019
    union all by name select 2020 as year, * exclude (year) from raw_county_2020
    union all by name select 2021 as year, * exclude (year) from raw_county_2021
),
wide as (
    select
        year,
        cast(num(state_id) as integer) as state_id,
        cast(num(county_id) as integer) as county_id,
        num(per_capita_exp_esrd) as pc_esrd, num(person_years_esrd) as py_esrd, num(avg_risk_score_esrd) as rs_esrd,
        num(per_capita_exp_dis) as pc_dis, num(person_years_dis) as py_dis, num(avg_risk_score_dis) as rs_dis,
        num(per_capita_exp_agdu) as pc_agdu, num(person_years_agdu) as py_agdu, num(avg_risk_score_agdu) as rs_agdu,
        num(per_capita_exp_agnd) as pc_agnd, num(person_years_agnd) as py_agnd, num(avg_risk_score_agnd) as rs_agnd
    from raw
)
select year, state_id, county_id, 'ESRD' as type, pc_esrd as pc, py_esrd as person_years, rs_esrd as risk from wide
union all select year, state_id, county_id, 'DIS', pc_dis, py_dis, rs_dis from wide
union all select year, state_id, county_id, 'AGDU', pc_agdu, py_agdu, rs_agdu from wide
union all select year, state_id, county_id, 'AGND', pc_agnd, py_agnd, rs_agnd from wide;

-- National per-capita spending: assignable person-year weighted mean over counties with both values.
create or replace table national as
select year, type, sum(pc * person_years) / sum(person_years) as pc
from county
where pc is not null and person_years > 0
group by year, type;

-- ACO assigned person-years by county and type, 2021 (BY3 proxy).
create or replace table assign as
with wide as (
    select
        trim(aco_id) as aco_id,
        cast(num(state_id) as integer) as state_id,
        cast(num(county_id) as integer) as county_id,
        num(ab_psn_yrs_esrd) as esrd, num(ab_psn_yrs_dis) as dis, num(ab_psn_yrs_agdu) as agdu, num(ab_psn_yrs_agnd) as agnd,
        num(tot_ab_psn_yrs) as tot_ab_psn_yrs
    from raw_assign_2021
)
select aco_id, state_id, county_id, tot_ab_psn_yrs, 'ESRD' as type, esrd as ab_person_years from wide
union all select aco_id, state_id, county_id, tot_ab_psn_yrs, 'DIS', dis from wide
union all select aco_id, state_id, county_id, tot_ab_psn_yrs, 'AGDU', agdu from wide
union all select aco_id, state_id, county_id, tot_ab_psn_yrs, 'AGND', agnd from wide;

-- Regional service area spending by ACO, year and type, weighting counties by the ACO's 2021 person-years of that type
-- (425.601(d)): risk-standardized county spending, county spending / county mean risk score (425.601(c)(4)); the
-- weighted mean county risk score (fallback when the ACO's own score is hidden); and unadjusted spending (robustness).
create or replace table region_std as
select
    a.aco_id, c.year, a.type,
    sum(a.ab_person_years * c.pc / c.risk) / sum(a.ab_person_years) as pc_std,
    sum(a.ab_person_years * c.risk) / sum(a.ab_person_years) as risk,
    sum(a.ab_person_years * c.pc) / sum(a.ab_person_years) as pc_unadjusted
from assign as a
join county as c using (state_id, county_id, type)
where a.ab_person_years > 0 and c.pc is not null and c.risk > 0
group by a.aco_id, c.year, a.type;

-- Share s of assignable beneficiaries (425.601(a)(5)(v)): sum over counties of (ACO person-years / county assignable
-- person-years), weighted by the ACO's share of its total person-years in each county.
create or replace table share_s as
with county_total as (
    select state_id, county_id, sum(person_years) as person_years
    from county where year = 2021 group by state_id, county_id
),
aco_county as (
    select distinct aco_id, state_id, county_id, tot_ab_psn_yrs from assign where tot_ab_psn_yrs > 0
)
select a.aco_id, sum(a.tot_ab_psn_yrs * (a.tot_ab_psn_yrs / t.person_years)) / sum(a.tot_ab_psn_yrs) as s
from aco_county as a
join county_total as t using (state_id, county_id)
where t.person_years > 0
group by a.aco_id;
