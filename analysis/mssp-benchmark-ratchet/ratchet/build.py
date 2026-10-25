"""Build the study database in DuckDB from the verified snapshot.

Stage "enrollment" reads only enrollment files (allowed before registration). Stage "full" also reads the outcome files,
which ratchet.snapshot refuses for real data until REGISTRATION.md exists. The PY2022 results file is filtered to the
validation sample as it is loaded, so early renewers' PY2022 rows never enter the database (section 4.4).
"""

from pathlib import Path

import duckdb

from ratchet import config
from ratchet.snapshot import checked_path

ENROLLMENT_SQL = ("00_macros.sql", "01_enrollment.sql", "02_groups.sql", "03_phase_in.sql")
FULL_SQL = ("04_results.sql", "05_regional.sql", "06_expected_gain.sql", "07_analysis.sql")
DESCRIPTIVE_SQL = ("08_descriptive.sql",)


def _read_csv(path: Path) -> str:
    quoted = str(path).replace("'", "''")
    return f"read_csv('{quoted}', all_varchar = true, encoding = 'latin-1', header = true)"


def _run_sql(con: duckdb.DuckDBPyConnection, names: tuple[str, ...]) -> None:
    for name in names:
        con.execute((config.SQL_DIR / name).read_text())


def connect(
    data_dir: Path = config.DEFAULT_DATA_DIR, stage: str = "enrollment", registration: Path = config.REGISTRATION, by_first: int = 2019, descriptive: bool = False
) -> duckdb.DuckDBPyConnection:
    """by_first: first benchmark year in step 1 of 4.3 (2020 for robustness item 6). descriptive: also load the full
    PY2022 file and PY2023-PY2024 for the section 5.6 spending table; only after the confirmatory results exist."""
    if stage not in ("enrollment", "full"):
        raise ValueError(f"unknown stage {stage!r}")
    if by_first not in (2019, 2020):
        raise ValueError("by_first must be 2019 or 2020")
    con = duckdb.connect()
    con.execute(f"set variable by_first = {by_first}")
    for suffix, name in config.ENROLLMENT_FILES.items():
        con.execute(f"create table raw_enroll_{suffix} as select * from {_read_csv(checked_path(data_dir, name, registration))}")
    _run_sql(con, ENROLLMENT_SQL)
    if stage == "full":
        for year, name in config.RESULTS_FILES.items():
            source = _read_csv(checked_path(data_dir, name, registration))
            if year == 2022:
                con.execute(f"create table raw_results_2022 as select * from {source} where trim(aco_id) in (select aco_id from validation_sample)")
            else:
                con.execute(f"create table raw_results_{year} as select * from {source}")
        for year, name in config.COUNTY_FILES.items():
            con.execute(f"create table raw_county_{year} as select * from {_read_csv(checked_path(data_dir, name, registration))}")
        con.execute(f"create table raw_assign_2021 as select * from {_read_csv(checked_path(data_dir, config.ASSIGNMENT_FILE, registration))}")
        _run_sql(con, FULL_SQL)
        if descriptive:
            con.execute(f"create table raw_results_2022_all as select * from {_read_csv(checked_path(data_dir, config.RESULTS_FILES[2022], registration))}")
            for year, name in config.DESCRIPTIVE_RESULTS_FILES.items():
                con.execute(f"create table raw_results_{year} as select * from {_read_csv(checked_path(data_dir, name, registration))}")
            _run_sql(con, DESCRIPTIVE_SQL)
    return con


def scalar(con: duckdb.DuckDBPyConnection, sql: str):
    """First value of a query's single row (DuckDB 2 relations have no fetchone())."""
    return con.sql(sql).fetchall()[0][0]
