-- Per-capita spending by agreement year for 5-year agreements (section 5.6, descriptive). Reads the full PY2022 file,
-- so it is built only after the confirmatory results exist (ratchet.run, stage "exploratory").
with raw as (
    select 2020 as py, aco_id, current_start_date, per_capita_exp_total_py from {{ source('cms', 'raw_results_2020') }}
    union all select 2021, aco_id, current_start_date, per_capita_exp_total_py from {{ source('cms', 'raw_results_2021') }}
    union all select 2022, aco_id, current_start_date, per_capita_exp_total_py from {{ source('cms', 'raw_results_2022_all') }}
    union all select 2023, aco_id, current_start_date, per_capita_exp_total_py from {{ source('cms', 'raw_results_2023') }}
    union all select 2024, aco_id, current_start_date, per_capita_exp_total_py from {{ source('cms', 'raw_results_2024') }}
),
rows as (
    select py, trim(aco_id) as aco_id, {{ mdy('current_start_date') }} as start, {{ num('per_capita_exp_total_py') }} as pc
    from raw
)
select
    year(r.start) as start_year,
    r.py - year(r.start) + 1 as agreement_year,
    r.py - year(r.start) + 1 between 3 and 5 as scheduled_benchmark_year,
    coalesce(g.grp = 'early' and g.cohort = '2020-01', false) as early_renewer_from_2020,
    count(r.pc) as n_acos,
    avg(r.pc) as mean_pc
from rows as r
left join {{ ref('groups') }} as g using (aco_id)
where r.start in (date '2020-01-01', date '2021-01-01', date '2022-01-01') and r.py - year(r.start) + 1 between 1 and 5
group by all
order by all
