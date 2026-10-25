-- CMS's own benchmark-year spending for the validation sample (PY2022 file, already filtered to that sample at load):
-- raw (untrended) per-capita spending by type for BY1-BY3 = 2019-2021, used for the step-1 check (section 4.4).
with wide as (
    select
        trim(aco_id) as aco_id,
        {{ num('per_capita_exp_all_esrd_by1') }} as esrd_1, {{ num('per_capita_exp_all_esrd_by2') }} as esrd_2, {{ num('per_capita_exp_all_esrd_by3') }} as esrd_3,
        {{ num('per_capita_exp_all_dis_by1') }} as dis_1, {{ num('per_capita_exp_all_dis_by2') }} as dis_2, {{ num('per_capita_exp_all_dis_by3') }} as dis_3,
        {{ num('per_capita_exp_all_agdu_by1') }} as agdu_1, {{ num('per_capita_exp_all_agdu_by2') }} as agdu_2, {{ num('per_capita_exp_all_agdu_by3') }} as agdu_3,
        {{ num('per_capita_exp_all_agnd_by1') }} as agnd_1, {{ num('per_capita_exp_all_agnd_by2') }} as agnd_2, {{ num('per_capita_exp_all_agnd_by3') }} as agnd_3,
        {{ num('cms_hcc_riskscore_esrd_by1') }} as rs_esrd_1, {{ num('cms_hcc_riskscore_esrd_by2') }} as rs_esrd_2, {{ num('cms_hcc_riskscore_esrd_by3') }} as rs_esrd_3,
        {{ num('cms_hcc_riskscore_dis_by1') }} as rs_dis_1, {{ num('cms_hcc_riskscore_dis_by2') }} as rs_dis_2, {{ num('cms_hcc_riskscore_dis_by3') }} as rs_dis_3,
        {{ num('cms_hcc_riskscore_agdu_by1') }} as rs_agdu_1, {{ num('cms_hcc_riskscore_agdu_by2') }} as rs_agdu_2, {{ num('cms_hcc_riskscore_agdu_by3') }} as rs_agdu_3,
        {{ num('cms_hcc_riskscore_agnd_by1') }} as rs_agnd_1, {{ num('cms_hcc_riskscore_agnd_by2') }} as rs_agnd_2, {{ num('cms_hcc_riskscore_agnd_by3') }} as rs_agnd_3
    from {{ source('cms', 'raw_results_2022') }}
)
select aco_id, 'ESRD' as type, esrd_1 as by1, esrd_2 as by2, esrd_3 as by3, rs_esrd_1 as rs1, rs_esrd_2 as rs2, rs_esrd_3 as rs3 from wide
union all select aco_id, 'DIS', dis_1, dis_2, dis_3, rs_dis_1, rs_dis_2, rs_dis_3 from wide
union all select aco_id, 'AGDU', agdu_1, agdu_2, agdu_3, rs_agdu_1, rs_agdu_2, rs_agdu_3 from wide
union all select aco_id, 'AGND', agnd_1, agnd_2, agnd_3, rs_agnd_1, rs_agnd_2, rs_agnd_3 from wide
