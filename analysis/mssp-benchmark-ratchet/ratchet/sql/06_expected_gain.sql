-- Expected benchmark gain from a 2022 reset (section 4.3 steps 1-6), for base ACOs and the validation sample.
-- A type with zero PY2021 share contributes nothing; a type with positive share and an input still missing after the
-- section 3 rules makes the ACO's result missing, so sums below are guarded rather than silently skipping NULLs.

-- Step 1: trend factor to 2021 dollars, s x national growth + (1 - s) x regional growth, with regional growth from
-- risk-standardized regional spending (425.601(a)(5)(iii), (c), (d)).
create or replace table trend as
select
    r.aco_id, r.year, r.type,
    s.s * (n21.pc / n.pc) + (1 - s.s) * (r21.pc_std / r.pc_std) as factor
from region_std as r
join region_std as r21 on r21.aco_id = r.aco_id and r21.type = r.type and r21.year = 2021
join national as n on n.year = r.year and n.type = r.type
join national as n21 on n21.year = 2021 and n21.type = r.type
join share_s as s on s.aco_id = r.aco_id;

-- Step 2: regional spending adjusted to the ACO's own case mix (425.601(a)(8)(i)(C)): risk-standardized regional
-- spending x the ACO's mean prospective CMS-HCC score for the type and year; if that score is hidden, the region's
-- weighted mean county score is used and the value is flagged (section 3).
create or replace table region as
select
    r.aco_id, r.year, r.type,
    r.pc_std * coalesce(p.risk, r.risk) as pc,
    p.risk is null as risk_imputed,
    r.pc_unadjusted
from region_std as r
left join res_pc as p on p.aco_id = r.aco_id and p.py = r.year and p.type = r.type;

-- Step 1: rebased benchmark per type, equal weights over the benchmark years with a results record (BY1 is omitted
-- only when the ACO has no PY2019 record; PY2020 and PY2021 records are required). BY1 and BY2 are restated to BY3
-- case mix by the ratio of the ACO's PY2021 to that year's risk score (425.601(a)(3)); a hidden score leaves the year
-- unrestated and is flagged. Hidden spending (section 3): rule 2, a type shown in some years uses the mean of those
-- years; rule 3, a type hidden in every year uses the region's spending for that type and year times the ACO's
-- own-to-region ratio over its shown types that year.
create or replace table rebased as
with recs as (
    select distinct aco_id, py from res where py between 2019 and 2021
),
cells as (
    select
        r.aco_id, r.py, t.type, p.pc, rg.pc as regional, tr.factor, sh.share,
        p21.risk / p.risk as restate,
        p.risk is null or p21.risk is null as restate_missing
    from recs as r
    cross join (select unnest(['ESRD', 'DIS', 'AGDU', 'AGND']) as type) as t
    left join res_pc as p on p.aco_id = r.aco_id and p.py = r.py and p.type = t.type
    left join res_pc as p21 on p21.aco_id = r.aco_id and p21.py = 2021 and p21.type = t.type
    left join region as rg on rg.aco_id = r.aco_id and rg.year = r.py and rg.type = t.type
    left join trend as tr on tr.aco_id = r.aco_id and tr.year = r.py and tr.type = t.type
    left join shares as sh on sh.aco_id = r.aco_id and sh.type = t.type
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
group by aco_id, type;

-- Inputs per ACO and type, restricted to the ACOs constructed here.
create or replace table gain_inputs as
select
    a.aco_id, a.type, sh.share, rb.pc as rebased, rg.pc as regional, rg.pc_unadjusted as regional_unadjusted, n21.pc as national,
    p.step, p.w_below, p.w_above,
    coalesce(sh.share > 0 and (rb.imputed or rg.risk_imputed), false) or coalesce(sh.share_recovered, false) as imputed
from (select aco_id, type from phase_in cross join (select unnest(['ESRD', 'DIS', 'AGDU', 'AGND']) as type)) as a
join phase_in as p using (aco_id)
left join shares as sh using (aco_id, type)
left join rebased as rb using (aco_id, type)
left join region as rg on rg.aco_id = a.aco_id and rg.type = a.type and rg.year = 2021
left join national as n21 on n21.type = a.type and n21.year = 2021;

-- Steps 3-4: weight depends on whether the ACO's share-weighted spending is below its region's; adjustment capped
-- at +/-5% of national per-capita spending for the type.
create or replace table gain_by_type as
with complete as (
    select
        aco_id,
        bool_and(share is not null and (share = 0 or (rebased is not null and regional is not null and national is not null))) as ok,
        sum(case when share > 0 then share * rebased else 0 end) as rebased_w,
        sum(case when share > 0 then share * regional else 0 end) as regional_w
    from gain_inputs
    group by aco_id
)
select
    g.*,
    c.ok,
    case when c.rebased_w < c.regional_w then g.w_below else g.w_above end as w,
    greatest(least((case when c.rebased_w < c.regional_w then g.w_below else g.w_above end) * (g.regional - g.rebased), 0.05 * g.national), -0.05 * g.national) as adjustment
from gain_inputs as g
join complete as c using (aco_id);

-- Steps 4-6: new benchmark, expected gain and its components, regional pull, in percent of the current benchmark.
create or replace table expected_gain as
with acos as (
    select
        aco_id,
        bool_and(ok) as ok,
        -- Regional pull needs only regional spending, risk scores and shares, not the ACO's own spending (section 4.4).
        bool_and(share is not null and (share = 0 or regional is not null)) as ok_pull,
        bool_and(share is not null and (share = 0 or regional_unadjusted is not null)) as ok_pull_unadjusted,
        any_value(step) as step,
        any_value(w) as w,
        bool_or(imputed) as imputed,
        sum(case when share > 0 then share * rebased else 0 end) as rebased_w,
        sum(case when share > 0 then share * adjustment else 0 end) as adjustment_w,
        sum(case when share > 0 then share * regional else 0 end) as regional_w,
        sum(case when share > 0 then share * regional_unadjusted else 0 end) as regional_unadjusted_w
    from gain_by_type
    group by aco_id
)
select
    a.aco_id, a.step, a.w, a.imputed,
    case when a.ok then a.rebased_w end as rebased_w,
    case when a.ok then a.adjustment_w end as adjustment_w,
    case when a.ok then a.rebased_w + a.adjustment_w end as new_bnchmk,
    r.updated_bnchmk as current_bnchmk,
    case when a.ok then 100 * (a.rebased_w + a.adjustment_w - r.updated_bnchmk) / r.updated_bnchmk end as gain,
    case when a.ok then 100 * (a.rebased_w - r.updated_bnchmk) / r.updated_bnchmk end as own,
    case when a.ok then 100 * a.adjustment_w / r.updated_bnchmk end as regional_comp,
    case when a.ok_pull then 100 * (a.regional_w - r.updated_bnchmk) / r.updated_bnchmk end as pull,
    case when a.ok_pull_unadjusted then 100 * (a.regional_unadjusted_w - r.updated_bnchmk) / r.updated_bnchmk end as pull_unadjusted
from acos as a
left join (select aco_id, updated_bnchmk from res where py = 2021) as r using (aco_id);

-- Step-1 check (section 4.4): the rebased benchmark rebuilt from CMS's BY1-BY3 spending and risk scores with the same
-- trend factors, restatement and shares, for the validation sample.
create or replace table rebased_cms as
with per_type as (
    select
        c.aco_id, c.type, sh.share,
        (c.by1 * t1.factor * c.rs3 / c.rs1 + c.by2 * t2.factor * c.rs3 / c.rs2 + c.by3) / 3 as pc
    from cms_by as c
    left join shares as sh using (aco_id, type)
    left join trend as t1 on t1.aco_id = c.aco_id and t1.type = c.type and t1.year = 2019
    left join trend as t2 on t2.aco_id = c.aco_id and t2.type = c.type and t2.year = 2020
)
select
    aco_id,
    case when bool_and(share is not null and (share = 0 or pc is not null)) then sum(case when share > 0 then share * pc else 0 end) end as rebased_w
from per_type
group by aco_id;
