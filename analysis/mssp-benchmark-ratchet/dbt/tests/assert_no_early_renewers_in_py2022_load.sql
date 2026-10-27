-- The PY2022 results file is filtered to the validation sample as it is loaded (section 4.4).
{{ config(tags=["full"]) }}
select r.aco_id
from {{ source('cms', 'raw_results_2022') }} as r
join {{ ref('groups') }} as g on g.aco_id = trim(r.aco_id)
where g.grp = 'early'
