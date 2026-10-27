-- ACO assigned person-years by county and type, 2021 (BY3 proxy).
with wide as (
    select
        trim(aco_id) as aco_id,
        trim(state_name) as state_name,
        cast({{ num('state_id') }} as integer) as state_id,
        cast({{ num('county_id') }} as integer) as county_id,
        {{ num('ab_psn_yrs_esrd') }} as esrd, {{ num('ab_psn_yrs_dis') }} as dis, {{ num('ab_psn_yrs_agdu') }} as agdu, {{ num('ab_psn_yrs_agnd') }} as agnd,
        {{ num('tot_ab_psn_yrs') }} as tot_ab_psn_yrs
    from {{ source('cms', 'raw_assign_2021') }}
)
select aco_id, state_name, state_id, county_id, tot_ab_psn_yrs, 'ESRD' as type, esrd as ab_person_years from wide
union all select aco_id, state_name, state_id, county_id, tot_ab_psn_yrs, 'DIS', dis from wide
union all select aco_id, state_name, state_id, county_id, tot_ab_psn_yrs, 'AGDU', agdu from wide
union all select aco_id, state_name, state_id, county_id, tot_ab_psn_yrs, 'AGND', agnd from wide
