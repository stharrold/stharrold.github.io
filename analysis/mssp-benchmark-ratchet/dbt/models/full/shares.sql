-- PY2021 person-year share of each type (section 4.3 step 4). A single hidden type is recovered exactly as the total
-- (N_AB_Year_PY) minus the other three; with two or more hidden, the shares are unknown and the ACO is excluded.
with long as (
    select aco_id, 'ESRD' as type, py_esrd as person_years, py_total from {{ ref('res') }} where py = 2021
    union all select aco_id, 'DIS', py_dis, py_total from {{ ref('res') }} where py = 2021
    union all select aco_id, 'AGDU', py_agdu, py_total from {{ ref('res') }} where py = 2021
    union all select aco_id, 'AGND', py_agnd, py_total from {{ ref('res') }} where py = 2021
),
counts as (
    select aco_id, count(*) filter (where person_years is null) as n_hidden, sum(person_years) as known, any_value(py_total) as total
    from long group by aco_id
),
filled as (
    select
        l.aco_id, l.type,
        case when l.person_years is null and c.n_hidden = 1 then greatest(c.total - c.known, 0) else l.person_years end as person_years,
        l.person_years is null and c.n_hidden = 1 and c.total is not null as share_recovered
    from long as l join counts as c using (aco_id)
)
select aco_id, type, person_years / sum(person_years) over (partition by aco_id) as share, share_recovered
from filled
