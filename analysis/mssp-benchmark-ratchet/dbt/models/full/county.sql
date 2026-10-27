-- County spending, national means, regional service area spending, and the share s (section 4.3 steps 1-2).
with raw as (
    select 2019 as year, * exclude (year) from {{ source('cms', 'raw_county_2019') }}
    union all by name select 2020 as year, * exclude (year) from {{ source('cms', 'raw_county_2020') }}
    union all by name select 2021 as year, * exclude (year) from {{ source('cms', 'raw_county_2021') }}
),
wide as (
    select
        year,
        cast({{ num('state_id') }} as integer) as state_id,
        cast({{ num('county_id') }} as integer) as county_id,
        {{ num('per_capita_exp_esrd') }} as pc_esrd, {{ num('person_years_esrd') }} as py_esrd, {{ num('avg_risk_score_esrd') }} as rs_esrd,
        {{ num('per_capita_exp_dis') }} as pc_dis, {{ num('person_years_dis') }} as py_dis, {{ num('avg_risk_score_dis') }} as rs_dis,
        {{ num('per_capita_exp_agdu') }} as pc_agdu, {{ num('person_years_agdu') }} as py_agdu, {{ num('avg_risk_score_agdu') }} as rs_agdu,
        {{ num('per_capita_exp_agnd') }} as pc_agnd, {{ num('person_years_agnd') }} as py_agnd, {{ num('avg_risk_score_agnd') }} as rs_agnd
    from raw
)
select year, state_id, county_id, 'ESRD' as type, pc_esrd as pc, py_esrd as person_years, rs_esrd as risk from wide
union all select year, state_id, county_id, 'DIS', pc_dis, py_dis, rs_dis from wide
union all select year, state_id, county_id, 'AGDU', pc_agdu, py_agdu, rs_agdu from wide
union all select year, state_id, county_id, 'AGND', pc_agnd, py_agnd, rs_agnd from wide
