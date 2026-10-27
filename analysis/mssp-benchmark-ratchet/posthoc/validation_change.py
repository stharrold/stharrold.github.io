"""Post hoc validation of the expected gain on the change scale, and early renewers' realized 2022 reset.

NOT REGISTERED. Written on 2026-10-27, after every registered result had been read, in response to a critical
assessment of the preprint: the registered validation (plan section 4.4) checks benchmark *levels*, which vary
widely across ACOs, while H2a, H2b and the gain concern *differences* of a few points of the benchmark. This script
uses the registered pipeline's tables unchanged (`ratchet.build`) and the registered estimator (`ratchet.resample`);
it changes no registered file and its results are exploratory.

1. Change scale, regular renewers (the registered validation sample): the rebuilt change,
   100 x (rebuilt - current) / current, against the actual change, 100 x (CMS 2022 historical benchmark - current) /
   current, where current is the PY2021 updated per-capita benchmark (both in 2021 dollars, as in section 4.4).
2. Realized reset, early renewers: the same actual change from the full PY2022 results file (`HistBnchmk`), which the
   registered analysis never compared with the rebuilt gain, against the rebuilt gain.
3. Benchmark update PY2021 to PY2022, early renewers vs stayers: 100 x (PY2022 / PY2021 updated benchmark - 1), which
   includes the annual update for both groups and the reset for early renewers; section 5.1's estimator (within-cohort
   difference in means, Bayesian bootstrap, stratified permutation, 10,000 resamples).

Writes posthoc/validation_change.json. Run from the repository root (about a minute; builds the database twice):

    uv run --group analysis python analysis/mssp-benchmark-ratchet/posthoc/validation_change.py
"""

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from ratchet import build, config, resample  # noqa: E402

NUM = "try_cast(replace(cast({} as varchar), ',', '') as double)"


def agreement(rebuilt: np.ndarray, actual: np.ndarray) -> dict:
    error = rebuilt - actual
    fit = stats.linregress(rebuilt, actual)
    return {
        "n": int(rebuilt.size),
        "spearman": float(stats.spearmanr(rebuilt, actual).statistic),
        "pearson": float(stats.pearsonr(rebuilt, actual).statistic),
        "slope_actual_on_rebuilt": float(fit.slope),
        "intercept": float(fit.intercept),
        "mean_error": float(error.mean()),
        "sd_error": float(error.std(ddof=1)),
        "median_abs_error": float(np.median(np.abs(error))),
        "same_sign_share": float(np.mean(np.sign(rebuilt) == np.sign(actual))),
        "rebuilt": {"mean": float(rebuilt.mean()), "median": float(np.median(rebuilt)), "sd": float(rebuilt.std(ddof=1))},
        "actual": {"mean": float(actual.mean()), "median": float(np.median(actual)), "sd": float(actual.std(ddof=1)), "share_negative": float(np.mean(actual < 0))},
    }


def main() -> None:
    con = build.connect(stage="full", descriptive=True)
    out: dict = {
        "registered": False,
        "note": "Post hoc, exploratory; written after all registered results were read (see the module docstring).",
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip(),
        "seed": config.SEED,
    }

    v = con.sql("select approximate, actual, current_bnchmk from validation where approximate is not null and actual is not null").df()
    out["regular_renewers_change"] = agreement(
        (100 * (v.approximate - v.current_bnchmk) / v.current_bnchmk).to_numpy(), (100 * (v.actual - v.current_bnchmk) / v.current_bnchmk).to_numpy()
    )

    py22 = f"select trim(ACO_ID) as aco_id, {NUM.format('HistBnchmk')} as hist_2022, {NUM.format('UpdatedBnchmk')} as upd_2022 from raw_results_2022_all"
    py21 = f"select trim(ACO_ID) as aco_id, {NUM.format('UpdatedBnchmk')} as upd_2021 from raw_results_2021"
    d = con.sql(
        f"""
        select a.aco_id, a.grp, a.cohort, a.gain, eg.current_bnchmk, p22.hist_2022, p22.upd_2022, p21.upd_2021
        from analysis a
        left join expected_gain eg using (aco_id)
        left join ({py22}) p22 using (aco_id)
        left join ({py21}) p21 using (aco_id)
        where a.grp in ('early', 'stayer')
        """
    ).df()
    early = d[d.grp == "early"].copy()
    # current benchmark: the pipeline's PY2021 per-capita updated benchmark where it was built, else the PY2021 file's.
    early["current"] = early.current_bnchmk.fillna(early.upd_2021)
    early["realized_gain"] = 100 * (early.hist_2022 - early.current) / early.current
    both = early.dropna(subset=["gain", "realized_gain"])
    out["early_renewers_realized"] = {
        "n_early": int(len(early)),
        "n_with_hist_2022": int(early.realized_gain.notna().sum()),
        "all_with_hist_2022": {
            "mean": float(early.realized_gain.mean()),
            "median": float(early.realized_gain.median()),
            "share_negative": float((early.realized_gain.dropna() < 0).mean()),
        },
        "rebuilt_vs_realized": agreement(both.gain.to_numpy(), both.realized_gain.to_numpy()),
    }

    d["update_pct"] = 100 * (d.upd_2022 / d.upd_2021 - 1)
    res = resample.compare(d.update_pct.to_numpy(), (d.grp == "early").to_numpy(), d.cohort.to_numpy(), config.N_RESAMPLES, config.SEED)
    res["group_means"] = {g: float(d.loc[d.grp == g, "update_pct"].mean()) for g in ("early", "stayer")}
    res["group_medians"] = {g: float(d.loc[d.grp == g, "update_pct"].median()) for g in ("early", "stayer")}
    out["benchmark_update_2021_2022"] = res

    path = HERE / "validation_change.json"
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
