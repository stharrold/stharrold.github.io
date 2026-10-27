-- H4 pre-period (section 4.5): log per-capita spending in PY2020 and PY2021 while in the original agreement, and the
-- person-year weighted mean risk score (missing if a type with positive share has a hidden score). Built in the full
-- stage so the power analysis (section 6) can use the pre-period change before any post-period file is read.
with yearly as (
    select
        r.aco_id, r.py, r.pc_total,
        case when (coalesce(r.py_esrd, 0) = 0 or r.rs_esrd is not null) and (coalesce(r.py_dis, 0) = 0 or r.rs_dis is not null)
              and (coalesce(r.py_agdu, 0) = 0 or r.rs_agdu is not null) and (coalesce(r.py_agnd, 0) = 0 or r.rs_agnd is not null)
             then (coalesce(r.py_esrd * r.rs_esrd, 0) + coalesce(r.py_dis * r.rs_dis, 0) + coalesce(r.py_agdu * r.rs_agdu, 0)
                   + coalesce(r.py_agnd * r.rs_agnd, 0)) / r.py_total end as risk_w
    from {{ ref('res') }} as r
    where r.py in (2020, 2021)
)
select
    g.aco_id, g.grp, g.cohort,
    max(ln(y.pc_total)) filter (where y.py = 2020) as y_2020,
    max(ln(y.pc_total)) filter (where y.py = 2021) as y_2021,
    max(ln(y.pc_total / y.risk_w)) filter (where y.py = 2020) as y_risk_2020,
    max(ln(y.pc_total / y.risk_w)) filter (where y.py = 2021) as y_risk_2021
from {{ ref('groups') }} as g
join yearly as y using (aco_id)
join {{ ref('enroll') }} as e on e.aco_id = g.aco_id and e.py = y.py and e.start = g.start_2021
where g.grp in ('early', 'stayer')
group by g.aco_id, g.grp, g.cohort
