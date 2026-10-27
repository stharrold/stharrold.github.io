"""Build the study database: verified raw CMS tables in DuckDB, then the derived tables with dbt.

Stage "enrollment" reads only enrollment files (allowed before registration). Stage "full" also reads the outcome files,
which ratchet.snapshot refuses for real data until REGISTRATION.md exists. Raw tables are loaded here, after each
file's sha256 is checked; dbt (`dbt/`) builds and tests every derived table from them and never reads a file itself.
dbt runs twice: the enrollment models first, so that the PY2022 results file can be filtered to the dbt-built
`validation_sample` as it is loaded (early renewers' PY2022 rows never enter the database, section 4.4); then the
outcome models.
"""

import json
import os
import tempfile
from pathlib import Path

import duckdb
from dbt.cli.main import dbtRunner

from ratchet import config
from ratchet.snapshot import checked_path

DBT_DIR = config.STUDY_DIR / "dbt"


def _read_csv(path: Path) -> str:
    quoted = str(path).replace("'", "''")
    return f"read_csv('{quoted}', all_varchar = true, encoding = 'latin-1', header = true)"


def _dbt_build(db: Path, tags: list[str], by_first: int, workdir: Path) -> None:
    os.environ["RATCHET_DUCKDB_PATH"] = str(db)
    target = Path(tempfile.gettempdir()) / "ratchet-dbt-target"  # shared across builds, for partial parsing
    args = ["build", "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR), "--target-path", str(target), "--log-path", str(workdir / "logs")]
    args += ["--quiet", "--indirect-selection", "cautious"]
    args += ["--select", " ".join(f"tag:{t}" for t in tags), "--vars", json.dumps({"by_first": by_first})]
    result = dbtRunner().invoke(args)
    if not result.success:
        failed = [r.node.name for r in (result.result or []) if getattr(r, "status", None) not in ("success", "pass")]
        raise RuntimeError(f"dbt build failed: {failed or result.exception}")


def connect(
    data_dir: Path = config.DEFAULT_DATA_DIR, stage: str = "enrollment", registration: Path = config.REGISTRATION, by_first: int = 2019, descriptive: bool = False
) -> duckdb.DuckDBPyConnection:
    """by_first: first benchmark year in step 1 of 4.3 (2020 for robustness item 6). descriptive: also load the full
    PY2022 file and PY2023-PY2024 for H4 and the section 5.6 spending table; only after the confirmatory results exist."""
    if stage not in ("enrollment", "full"):
        raise ValueError(f"unknown stage {stage!r}")
    if by_first not in (2019, 2020):
        raise ValueError("by_first must be 2019 or 2020")
    workdir = Path(tempfile.mkdtemp(prefix="ratchet-"))
    db = workdir / "study.duckdb"
    with duckdb.connect(str(db)) as con:
        for suffix, name in config.ENROLLMENT_FILES.items():
            con.execute(f"create table raw_enroll_{suffix} as select * from {_read_csv(checked_path(data_dir, name, registration))}")
    _dbt_build(db, ["enrollment"], by_first, workdir)
    if stage == "full":
        tags = ["full"]
        with duckdb.connect(str(db)) as con:
            for year, name in config.RESULTS_FILES.items():
                source = _read_csv(checked_path(data_dir, name, registration))
                where = " where trim(aco_id) in (select aco_id from validation_sample)" if year == 2022 else ""
                con.execute(f"create table raw_results_{year} as select * from {source}{where}")
            for year, name in config.COUNTY_FILES.items():
                con.execute(f"create table raw_county_{year} as select * from {_read_csv(checked_path(data_dir, name, registration))}")
            con.execute(f"create table raw_assign_2021 as select * from {_read_csv(checked_path(data_dir, config.ASSIGNMENT_FILE, registration))}")
            if descriptive:
                tags.append("descriptive")
                con.execute(f"create table raw_results_2022_all as select * from {_read_csv(checked_path(data_dir, config.RESULTS_FILES[2022], registration))}")
                for year, name in config.DESCRIPTIVE_RESULTS_FILES.items():
                    con.execute(f"create table raw_results_{year} as select * from {_read_csv(checked_path(data_dir, name, registration))}")
        _dbt_build(db, tags, by_first, workdir)
    return duckdb.connect(str(db))


def scalar(con: duckdb.DuckDBPyConnection, sql: str):
    """First value of a query's single row (DuckDB 2 relations have no fetchone())."""
    return con.sql(sql).fetchall()[0][0]
