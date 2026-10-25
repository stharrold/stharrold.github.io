-- Parsing helpers. Files are loaded as text; anything non-numeric (e.g. suppression markers) becomes NULL (section 3).
create or replace macro num(x) as try_cast(regexp_replace(trim(x), '[$,%]', '', 'g') as double);
-- Dates are M/D/YYYY, with a " 0:00" time suffix in the PY2019 January file.
create or replace macro mdy(x) as cast(try_strptime(split_part(trim(x), ' ', 1), '%m/%d/%Y') as date);
create or replace macro flag(x) as coalesce(num(x), 0) = 1;
