-- Analysis frame: one row per base ACO (section 3) with every variable used in sections 5.1-5.4.
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
from {{ ref('groups') }} as g
left join (select * from {{ ref('res') }} where py = 2020) as r20 using (aco_id)
left join (select * from {{ ref('res') }} where py = 2021) as r21 using (aco_id)
left join {{ ref('expected_gain') }} as e using (aco_id)
left join {{ ref('census_region') }} as cr using (aco_id)
