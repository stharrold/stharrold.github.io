-- Analysis frame: one row per base ACO (section 3) with every variable used in sections 5.1-5.4.
create or replace table analysis as
select
    g.aco_id, g.cohort, g.grp,
    g.basic, g.basic_level, g.enhanced,
    g.basic_level in ('C', 'D', 'E') as basic_high,
    g.high_revenue, g.prospective,
    g.period_2021 >= 2 as later_agreement,
    cr.region as census_region,
    r20.share_85plus as share_85plus_2020,
    r20.share_female as share_female_2020,
    g.enhanced_2022,
    r20.sav_rate as sav_rate_2020,
    r21.sav_rate as sav_rate_2021,
    ln(r20.n_ab) as log_n_ab_2020,
    e.step, e.w, e.gain, e.own, e.regional_comp, e.pull, e.pull_unadjusted,
    e.rebased_w, e.adjustment_w, e.current_bnchmk, e.imputed
from groups as g
left join (select * from res where py = 2020) as r20 using (aco_id)
left join (select * from res where py = 2021) as r21 using (aco_id)
left join expected_gain as e using (aco_id)
left join census_region as cr using (aco_id);

-- Validation (section 4.4): approximate new benchmark vs PY2022 HistBnchmk, regular renewers only.
create or replace table validation as
select v.aco_id, e.step, e.new_bnchmk as approximate, r.hist_bnchmk as actual,
    e.rebased_w as rebased_approximate, c.rebased_w as rebased_cms, e.current_bnchmk
from validation_sample as v
left join expected_gain as e using (aco_id)
left join rebased_cms as c using (aco_id)
left join (select aco_id, hist_bnchmk from res where py = 2022) as r using (aco_id);

-- H4 pre-period (section 4.5): log per-capita spending in PY2020 and PY2021 while in the original agreement, and the
-- person-year weighted mean risk score (missing if a type with positive share has a hidden score). Built in the full
-- stage so the power analysis (section 6) can use the pre-period change before any post-period file is read.
create or replace table did_pre as
with yearly as (
    select
        r.aco_id, r.py, r.pc_total,
        case when (coalesce(r.py_esrd, 0) = 0 or r.rs_esrd is not null) and (coalesce(r.py_dis, 0) = 0 or r.rs_dis is not null)
              and (coalesce(r.py_agdu, 0) = 0 or r.rs_agdu is not null) and (coalesce(r.py_agnd, 0) = 0 or r.rs_agnd is not null)
             then (coalesce(r.py_esrd * r.rs_esrd, 0) + coalesce(r.py_dis * r.rs_dis, 0) + coalesce(r.py_agdu * r.rs_agdu, 0)
                   + coalesce(r.py_agnd * r.rs_agnd, 0)) / r.py_total end as risk_w
    from res as r
    where r.py in (2020, 2021)
)
select
    g.aco_id, g.grp, g.cohort,
    max(ln(y.pc_total)) filter (where y.py = 2020) as y_2020,
    max(ln(y.pc_total)) filter (where y.py = 2021) as y_2021,
    max(ln(y.pc_total / y.risk_w)) filter (where y.py = 2020) as y_risk_2020,
    max(ln(y.pc_total / y.risk_w)) filter (where y.py = 2021) as y_risk_2021
from groups as g
join yearly as y using (aco_id)
join enroll as e on e.aco_id = g.aco_id and e.py = y.py and e.start = g.start_2021
where g.grp in ('early', 'stayer')
group by g.aco_id, g.grp, g.cohort;
