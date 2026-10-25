-- One row per ACO and enrollment file (sections 2.1, 4.2). Columns absent from older files are NULL.
create or replace table enroll as
with raw as (
    select 2016 as py, * from raw_enroll_2016
    union all by name select 2017 as py, * from raw_enroll_2017
    union all by name select 2018 as py, * from raw_enroll_2018
    union all by name select 2019 as py, * from raw_enroll_2019a
    union all by name select 2019 as py, * from raw_enroll_2019b
    union all by name select 2020 as py, * from raw_enroll_2020
    union all by name select 2021 as py, * from raw_enroll_2021
    union all by name select 2022 as py, * from raw_enroll_2022
    union all by name select 2023 as py, * from raw_enroll_2023
    union all by name select 2024 as py, * from raw_enroll_2024
)
select
    py,
    trim(aco_id) as aco_id,
    cast(num(agreement_period_num) as integer) as period,
    mdy(current_start_date) as start,
    flag(basic_track) as basic,
    nullif(trim(basic_track_level), '') as basic_level,
    flag(enhanced_track) as enhanced,
    flag(high_revenue_aco) as high_revenue,
    flag(prospective_assignment) as prospective
from raw;
