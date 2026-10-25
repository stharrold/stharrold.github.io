"""Command-line runner. Stages run in the order the plan fixes, enforced by the files each stage needs:

    enrollment -> validate (results/validation.json) -> power (results/power.json) -> confirm (results/confirm.json)

Usage (from the repository root):
    uv run --group analysis python analysis/mssp-benchmark-ratchet/ratchet/run.py <stage> [--data-dir DIR] [--out-dir DIR]

Real data must use the registered settings; --quick (small resample counts and sampler settings) is allowed only for a
synthetic data directory.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from ratchet import build, config, decision, power, resample, snapshot, validate  # noqa: E402

QUICK = {
    "n_resamples": 50,
    "full": decision.Settings(2, 300, 300, 0.9),
    "retry": decision.Settings(2, 300, 600, 0.95),
    "reduced": decision.Settings(1, 200, 200, 0.9),
    "power_datasets": 5,
    "power_perm": 99,
}
REGISTERED = {"n_resamples": config.N_RESAMPLES, "full": decision.FULL, "retry": decision.RETRY, "reduced": decision.REDUCED, "power_datasets": 500, "power_perm": 999}
H1_POWER_DATASETS = 1000


def _metadata(data_dir: Path, settings: dict) -> dict:
    commit = subprocess.run(["git", "-C", str(config.STUDY_DIR), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return {
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_commit": commit,
        "synthetic": snapshot.is_synthetic(data_dir),
        "seed": config.SEED,
        "settings": {k: (v.__dict__ if isinstance(v, decision.Settings) else v) for k, v in settings.items()},
        "versions": {p: version(p) for p in ("duckdb", "pymc", "numpy", "pandas", "scipy", "firthmodels")},
    }


def _write(out_dir: Path, name: str, payload: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / name).write_text(json.dumps(payload, indent=2, default=float) + "\n")


def _read(out_dir: Path, name: str) -> dict:
    path = out_dir / name
    if not path.exists():
        raise SystemExit(f"{name} is missing: run the earlier stage first (the plan fixes the order)")
    return json.loads(path.read_text())


def _frames(con, validation: dict):
    frame = con.sql("select * from analysis").df()
    if validation["calibrated"]:
        frame = validate.apply_calibration(frame, validation)
    return frame


def stage_enrollment(con, out_dir, settings, meta):
    groups = con.sql("select cohort, grp, count(*) as n from groups group by all order by all").df()
    steps = con.sql("select coalesce(g.grp, 'validation') as grp, p.step, count(*) as n from phase_in p left join groups g using (aco_id) group by all order by all").df()
    _write(out_dir, "enrollment.json", {**meta, "groups": groups.to_dict(orient="records"), "phase_in": steps.to_dict(orient="records")})


def stage_validate(con, out_dir, settings, meta):
    result = validate.validate(con.sql("select * from validation").df())
    _write(out_dir, "validation.json", {**meta, **result})


def stage_power(con, out_dir, settings, meta):
    validation = _read(out_dir, "validation.json")
    frame = _frames(con, validation)
    compared = frame[frame.grp.isin(["early", "stayer"])]
    early, cohort = (compared.grp == "early").to_numpy(), compared.cohort.to_numpy()
    sd_h1 = power.sav_rate_sd(con.sql("select py, sav_rate from res").df())
    stayers = compared[compared.grp == "stayer"]
    out = {"h1": {"sd": sd_h1, "mde": power.mde(sd_h1, early.sum(), (~early).sum())}, "h2": {}}
    n_h1 = settings["power_datasets"] if settings["quick"] else H1_POWER_DATASETS
    out["h1"]["simulated_power_at_mde"] = power.simulated_power(sd_h1, out["h1"]["mde"], early, cohort, n_h1, settings["power_perm"], config.SEED)
    for name in ("pull", "own"):
        sd = float(stayers[name].std())
        out["h2"][name] = {"sd_stayers": sd, "mde_sd_units": power.mde(1.0, early.sum(), (~early).sum()), "mde": power.mde(sd, early.sum(), (~early).sum())}
    design = decision.make_design(frame, validation["sigma_v"] if validation["passed"] else None, include_own=validation["passed"])
    out["h3"] = power.h3_precision(design, settings["power_datasets"], config.SEED, settings=settings["reduced"], workers=settings["workers"])
    _write(out_dir, "power.json", {**meta, **out})


def stage_confirm(con, out_dir, settings, meta):
    validation = _read(out_dir, "validation.json")
    _read(out_dir, "power.json")
    frame = _frames(con, validation)
    compared = frame[frame.grp.isin(["early", "stayer"])]
    early, cohort = (compared.grp == "early").to_numpy(), compared.cohort.to_numpy()
    n = settings["n_resamples"]
    groups = {}
    for label, column in (
        ("H2b_pull", "pull"),
        ("H2a_own", "own"),
        ("H1_sav_rate_2020", "sav_rate_2020"),
        ("H1_sav_rate_2021", "sav_rate_2021"),
        ("gain", "gain"),
        ("regional_comp", "regional_comp"),
    ):
        groups[label] = resample.compare(compared[column].to_numpy(), early, cohort, n, config.SEED)
    groups["H2a_own"]["exploratory"] = not validation["passed"]
    design = decision.make_design(frame, validation["sigma_v"] if validation["passed"] else None, include_own=validation["passed"])
    idata, checks = decision.fit_checked(design, config.SEED, full=settings["full"], retry=settings["retry"], cores=min(4, settings["workers"]))
    names = decision.coefficient_names(design)
    h3 = {"sample": {"n": int(design.y.size), "early": int(design.y.sum()), "excluded": design.excluded}, "convergence": checks}
    h3["posterior"] = decision.coefficient_summary(idata, names)
    t_idata, t_checks = decision.fit_checked(design, config.SEED + 2, prior="t", full=settings["full"], retry=settings["retry"], cores=min(4, settings["workers"]))
    h3["t_prior"] = {"posterior": decision.coefficient_summary(t_idata, names), "convergence": t_checks}
    h3["predictive_checks"] = decision.predictive_checks(design, idata, config.SEED)
    if checks["converged"]:
        h3["tests"] = {
            p: decision.direct_simulation_test(design, p, n, config.SEED, full=settings["full"], reduced=settings["reduced"], workers=settings["workers"])
            for p in decision.CORE
            if p in design.predictors
        }
        h3["overall_test"] = decision.overall_test(design, n, config.SEED, reduced=settings["reduced"], workers=settings["workers"])
    else:
        h3["fallback_firth"] = decision.firth_fallback(frame, n, config.SEED)
    _write(out_dir, "confirm.json", {**meta, "validation_passed": validation["passed"], "groups": groups, "h3": h3})


STAGES = {"enrollment": stage_enrollment, "validate": stage_validate, "power": stage_power, "confirm": stage_confirm}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("--data-dir", type=Path, default=config.DEFAULT_DATA_DIR)
    parser.add_argument("--out-dir", type=Path, default=config.RESULTS_DIR)
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument("--quick", action="store_true", help="small settings; synthetic data only")
    args = parser.parse_args(argv)
    synthetic = snapshot.is_synthetic(args.data_dir)
    if args.quick and not synthetic:
        raise SystemExit("--quick is allowed only for synthetic data; real data use the registered settings")
    if synthetic and args.out_dir == config.RESULTS_DIR:
        raise SystemExit("synthetic runs must write elsewhere than results/ (pass --out-dir)")
    settings = dict(QUICK if args.quick else REGISTERED, workers=args.workers, quick=args.quick)
    con = build.connect(args.data_dir, stage="enrollment" if args.stage == "enrollment" else "full")
    np.seterr(all="ignore")
    STAGES[args.stage](con, args.out_dir, settings, _metadata(args.data_dir, settings))
    print(f"{args.stage}: wrote {args.out_dir}")


if __name__ == "__main__":
    main()
