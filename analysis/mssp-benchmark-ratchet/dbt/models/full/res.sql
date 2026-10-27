-- ACO results by performance year (section 4.1). PY2016-PY2017 use ACO_Num; PY2021 spells Sav_Rate (names are case-insensitive).
with raw as (
    select 2016 as py, aco_num as aco_id, * exclude (aco_num) from {{ source('cms', 'raw_results_2016') }}
    union all by name select 2017 as py, aco_num as aco_id, * exclude (aco_num) from {{ source('cms', 'raw_results_2017') }}
    union all by name select 2018 as py, * from {{ source('cms', 'raw_results_2018') }}
    union all by name select 2019 as py, * from {{ source('cms', 'raw_results_2019') }}
    union all by name select 2020 as py, * from {{ source('cms', 'raw_results_2020') }}
    union all by name select 2021 as py, * from {{ source('cms', 'raw_results_2021') }}
    union all by name select 2022 as py, * from {{ source('cms', 'raw_results_2022') }}
)
select
    py,
    trim(aco_id) as aco_id,
    {{ num('sav_rate') }} as sav_rate,
    {{ num('n_ab') }} as n_ab,
    {{ num('updatedbnchmk') }} as updated_bnchmk,
    {{ num('histbnchmk') }} as hist_bnchmk,
    {{ num('per_capita_exp_all_esrd_py') }} as pc_esrd,
    {{ num('per_capita_exp_all_dis_py') }} as pc_dis,
    {{ num('per_capita_exp_all_agdu_py') }} as pc_agdu,
    {{ num('per_capita_exp_all_agnd_py') }} as pc_agnd,
    {{ num('n_ab_year_esrd_py') }} as py_esrd,
    {{ num('n_ab_year_dis_py') }} as py_dis,
    {{ num('n_ab_year_aged_dual_py') }} as py_agdu,
    {{ num('n_ab_year_aged_nondual_py') }} as py_agnd,
    {{ num('n_ab_year_py') }} as py_total,
    {{ num('per_capita_exp_total_py') }} as pc_total,
    {{ num('cms_hcc_riskscore_esrd_py') }} as rs_esrd,
    {{ num('cms_hcc_riskscore_dis_py') }} as rs_dis,
    {{ num('cms_hcc_riskscore_agdu_py') }} as rs_agdu,
    {{ num('cms_hcc_riskscore_agnd_py') }} as rs_agnd,
    -- Balance (section 5.6): share aged 85+ over the age bins, share female over female + male.
    {{ num('n_ben_age_85plus') }} / ({{ num('n_ben_age_0_64') }} + {{ num('n_ben_age_65_74') }} + {{ num('n_ben_age_75_84') }} + {{ num('n_ben_age_85plus') }}) as share_85plus,
    {{ num('n_ben_female') }} / ({{ num('n_ben_female') }} + {{ num('n_ben_male') }}) as share_female
from raw
