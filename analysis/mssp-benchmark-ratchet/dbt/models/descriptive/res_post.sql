-- H4 panel (section 4.5): log per-capita spending PY2020-PY2024 for early renewers and stayers, with each year's
-- inclusion status. Reads the full PY2022 file and PY2023-PY2024, so it is built only in the descriptive stage, after
-- the confirmatory results exist.
with raw as (
    select 2022 as py, * from {{ source('cms', 'raw_results_2022_all') }}
    union all by name select 2023 as py, * from {{ source('cms', 'raw_results_2023') }}
    union all by name select 2024 as py, * from {{ source('cms', 'raw_results_2024') }}
)
select
    py,
    trim(aco_id) as aco_id,
    {{ num('per_capita_exp_total_py') }} as pc_total,
    {{ num('n_ab_year_esrd_py') }} as py_esrd, {{ num('n_ab_year_dis_py') }} as py_dis,
    {{ num('n_ab_year_aged_dual_py') }} as py_agdu, {{ num('n_ab_year_aged_nondual_py') }} as py_agnd,
    {{ num('n_ab_year_py') }} as py_total,
    {{ num('cms_hcc_riskscore_esrd_py') }} as rs_esrd, {{ num('cms_hcc_riskscore_dis_py') }} as rs_dis,
    {{ num('cms_hcc_riskscore_agdu_py') }} as rs_agdu, {{ num('cms_hcc_riskscore_agnd_py') }} as rs_agnd
from raw
