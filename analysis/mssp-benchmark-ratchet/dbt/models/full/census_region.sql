-- Census region of each ACO (section 5.6): the region with the largest share of its 2021 assigned person-years.
-- States are matched by name; territories and unmatched names have no region.
with states(state_name, region) as (values
    ('Connecticut', 'Northeast'), ('Maine', 'Northeast'), ('Massachusetts', 'Northeast'), ('New Hampshire', 'Northeast'),
    ('Rhode Island', 'Northeast'), ('Vermont', 'Northeast'), ('New Jersey', 'Northeast'), ('New York', 'Northeast'),
    ('Pennsylvania', 'Northeast'),
    ('Illinois', 'Midwest'), ('Indiana', 'Midwest'), ('Michigan', 'Midwest'), ('Ohio', 'Midwest'), ('Wisconsin', 'Midwest'),
    ('Iowa', 'Midwest'), ('Kansas', 'Midwest'), ('Minnesota', 'Midwest'), ('Missouri', 'Midwest'), ('Nebraska', 'Midwest'),
    ('North Dakota', 'Midwest'), ('South Dakota', 'Midwest'),
    ('Delaware', 'South'), ('District of Columbia', 'South'), ('Florida', 'South'), ('Georgia', 'South'),
    ('Maryland', 'South'), ('North Carolina', 'South'), ('South Carolina', 'South'), ('Virginia', 'South'),
    ('West Virginia', 'South'), ('Alabama', 'South'), ('Kentucky', 'South'), ('Mississippi', 'South'),
    ('Tennessee', 'South'), ('Arkansas', 'South'), ('Louisiana', 'South'), ('Oklahoma', 'South'), ('Texas', 'South'),
    ('Arizona', 'West'), ('Colorado', 'West'), ('Idaho', 'West'), ('Montana', 'West'), ('Nevada', 'West'),
    ('New Mexico', 'West'), ('Utah', 'West'), ('Wyoming', 'West'), ('Alaska', 'West'), ('California', 'West'),
    ('Hawaii', 'West'), ('Oregon', 'West'), ('Washington', 'West')
),
by_region as (
    select a.aco_id, s.region, sum(a.tot_ab_psn_yrs) as person_years
    from (select distinct aco_id, state_name, state_id, county_id, tot_ab_psn_yrs from {{ ref('assign') }} where tot_ab_psn_yrs > 0) as a
    join states as s on lower(s.state_name) = lower(a.state_name)
    group by a.aco_id, s.region
)
select aco_id, arg_max(region, person_years) as region from by_region group by aco_id
