select
    b.*,
    case
        when e.aco_id is null then 'leaver'
        when e.start = date '2022-01-01' then 'early'
        when e.start = b.start_2021 then 'stayer'
        else 'other'
    end as grp,
    e.enhanced as enhanced_2022
from {{ ref('base') }} as b
left join (select * from {{ ref('enroll') }} where py = 2022) as e using (aco_id)
