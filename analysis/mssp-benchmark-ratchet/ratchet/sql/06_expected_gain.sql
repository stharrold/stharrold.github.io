-- Expected benchmark gain from a 2022 reset (section 4.3 steps 1-6), for base ACOs and the validation sample.
-- A type with zero PY2021 share contributes nothing; a type with positive share and a missing input makes the ACO's
-- result missing (section 3), so sums below are guarded rather than silently skipping NULLs.

-- Step 1: trend factor to 2021 dollars, s x national growth + (1 - s) x regional growth.
create or replace table trend as
select
    r.aco_id, r.year, r.type,
    s.s * (n21.pc / n.pc) + (1 - s.s) * (r21.pc / r.pc) as factor
from region as r
join region as r21 on r21.aco_id = r.aco_id and r21.type = r.type and r21.year = 2021
join national as n on n.year = r.year and n.type = r.type
join national as n21 on n21.year = 2021 and n21.type = r.type
join share_s as s on s.aco_id = r.aco_id;

-- Step 1: rebased benchmark per type, equal weights over BY1-BY3; BY1 is omitted only when the ACO has no PY2019 record.
create or replace table rebased as
with trended as (
    select p.aco_id, p.type, p.py, p.pc * t.factor as pc_2021
    from res_pc as p
    left join trend as t on t.aco_id = p.aco_id and t.type = p.type and t.year = p.py
),
wide as (
    select
        aco_id, type,
        max(pc_2021) filter (where py = 2019) as by1,
        max(pc_2021) filter (where py = 2020) as by2,
        max(pc_2021) filter (where py = 2021) as by3,
        bool_or(py = 2019) as has_py2019
    from trended
    group by aco_id, type
)
select aco_id, type, case when has_py2019 then (by1 + by2 + by3) / 3 else (by2 + by3) / 2 end as pc
from wide;

-- Inputs per ACO and type, restricted to the ACOs constructed here.
create or replace table gain_inputs as
select
    a.aco_id, a.type, sh.share, rb.pc as rebased, rg.pc as regional, n21.pc as national,
    p.step, p.w_below, p.w_above
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
        -- Regional pull needs only regional spending and shares, not the ACO's own BY1-BY3 spending (section 4.4).
        bool_and(share is not null and (share = 0 or regional is not null)) as ok_pull,
        any_value(step) as step,
        any_value(w) as w,
        sum(case when share > 0 then share * rebased else 0 end) as rebased_w,
        sum(case when share > 0 then share * adjustment else 0 end) as adjustment_w,
        sum(case when share > 0 then share * regional else 0 end) as regional_w
    from gain_by_type
    group by aco_id
)
select
    a.aco_id, a.step, a.w,
    case when a.ok then a.rebased_w end as rebased_w,
    case when a.ok then a.adjustment_w end as adjustment_w,
    case when a.ok then a.rebased_w + a.adjustment_w end as new_bnchmk,
    r.updated_bnchmk as current_bnchmk,
    case when a.ok then 100 * (a.rebased_w + a.adjustment_w - r.updated_bnchmk) / r.updated_bnchmk end as gain,
    case when a.ok then 100 * (a.rebased_w - r.updated_bnchmk) / r.updated_bnchmk end as own,
    case when a.ok then 100 * a.adjustment_w / r.updated_bnchmk end as regional_comp,
    case when a.ok_pull then 100 * (a.regional_w - r.updated_bnchmk) / r.updated_bnchmk end as pull
from acos as a
left join (select aco_id, updated_bnchmk from res where py = 2021) as r using (aco_id);
