-- Steps 3-4: weight depends on whether the ACO's share-weighted spending is below its region's; adjustment capped
-- at +/-5% of national per-capita spending for the type.
with complete as (
    select
        aco_id,
        bool_and(share is not null and (share = 0 or (rebased is not null and regional is not null and national is not null))) as ok,
        sum(case when share > 0 then share * rebased else 0 end) as rebased_w,
        sum(case when share > 0 then share * regional else 0 end) as regional_w
    from {{ ref('gain_inputs') }}
    group by aco_id
)
select
    g.*,
    c.ok,
    case when c.rebased_w < c.regional_w then g.w_below else g.w_above end as w,
    greatest(least((case when c.rebased_w < c.regional_w then g.w_below else g.w_above end) * (g.regional - g.rebased), 0.05 * g.national), -0.05 * g.national) as adjustment
from {{ ref('gain_inputs') }} as g
join complete as c using (aco_id)
