-- Parsing helpers. Files are loaded as text; anything non-numeric (e.g. suppression markers) becomes NULL (section 3).
create or replace macro num(x) as try_cast(regexp_replace(trim(x), '[$,%]', '', 'g') as double);
-- Enrollment dates are M/D/YYYY, with a " 0:00" time suffix in the PY2019 January file. The results files' date format
-- cannot be checked before registration, so YYYY-MM-DD is accepted too.
create or replace macro mdy(x) as cast(coalesce(
    try_strptime(split_part(trim(x), ' ', 1), '%m/%d/%Y'),
    try_strptime(split_part(trim(x), ' ', 1), '%Y-%m-%d')
) as date);
create or replace macro flag(x) as coalesce(num(x), 0) = 1;
