-- Step-1 check (section 4.4): the rebased benchmark rebuilt from CMS's BY1-BY3 spending and risk scores with the same
-- trend factors, restatement and shares, for the validation sample.
with per_type as (
    select
        c.aco_id, c.type, sh.share,
        (c.by1 * t1.factor * c.rs3 / c.rs1 + c.by2 * t2.factor * c.rs3 / c.rs2 + c.by3) / 3 as pc
    from {{ ref('cms_by') }} as c
    left join {{ ref('shares') }} as sh using (aco_id, type)
    left join {{ ref('trend') }} as t1 on t1.aco_id = c.aco_id and t1.type = c.type and t1.year = 2019
    left join {{ ref('trend') }} as t2 on t2.aco_id = c.aco_id and t2.type = c.type and t2.year = 2020
)
select
    aco_id,
    case when bool_and(share is not null and (share = 0 or pc is not null)) then sum(case when share > 0 then share * pc else 0 end) end as rebased_w
from per_type
group by aco_id
