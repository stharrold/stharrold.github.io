{{ config(tags=["descriptive"]) }}
select aco_id, py
from {{ ref('did_panel') }}
group by aco_id, py
having count(*) > 1
