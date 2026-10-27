-- Regular renewers into 2022 agreements with a PY2021 record; the early renewers are never in this table.
select aco_id
from {{ ref('enroll') }}
where py = 2022 and start = date '2022-01-01' and period >= 2
  and aco_id not in (select aco_id from {{ ref('base') }})
  and aco_id in (select aco_id from {{ ref('enroll') }} where py = 2021)
