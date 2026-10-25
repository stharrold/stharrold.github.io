-- ACO results by performance year (section 4.1). PY2016-PY2017 use ACO_Num; PY2021 spells Sav_Rate (names are case-insensitive).
create or replace table res as
with raw as (
    select 2016 as py, aco_num as aco_id, * exclude (aco_num) from raw_results_2016
    union all by name select 2017 as py, aco_num as aco_id, * exclude (aco_num) from raw_results_2017
    union all by name select 2018 as py, * from raw_results_2018
    union all by name select 2019 as py, * from raw_results_2019
    union all by name select 2020 as py, * from raw_results_2020
    union all by name select 2021 as py, * from raw_results_2021
    union all by name select 2022 as py, * from raw_results_2022
)
select
    py,
    trim(aco_id) as aco_id,
    num(sav_rate) as sav_rate,
    num(n_ab) as n_ab,
    num(updatedbnchmk) as updated_bnchmk,
    num(histbnchmk) as hist_bnchmk,
    num(per_capita_exp_all_esrd_py) as pc_esrd,
    num(per_capita_exp_all_dis_py) as pc_dis,
    num(per_capita_exp_all_agdu_py) as pc_agdu,
    num(per_capita_exp_all_agnd_py) as pc_agnd,
    num(n_ab_year_esrd_py) as py_esrd,
    num(n_ab_year_dis_py) as py_dis,
    num(n_ab_year_aged_dual_py) as py_agdu,
    num(n_ab_year_aged_nondual_py) as py_agnd,
    num(n_ab_year_py) as py_total,
    num(cms_hcc_riskscore_esrd_py) as rs_esrd,
    num(cms_hcc_riskscore_dis_py) as rs_dis,
    num(cms_hcc_riskscore_agdu_py) as rs_agdu,
    num(cms_hcc_riskscore_agnd_py) as rs_agnd,
    -- Balance (section 5.6): share aged 85+ over the age bins, share female over female + male.
    num(n_ben_age_85plus) / (num(n_ben_age_0_64) + num(n_ben_age_65_74) + num(n_ben_age_75_84) + num(n_ben_age_85plus)) as share_85plus,
    num(n_ben_female) / (num(n_ben_female) + num(n_ben_male)) as share_female
from raw;

-- Per-capita expenditure and mean prospective CMS-HCC risk score by type (long), PY2019-PY2021 (BY1-BY3 of a 2022 reset).
create or replace table res_pc as
select py, aco_id, 'ESRD' as type, pc_esrd as pc, rs_esrd as risk from res where py between 2019 and 2021
union all select py, aco_id, 'DIS', pc_dis, rs_dis from res where py between 2019 and 2021
union all select py, aco_id, 'AGDU', pc_agdu, rs_agdu from res where py between 2019 and 2021
union all select py, aco_id, 'AGND', pc_agnd, rs_agnd from res where py between 2019 and 2021;

-- PY2021 person-year share of each type (section 4.3 step 4). A single hidden type is recovered exactly as the total
-- (N_AB_Year_PY) minus the other three; with two or more hidden, the shares are unknown and the ACO is excluded.
create or replace table shares as
with long as (
    select aco_id, 'ESRD' as type, py_esrd as person_years, py_total from res where py = 2021
    union all select aco_id, 'DIS', py_dis, py_total from res where py = 2021
    union all select aco_id, 'AGDU', py_agdu, py_total from res where py = 2021
    union all select aco_id, 'AGND', py_agnd, py_total from res where py = 2021
),
counts as (
    select aco_id, count(*) filter (where person_years is null) as n_hidden, sum(person_years) as known, any_value(py_total) as total
    from long group by aco_id
),
filled as (
    select
        l.aco_id, l.type,
        case when l.person_years is null and c.n_hidden = 1 then greatest(c.total - c.known, 0) else l.person_years end as person_years,
        l.person_years is null and c.n_hidden = 1 and c.total is not null as share_recovered
    from long as l join counts as c using (aco_id)
)
select aco_id, type, person_years / sum(person_years) over (partition by aco_id) as share, share_recovered
from filled;

-- CMS's own benchmark-year spending for the validation sample (PY2022 file, already filtered to that sample at load):
-- raw (untrended) per-capita spending by type for BY1-BY3 = 2019-2021, used for the step-1 check (section 4.4).
create or replace table cms_by as
with wide as (
    select
        trim(aco_id) as aco_id,
        num(per_capita_exp_all_esrd_by1) as esrd_1, num(per_capita_exp_all_esrd_by2) as esrd_2, num(per_capita_exp_all_esrd_by3) as esrd_3,
        num(per_capita_exp_all_dis_by1) as dis_1, num(per_capita_exp_all_dis_by2) as dis_2, num(per_capita_exp_all_dis_by3) as dis_3,
        num(per_capita_exp_all_agdu_by1) as agdu_1, num(per_capita_exp_all_agdu_by2) as agdu_2, num(per_capita_exp_all_agdu_by3) as agdu_3,
        num(per_capita_exp_all_agnd_by1) as agnd_1, num(per_capita_exp_all_agnd_by2) as agnd_2, num(per_capita_exp_all_agnd_by3) as agnd_3,
        num(cms_hcc_riskscore_esrd_by1) as rs_esrd_1, num(cms_hcc_riskscore_esrd_by2) as rs_esrd_2, num(cms_hcc_riskscore_esrd_by3) as rs_esrd_3,
        num(cms_hcc_riskscore_dis_by1) as rs_dis_1, num(cms_hcc_riskscore_dis_by2) as rs_dis_2, num(cms_hcc_riskscore_dis_by3) as rs_dis_3,
        num(cms_hcc_riskscore_agdu_by1) as rs_agdu_1, num(cms_hcc_riskscore_agdu_by2) as rs_agdu_2, num(cms_hcc_riskscore_agdu_by3) as rs_agdu_3,
        num(cms_hcc_riskscore_agnd_by1) as rs_agnd_1, num(cms_hcc_riskscore_agnd_by2) as rs_agnd_2, num(cms_hcc_riskscore_agnd_by3) as rs_agnd_3
    from raw_results_2022
)
select aco_id, 'ESRD' as type, esrd_1 as by1, esrd_2 as by2, esrd_3 as by3, rs_esrd_1 as rs1, rs_esrd_2 as rs2, rs_esrd_3 as rs3 from wide
union all select aco_id, 'DIS', dis_1, dis_2, dis_3, rs_dis_1, rs_dis_2, rs_dis_3 from wide
union all select aco_id, 'AGDU', agdu_1, agdu_2, agdu_3, rs_agdu_1, rs_agdu_2, rs_agdu_3 from wide
union all select aco_id, 'AGND', agnd_1, agnd_2, agnd_3, rs_agnd_1, rs_agnd_2, rs_agnd_3 from wide;
