-- Inputs per ACO and type, restricted to the ACOs constructed here.
select
    a.aco_id, a.type, sh.share, rb.pc as rebased, rg.pc as regional, rg.pc_unadjusted as regional_unadjusted, n21.pc as national,
    p.step, p.w_below, p.w_above,
    coalesce(sh.share > 0 and (rb.imputed or rg.risk_imputed), false) or coalesce(sh.share_recovered, false) as imputed
from (select aco_id, type from {{ ref('phase_in') }} cross join (select unnest(['ESRD', 'DIS', 'AGDU', 'AGND']) as type)) as a
join {{ ref('phase_in') }} as p using (aco_id)
left join {{ ref('shares') }} as sh using (aco_id, type)
left join {{ ref('rebased') }} as rb using (aco_id, type)
left join {{ ref('region') }} as rg on rg.aco_id = a.aco_id and rg.type = a.type and rg.year = 2021
left join {{ ref('national') }} as n21 on n21.type = a.type and n21.year = 2021
