-- Analysis frame: one row per base ACO (section 3) with every variable used in sections 5.1-5.4.
create or replace table analysis as
select
    g.aco_id, g.cohort, g.grp,
    g.basic, g.basic_level, g.enhanced,
    g.basic_level in ('C', 'D', 'E') as basic_high,
    g.high_revenue, g.prospective,
    g.period_2021 >= 2 as later_agreement,
    r20.sav_rate as sav_rate_2020,
    r21.sav_rate as sav_rate_2021,
    ln(r20.n_ab) as log_n_ab_2020,
    e.step, e.w, e.gain, e.own, e.regional_comp, e.pull
from groups as g
left join (select * from res where py = 2020) as r20 using (aco_id)
left join (select * from res where py = 2021) as r21 using (aco_id)
left join expected_gain as e using (aco_id);

-- Validation (section 4.4): approximate new benchmark vs PY2022 HistBnchmk, regular renewers only.
create or replace table validation as
select v.aco_id, e.step, e.new_bnchmk as approximate, r.hist_bnchmk as actual
from validation_sample as v
left join expected_gain as e using (aco_id)
left join (select aco_id, hist_bnchmk from res where py = 2022) as r using (aco_id);
