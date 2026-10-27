{# Parsing helpers. Files are loaded as text; anything non-numeric (e.g. suppression markers) becomes NULL (section 3). #}
{% macro num(column) -%}
    try_cast(regexp_replace(trim({{ column }}), '[$,%]', '', 'g') as double)
{%- endmacro %}

{# Enrollment dates are M/D/YYYY, with a " 0:00" time suffix in the PY2019 January file. The results files' date format
   cannot be checked before registration, so YYYY-MM-DD is accepted too. #}
{% macro mdy(column) -%}
    cast(coalesce(
        try_strptime(split_part(trim({{ column }}), ' ', 1), '%m/%d/%Y'),
        try_strptime(split_part(trim({{ column }}), ' ', 1), '%Y-%m-%d')
    ) as date)
{%- endmacro %}

{% macro flag(column) -%}
    coalesce({{ num(column) }}, 0) = 1
{%- endmacro %}
