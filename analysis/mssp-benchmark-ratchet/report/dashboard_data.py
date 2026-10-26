"""Build the post's dashboard data (data.json) from the pipeline's results files.

Reads results/*.json as written by ratchet/run.py and writes the compact file that
content/static/<slug>/dashboard.js renders. Reporting only: it reads finished results and changes nothing in the
registered analysis, so it is outside the paths DEVIATIONS.md covers. Standard library only, so it adds no
dependency to pyproject.toml or uv.lock.

A stage whose results file does not exist yet is written as null, and the dashboard shows it as pending. The
`synthetic` flag is taken from the results files themselves, so the dashboard's synthetic-data banner cannot
outlive a switch to the real results (or be missing on synthetic ones).

Verdict wording follows PREREGISTRATION.md section 7 (two-sided p < 0.05 decides the direction); the post's text,
not this file, is the authoritative report.

Usage, from the repository root:

    python3 analysis/mssp-benchmark-ratchet/report/dashboard_data.py                       # results/ (real data)
    python3 analysis/mssp-benchmark-ratchet/report/dashboard_data.py --results <synthetic out dir>
"""

import argparse
import datetime
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SLUG = "20261026-preregistered-mssp-early-renewal"
DEFAULT_RESULTS = HERE.parent / "results"
DEFAULT_OUT = ROOT / "content" / "static" / SLUG / "data.json"
STAGES = ("validation", "power", "confirm", "robustness", "did", "conventional", "exploratory")

# Group comparisons in reporting order (section 7: primary first).
COMPARISONS = (
    ("H2b_pull", "H2b regional pull", "primary", "pp of benchmark", ("h2", "pull")),
    ("H2a_own", "H2a own-spending component", "secondary", "pp of benchmark", ("h2", "own")),
    ("H1_sav_rate_2020", "H1 savings rate, PY2020", "descriptive", "pp", ("h1",)),
    ("H1_sav_rate_2021", "H1 savings rate, PY2021", "descriptive", "pp", ("h1",)),
    ("gain", "Total expected gain", "descriptive", "pp of benchmark", None),
    ("regional_comp", "Regional component", "descriptive", "pp of benchmark", None),
)
COEFFICIENTS = {
    "b_pull": ("Regional pull", True),
    "b_own": ("Own-spending component", True),
    "b_basic_high": ("Higher BASIC level (C-E)", True),
    "b_cohort_2020": ("2020-01-01 cohort", False),
    "b_log_n_ab_2020": ("Log assigned beneficiaries", False),
    "b_high_revenue": ("High revenue", False),
    "b_prospective": ("Prospective assignment", False),
    "b_later_agreement": ("Later agreement", False),
}
CLAIMS = {"H3 pull": "H3 regional pull", "H3 own": "H3 own-spending component", "H3 basic_high": "H3 higher BASIC level"}
# 95% range of each prior on a coefficient: Normal(0, 1) and Student-t(3, 0, 2.5) (plan 5.4).
PRIOR_BAND = {"normal": 1.959964, "student_t": 3.182446 * 2.5}
H4_ROBUSTNESS = (
    ("5_trend_adjusted", "Trend-adjusted"),
    ("3_propensity_weighted", "Propensity-weighted"),
    ("1_risk_adjusted", "Risk-adjusted outcome"),
    ("2_balanced", "Balanced panel"),
    ("4_cohort_2020", "2020-01-01 cohort only"),
)


def load(results: Path) -> dict:
    out = {}
    for stage in STAGES:
        path = results / f"{stage}.json"
        out[stage] = json.loads(path.read_text()) if path.is_file() else None
    return out


def direction(estimate: float, p: float, null_text: str = "no detectable difference") -> str:
    if p is None or p >= 0.05:
        return null_text
    return "positive" if estimate > 0 else "negative"


def pct(log_value: float) -> float:
    return 100 * math.expm1(log_value)


def comparisons(confirm: dict, power: dict | None) -> dict:
    # Savings rates are fractions in the CMS files (the power SD is about 0.05); shown in percentage points.
    h1_scale = 100.0 if power and power["h1"]["sd"] < 1 else 1.0
    rows = []
    for key, label, role, unit, mde_path in COMPARISONS:
        g = confirm["groups"][key]
        scale = h1_scale if key.startswith("H1") else 1.0
        mde = None
        if power and mde_path:
            node = power
            for part in mde_path:
                node = node[part]
            mde = node["mde"] * scale
        if key == "H2a_own" and g.get("exploratory"):
            role = "secondary, exploratory (validation failed)"
        verdict = direction(g["posterior_mean"], g["p_value"]) if key in ("H2b_pull", "H2a_own") else None
        rows.append(
            {
                "key": key,
                "label": label,
                "role": role,
                "unit": unit,
                "mean": g["posterior_mean"] * scale,
                "lo": g["eti95"][0] * scale,
                "hi": g["eti95"][1] * scale,
                "p": g["p_value"],
                "p_positive": g["p_positive"],
                "mde": mde,
                "n_early": g["n_early"],
                "n_stayer": g["n_stayer"],
                "verdict": verdict,
            }
        )
    return {"rows": rows, "imputed_by_group": confirm.get("imputed_by_group")}


def decision_model(confirm: dict, power: dict | None) -> dict:
    h3 = confirm["h3"]
    converged = h3["convergence"]["converged"]
    tests = {}
    if converged and "tests" in h3:
        tests = {f"b_{k}": {"p": v["p_value"], "decision": v["decision"], "by": "direct simulation"} for k, v in h3["tests"].items()}
    elif "fallback_firth" in h3:
        tests = {
            f"b_{k}": {"p": v["p_value"], "decision": v["decision"], "by": "Firth fallback"} for k, v in h3["fallback_firth"]["coefficients"].items() if "decision" in v
        }

    def rows(posterior: dict) -> list:
        out = []
        for name, summary in posterior.items():
            label, core = COEFFICIENTS.get(name, (name, False))
            out.append(
                {
                    "name": name,
                    "label": label,
                    "core": core,
                    "predicted": "+" if core else None,
                    "mean": summary["mean"],
                    "lo": summary["eti95"][0],
                    "hi": summary["eti95"][1],
                    "p_positive": summary["p_positive"],
                    "test": tests.get(name),
                }
            )
        return sorted(out, key=lambda r: not r["core"])

    note = None
    if power:
        shares = power["h3"]
        labels = (("pull", "pull"), ("own", "own"), ("basic_high", "BASIC level"))
        note = ", ".join(f"{round(100 * shares[k]['detection_share'])}% ({label})" for k, label in labels if k in shares)
    return {
        "sample": h3["sample"],
        "converged": converged,
        "posterior": {"normal": rows(h3["posterior"]), "student_t": rows(h3["t_prior"]["posterior"])},
        "prior_band": PRIOR_BAND,
        "overall_test": h3.get("overall_test"),
        "power_note": note,
    }


def effect(did: dict, power: dict | None) -> dict:
    def row(est: dict, label: str, role: str) -> dict:
        if isinstance(est.get("percent"), float):  # propensity-weighted: a point estimate and a p-value, no interval
            mean, lo, hi = est["percent"], None, None
        elif "percent" in est:
            mean, (lo, hi) = est["percent"]["posterior_mean"], est["percent"]["eti95"]
        else:
            mean, lo, hi = pct(est.get("posterior_mean", est.get("estimate"))), pct(est["eti95"][0]), pct(est["eti95"][1])
        return {"label": label, "role": role, "mean": mean, "lo": lo, "hi": hi, "p": est.get("p_value")}

    h4 = did["H4"]
    estimates = [row(h4, "H4 difference-in-differences", "confirmatory")]
    for key, label in H4_ROBUSTNESS:
        if key in did.get("robustness", {}):
            estimates.append(row(did["robustness"][key], label, "robustness"))
    twfe = did["conventional"]["twfe"]
    pooled = twfe["pooled"]
    lo, hi = pooled["ci95"]
    estimates.append({"label": "Two-way fixed effects", "role": "conventional", "mean": pct(pooled["estimate"]), "lo": pct(lo), "hi": pct(hi), "p": pooled["p_value"]})
    event = [{"year": 2021, "mean": 0.0, "lo": 0.0, "hi": 0.0, "reference": True}]
    for year, e in twfe.get("event_study", {}).items():
        event.append({"year": int(year), "mean": pct(e["estimate"]), "lo": pct(e["ci95"][0]), "hi": pct(e["ci95"][1]), "reference": False})
    pre = did["pre_trend_check"]
    return {
        "sample": did.get("sample"),
        "verdict": direction(h4["posterior_mean"], h4["p_value"]),
        "estimates": estimates,
        "pre_trend": {"mean": pre["posterior_mean"], "lo": pre["eti95"][0], "hi": pre["eti95"][1], "p": pre["p_value"]},
        "equivalence": pre.get("equivalence"),
        "mde_percent": pct(power["h4"]["mde_log"]) if power else None,
        "event_study": sorted(event, key=lambda p: p["year"]),
    }


def build(results: Path) -> dict:
    r = load(results)
    present = [v for v in r.values() if v]
    if not present:
        raise SystemExit(f"no results files in {results}")
    flags = {bool(v.get("synthetic")) for v in present}
    if len(flags) > 1:
        raise SystemExit(f"{results} mixes synthetic and real results")
    commits = sorted({v["git_commit"][:7] for v in present})
    power = r["power"]
    return {
        "synthetic": flags.pop(),
        "built": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "commit": ", ".join(commits),
        "stages": [{"name": s, "done": r[s] is not None} for s in STAGES],
        "validation": {k: r["validation"].get(k) for k in ("passed", "calibrated", "sigma_v_model")} if r["validation"] else None,
        "comparisons": comparisons(r["confirm"], power) if r["confirm"] else None,
        "h3": decision_model(r["confirm"], power) if r["confirm"] else None,
        "h4": effect(r["did"], power) if r["did"] else None,
        "agreement": [{**row, "claim": CLAIMS.get(row["claim"], row["claim"])} for row in r["conventional"]["agreement"]] if r["conventional"] else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    data = build(args.results)
    args.out.write_text(json.dumps(data, indent=1, allow_nan=False) + "\n")
    print(f"wrote {args.out} ({'synthetic' if data['synthetic'] else 'real'} results)")


if __name__ == "__main__":
    main()
