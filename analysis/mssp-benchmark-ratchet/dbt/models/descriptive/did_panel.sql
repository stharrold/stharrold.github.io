with yearly as (
    select
        py, aco_id, pc_total,
        case when (coalesce(py_esrd, 0) = 0 or rs_esrd is not null) and (coalesce(py_dis, 0) = 0 or rs_dis is not null)
              and (coalesce(py_agdu, 0) = 0 or rs_agdu is not null) and (coalesce(py_agnd, 0) = 0 or rs_agnd is not null)
             then (coalesce(py_esrd * rs_esrd, 0) + coalesce(py_dis * rs_dis, 0) + coalesce(py_agdu * rs_agdu, 0)
                   + coalesce(py_agnd * rs_agnd, 0)) / py_total end as risk_w
    from (
        select py, aco_id, pc_total, py_esrd, py_dis, py_agdu, py_agnd, py_total, rs_esrd, rs_dis, rs_agdu, rs_agnd
        from {{ ref('res') }} where py in (2020, 2021)
        union all
        select py, aco_id, pc_total, py_esrd, py_dis, py_agdu, py_agnd, py_total, rs_esrd, rs_dis, rs_agdu, rs_agnd
        from {{ ref('res_post') }}
    )
),
grid as (
    select g.aco_id, g.grp, g.cohort, g.start_2021, t.py
    from {{ ref('groups') }} as g
    cross join (select unnest([2020, 2021, 2022, 2023, 2024]) as py) as t
    where g.grp in ('early', 'stayer')
)
select
    grid.aco_id, grid.grp, grid.cohort, grid.py,
    grid.py >= 2022 as post,
    ln(y.pc_total) as y,
    ln(y.pc_total / y.risk_w) as y_risk,
    case
        when e.aco_id is null then 'absent'
        when e.start <> case when grid.py >= 2022 and grid.grp = 'early' then date '2022-01-01' else grid.start_2021 end then 'later renewal'
        when y.pc_total is null then 'no spending value'
        else 'included'
    end as status
from grid
left join {{ ref('enroll') }} as e on e.aco_id = grid.aco_id and e.py = grid.py
left join yearly as y on y.aco_id = grid.aco_id and y.py = grid.py
