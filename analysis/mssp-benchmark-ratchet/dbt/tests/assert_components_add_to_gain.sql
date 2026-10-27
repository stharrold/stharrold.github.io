-- Own-spending component + regional component = expected gain (section 4.3 step 5).
{{ config(tags=["full"]) }}
select aco_id
from {{ ref('expected_gain') }}
where gain is not null and abs(own + regional_comp - gain) > 1e-9
