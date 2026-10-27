-- Steps 4-6: new benchmark, expected gain and its components, regional pull, in percent of the current benchmark.
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
    from {{ ref('gain_by_type') }}
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
left join (select aco_id, updated_bnchmk from {{ ref('res') }} where py = 2021) as r using (aco_id)
