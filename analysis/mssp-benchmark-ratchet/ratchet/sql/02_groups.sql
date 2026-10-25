-- Base population and groups (section 3), and the validation sample (section 4.4). Enrollment data only.
create or replace table base as
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
from enroll
where py = 2021 and start in (date '2019-07-01', date '2020-01-01');

create or replace table groups as
select
    b.*,
    case
        when e.aco_id is null then 'leaver'
        when e.start = date '2022-01-01' then 'early'
        when e.start = b.start_2021 then 'stayer'
        else 'other'
    end as grp,
    e.enhanced as enhanced_2022
from base as b
left join (select * from enroll where py = 2022) as e using (aco_id);

-- Regular renewers into 2022 agreements with a PY2021 record; the early renewers are never in this table.
create or replace table validation_sample as
select aco_id
from enroll
where py = 2022 and start = date '2022-01-01' and period >= 2
  and aco_id not in (select aco_id from base)
  and aco_id in (select aco_id from enroll where py = 2021);
