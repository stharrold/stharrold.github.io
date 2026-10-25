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
    num(n_ab_year_aged_nondual_py) as py_agnd
from raw;

-- Per-capita expenditure by type (long), PY2019-PY2021 only (BY1-BY3 of a 2022 reset).
create or replace table res_pc as
select py, aco_id, 'ESRD' as type, pc_esrd as pc from res where py between 2019 and 2021
union all select py, aco_id, 'DIS', pc_dis from res where py between 2019 and 2021
union all select py, aco_id, 'AGDU', pc_agdu from res where py between 2019 and 2021
union all select py, aco_id, 'AGND', pc_agnd from res where py between 2019 and 2021;

-- PY2021 person-year share of each type (section 4.3 step 4).
create or replace table shares as
with long as (
    select aco_id, 'ESRD' as type, py_esrd as person_years from res where py = 2021
    union all select aco_id, 'DIS', py_dis from res where py = 2021
    union all select aco_id, 'AGDU', py_agdu from res where py = 2021
    union all select aco_id, 'AGND', py_agnd from res where py = 2021
)
select aco_id, type, person_years / sum(person_years) over (partition by aco_id) as share
from long;
