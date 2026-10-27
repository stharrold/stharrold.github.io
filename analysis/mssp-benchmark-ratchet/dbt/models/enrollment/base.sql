-- Base population and groups (section 3), and the validation sample (section 4.4). Enrollment data only.
select
    aco_id,
    start as start_2021,
    case when start = date '2019-07-01' then '2019-07' else '2020-01' end as cohort,
    period as period_2021,
    basic,
    basic_level,
    enhanced,
    high_revenue,
    prospective
from {{ ref('enroll') }}
where py = 2021 and start in (date '2019-07-01', date '2020-01-01')
