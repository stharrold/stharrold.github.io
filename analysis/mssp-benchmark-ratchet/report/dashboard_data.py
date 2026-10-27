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
# Robustness (plan 5.5) by results key: label, and the confirm-stage group keys of the comparisons it repeats.
GROUP_KEYS = {"H1": "H1_sav_rate_2020", "H2a": "H2a_own", "H2b": "H2b_pull", "gain": "gain", "regional_comp": "regional_comp"}
GROUP_ROBUSTNESS = (
    ("2_medians", "Difference in medians (item 2)"),
    ("3_cohort_2020", "2020-01-01 cohort only (item 3)"),
    ("6_by2_by3", "BY2-BY3 only in step 1 (item 6)"),
    ("8_complete_cases", "Complete cases (item 8)"),
    ("9_unadjusted_pull", "Unadjusted county spending (item 9)"),
)
H3_ROBUSTNESS = (
    ("3_cohort_2020", "2020-01-01 cohort only (item 3)"),
    ("6_by2_by3", "BY2-BY3 only in step 1 (item 6)"),
    ("7_no_measurement_error", "No measurement-error model (item 7)"),
    ("8_complete_cases", "Complete cases (item 8)"),
    ("9_unadjusted_pull", "Unadjusted county spending (item 9)"),
)
CORE_COEFFICIENTS = ("b_pull", "b_own", "b_basic_high")
# Exploratory (plan 5.6): other measures of the regional pull, in place of it in H2b and H3.
ALT_EXPOSURES = (("pull_times_w", "Pull weighted by phase-in weight w"), ("capped_regional_component", "Capped regional component"))
DESCRIBED = {
    "sav_rate_2020": "Savings rate, PY2020 (pp)",
    "pull": "Regional pull (pp of benchmark)",
    "own": "Own-spending component (pp of benchmark)",
    "regional_comp": "Regional component (pp of benchmark)",
}
BALANCE = {"share_85plus_2020": "Share aged 85+, PY2020", "share_female_2020": "Share female, PY2020"}


def load(results: Path) -> dict:
    out = {}
    for stage in STAGES:
        path = results / f"{stage}.json"
        out[stage] = json.loads(path.read_text()) if path.is_file() else None
    return out


def direction(estimate: float, p: float, null_text: str = "no detectable difference") -> str:
    """Two-sided verdict with no predicted sign (H4)."""
    if p is None or p >= 0.05:
        return null_text
    return "positive" if estimate > 0 else "negative"


def prediction(estimate: float, p: float) -> str:
    """Verdict for a predicted-positive difference (H2b, H2a), in the agreement table's words."""
    if p is None or p >= 0.05:
        return "no detectable difference"
    return "supported" if estimate > 0 else "contradicted"


def pct(log_value: float) -> float:
    return 100 * math.expm1(log_value)


def h1_scale(power: dict | None) -> float:
    # Savings rates are fractions in the PY2016-PY2020 CMS files (the power SD is about 0.05); shown in percentage points.
    return 100.0 if power and power["h1"]["sd"] < 1 else 1.0


def value_scale(key: str, h1: float) -> float:
    # The PY2021 file writes savings rates as percents ("3.14%"), so its comparison is already in percentage points.
    return 1.0 if key == "H1_sav_rate_2021" else h1 if key.startswith("H1") else 1.0


def estimate_row(label: str, g: dict, scale: float = 1.0, role: str = "robustness") -> dict:
    """One interval row from a bootstrap comparison, a posterior summary, a regression coefficient or a Firth fit."""
    if "b_early_units" in g:  # 5.3 regression: the early-renewer coefficient in the variable's units, no test
        g = g["b_early_units"]
    mean = g.get("posterior_mean", g.get("mean", g.get("estimate")))
    lo, hi = g.get("eti95", g.get("pl95"))
    return {"label": label, "role": role, "mean": mean * scale, "lo": lo * scale, "hi": hi * scale, "p": g.get("p_value")}


def robustness(rob: dict, confirm: dict, power: dict | None) -> dict:
    """Plan 5.5, estimates only: each confirmatory row followed by the robustness items that repeat it."""
    scale = h1_scale(power)
    groups = []
    for key, label, *_ in COMPARISONS:
        if key == "H1_sav_rate_2021":  # item 4 is this comparison; it is already in the group comparisons
            continue
        s = scale if key.startswith("H1") else 1.0
        name = next(k for k, v in GROUP_KEYS.items() if v == key)
        rows = [estimate_row("Confirmatory", confirm["groups"][key], s, "confirmatory")]
        regressions = rob.get("1_adjusted_regressions", {}).get(name, {})
        if "unadjusted_5_3" in regressions:
            rows.append(estimate_row("Regression, cohort only (5.3)", regressions["unadjusted_5_3"], s, "reported"))
        if "adjusted" in regressions:
            rows.append(estimate_row("Regression + track, level and size (item 1)", regressions["adjusted"], s))
        rows += [estimate_row(item_label, rob[item][name], s) for item, item_label in GROUP_ROBUSTNESS if name in rob.get(item, {})]
        if len(rows) > 1:
            groups.append({"key": key, "label": label, "unit": next(u for k, _, _, u, _ in COMPARISONS if k == key), "rows": rows})

    h3 = []
    confirm_post = confirm["h3"]["posterior"]
    for coef in CORE_COEFFICIENTS:
        if coef not in confirm_post:  # own spending dropped when the validation fails (section 7)
            continue
        rows = [estimate_row("Confirmatory", confirm_post[coef], role="confirmatory")]
        firth = rob.get("5_firth", {}).get("coefficients", {}).get(coef[2:])
        if firth:
            rows.append(estimate_row("Firth logistic regression (item 5)", firth))
        for item, item_label in H3_ROBUSTNESS:
            fit = rob.get(item, {})
            fit = fit.get("H3", fit)
            if coef in fit.get("posterior", {}):
                row = estimate_row(item_label, fit["posterior"][coef])
                row["converged"] = fit["convergence"]["converged"]
                rows.append(row)
        h3.append({"key": coef, "label": COEFFICIENTS[coef][0], "unit": "log-odds", "rows": rows})
    return {"groups": groups, "h3": h3}


def exploratory(exp: dict, confirm: dict, power: dict | None) -> dict:
    """Plan 5.6: labeled exploratory; no verdicts."""
    scale = h1_scale(power)

    def scaled(variable: str, value: float | None) -> float | None:
        return value * scale if value is not None and variable == "sav_rate_2020" else value

    h2b = [estimate_row("Regional pull (confirmatory)", confirm["groups"]["H2b_pull"], role="confirmatory")]
    pull = [estimate_row("Regional pull (confirmatory)", confirm["h3"]["posterior"]["b_pull"], role="confirmatory")]
    for key, label in ALT_EXPOSURES:
        if key in exp:
            h2b.append(estimate_row(label, exp[key]["H2b"], role="exploratory"))
            pull.append(estimate_row(label, exp[key]["H3"]["posterior"]["b_pull"], role="exploratory"))
    region = exp.get("census_region_in_h3")
    if region:
        pull.append(estimate_row("Census region added", region["posterior"]["b_pull"], role="exploratory"))
    groups = {grp: {v: {**s, "mean": scaled(v, s["mean"]), "median": scaled(v, s["median"])} for v, s in table.items()} for grp, table in exp["leavers"].items()}
    return {
        "alternative_exposures": [
            {"key": "H2b", "label": "H2b, early renewers minus stayers", "unit": "pp of benchmark", "rows": h2b},
            {"key": "H3", "label": "H3 coefficient on the pull measure", "unit": "log-odds", "rows": pull},
        ],
        "region": {
            "excluded_no_region": region["excluded_no_region"],
            "rows": [estimate_row(f"{k[9:].capitalize()} vs Northeast", v, role="exploratory") for k, v in region["posterior"].items() if k.startswith("b_region_")],
        }
        if region
        else None,
        "described": DESCRIBED,
        "groups": groups,
        "enhanced": [
            {"aco_id": r["aco_id"], "cohort": r["cohort"], **{v: {"value": scaled(v, r[v]["value"]), "percentile": r[v]["stayer_percentile"]} for v in DESCRIBED}}
            for r in exp["enhanced_early_renewers"]
        ],
        "who_renewed": exp["who_renewed"],
        "balance": {"labels": BALANCE, "groups": exp["balance"]},
        "spending": [
            {
                "start_year": r["start_year"],
                "agreement_year": r["agreement_year"],
                "scheduled": r["scheduled_benchmark_year"],
                "early": r["early_renewer_from_2020"],
                "n": r["n_acos"],
                "mean": r["mean_pc"],
            }
            for r in exp["spending_by_agreement_year"]
        ],
    }


def comparisons(confirm: dict, power: dict | None) -> dict:
    h1 = h1_scale(power)
    rows = []
    for key, label, role, unit, mde_path in COMPARISONS:
        g = confirm["groups"][key]
        scale = value_scale(key, h1)
        mde = None
        if power and mde_path:
            node = power
            for part in mde_path:
                node = node[part]
            mde = node["mde"] * (h1 if key.startswith("H1") else 1.0)
        if key == "H2a_own" and g.get("exploratory"):
            role = "secondary, exploratory (validation failed)"
        verdict = prediction(g["posterior_mean"], g["p_value"]) if key in ("H2b_pull", "H2a_own") else None
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
        "robustness": robustness(r["robustness"], r["confirm"], power) if r["robustness"] and r["confirm"] else None,
        "exploratory": exploratory(r["exploratory"], r["confirm"], power) if r["exploratory"] and r["confirm"] else None,
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
