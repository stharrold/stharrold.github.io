-- Per-capita expenditure and mean prospective CMS-HCC risk score by type (long), PY2019-PY2021 (BY1-BY3 of a 2022 reset).
select py, aco_id, 'ESRD' as type, pc_esrd as pc, rs_esrd as risk from {{ ref('res') }} where py between 2019 and 2021
union all select py, aco_id, 'DIS', pc_dis, rs_dis from {{ ref('res') }} where py between 2019 and 2021
union all select py, aco_id, 'AGDU', pc_agdu, rs_agdu from {{ ref('res') }} where py between 2019 and 2021
union all select py, aco_id, 'AGND', pc_agnd, rs_agnd from {{ ref('res') }} where py between 2019 and 2021
