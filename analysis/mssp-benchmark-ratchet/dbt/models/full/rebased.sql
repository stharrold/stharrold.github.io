-- Step 1: rebased benchmark per type, equal weights over the benchmark years with a results record (BY1 is omitted
-- only when the ACO has no PY2019 record; PY2020 and PY2021 records are required). Benchmark years start at
-- getvariable('by_first'): 2019, or 2020 for robustness item 6 (section 5.5). BY1 and BY2 are restated to BY3
-- case mix by the ratio of the ACO's PY2021 to that year's risk score (425.601(a)(3)); a hidden score leaves the year
-- unrestated and is flagged. Hidden spending (section 3): rule 2, a type shown in some years uses the mean of those
-- years; rule 3, a type hidden in every year uses the region's spending for that type and year times the ACO's
-- own-to-region ratio over its shown types that year.
with recs as (
    select distinct aco_id, py from {{ ref('res') }} where py between {{ var('by_first') }} and 2021
),
cells as (
    select
        r.aco_id, r.py, t.type, p.pc, rg.pc as regional, tr.factor, sh.share,
        p21.risk / p.risk as restate,
        p.risk is null or p21.risk is null as restate_missing
    from recs as r
    cross join (select unnest(['ESRD', 'DIS', 'AGDU', 'AGND']) as type) as t
    left join {{ ref('res_pc') }} as p on p.aco_id = r.aco_id and p.py = r.py and p.type = t.type
    left join {{ ref('res_pc') }} as p21 on p21.aco_id = r.aco_id and p21.py = 2021 and p21.type = t.type
    left join {{ ref('region') }} as rg on rg.aco_id = r.aco_id and rg.year = r.py and rg.type = t.type
    left join {{ ref('trend') }} as tr on tr.aco_id = r.aco_id and tr.year = r.py and tr.type = t.type
    left join {{ ref('shares') }} as sh on sh.aco_id = r.aco_id and sh.type = t.type
),
ratio as (
    select aco_id, py, sum(share * pc) / sum(share * regional) as ratio
    from cells
    where share > 0 and pc is not null and regional is not null
    group by aco_id, py
),
shown as (
    select aco_id, type, count(pc) as n_shown from cells group by aco_id, type
),
filled as (
    select
        c.aco_id, c.py, c.type, c.factor,
        coalesce(c.restate, 1) as restate,
        case when s.n_shown > 0 then c.pc else c.regional * q.ratio end as pc,
        s.n_shown = 0 or c.pc is null or c.restate_missing as imputed
    from cells as c
    join shown as s using (aco_id, type)
    left join ratio as q using (aco_id, py)
)
select
    aco_id, type,
    case when bool_or(py = 2020) and bool_or(py = 2021) and count(pc * factor) > 0 then avg(pc * factor * restate) end as pc,
    bool_or(imputed) as imputed
from filled
group by aco_id, type
