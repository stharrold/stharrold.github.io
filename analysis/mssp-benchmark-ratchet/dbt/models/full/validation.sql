-- Validation (section 4.4): approximate new benchmark vs PY2022 HistBnchmk, regular renewers only.
select v.aco_id, e.step, e.new_bnchmk as approximate, r.hist_bnchmk as actual,
    e.rebased_w as rebased_approximate, c.rebased_w as rebased_cms, e.current_bnchmk
from {{ ref('validation_sample') }} as v
left join {{ ref('expected_gain') }} as e using (aco_id)
left join {{ ref('rebased_cms') }} as c using (aco_id)
left join (select aco_id, hist_bnchmk from {{ ref('res') }} where py = 2022) as r using (aco_id)
