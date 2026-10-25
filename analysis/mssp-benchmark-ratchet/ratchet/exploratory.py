"""Exploratory and descriptive analyses (section 5.6), labeled as such in the write-up."""

import numpy as np
import pandas as pd

from ratchet import robustness

REGIONS = ("Northeast", "Midwest", "South", "West")
DESCRIBED = ("sav_rate_2020", "pull", "own", "regional_comp")


def region_indicators(frame: pd.DataFrame) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """Indicators for the census regions present, Northeast as reference (the first region present if Northeast is not)."""
    present = [r for r in REGIONS if (frame.census_region == r).any()]
    reference = "Northeast" if "Northeast" in present else present[0]
    out = frame[frame.census_region.notna()].copy()
    names = []
    for r in present:
        if r != reference:
            out[f"region_{r.lower()}"] = (out.census_region == r).astype(float)
            names.append(f"region_{r.lower()}")
    return out, tuple(names)


def group_table(frame: pd.DataFrame, columns=DESCRIBED) -> dict:
    """n, mean, median and SD by group (early renewers, stayers, leavers)."""
    out = {}
    for grp, g in frame.groupby("grp"):
        out[grp] = {c: {"n": int(g[c].notna().sum()), "mean": float(g[c].mean()), "median": float(g[c].median()), "sd": float(g[c].std())} for c in columns}
    return out


def enhanced_early_renewers(frame: pd.DataFrame) -> list[dict]:
    """Early renewers already in ENHANCED in PY2021, each value with its percentile among stayers."""
    stayers = frame[frame.grp == "stayer"]
    rows = []
    for _, a in frame[(frame.grp == "early") & frame.enhanced.astype(bool)].iterrows():
        row = {"aco_id": a.aco_id, "cohort": a.cohort}
        for c in DESCRIBED:
            ref = stayers[c].dropna().to_numpy()
            row[c] = {"value": float(a[c]), "stayer_percentile": float(100 * np.mean(ref <= a[c])) if ref.size and not np.isnan(a[c]) else None}
        rows.append(row)
    return rows


def who_renewed(frame: pd.DataFrame) -> list[dict]:
    """Counts by group, cohort, PY2021 track/level and PY2022 track (enrollment data)."""
    t = frame.assign(
        track_2021=np.where(frame.enhanced.astype(bool), "ENHANCED", "BASIC " + frame.basic_level.fillna("?")),
        track_2022=np.where(frame.enhanced_2022.isna(), "left", np.where(frame.enhanced_2022.fillna(False).astype(bool), "ENHANCED", "BASIC")),
    )
    return t.groupby(["grp", "cohort", "track_2021", "track_2022"]).size().rename("n").reset_index().to_dict(orient="records")


def run_all(frame: pd.DataFrame, spending: pd.DataFrame, validation: dict, settings: dict, seed: int) -> dict:
    n = settings["n_resamples"]
    passed = validation["passed"]
    sigma_v = validation["sigma_v_model"] if passed else None
    out: dict = {}
    with_region, region_cols = region_indicators(frame)
    out["census_region_in_h3"] = {
        "excluded_no_region": int(frame.census_region.isna().sum()),
        "indicators": list(region_cols),
        **robustness.h3_posterior(with_region, sigma_v, passed, settings, seed, extra=region_cols),
    }
    out["leavers"] = group_table(frame)
    out["enhanced_early_renewers"] = enhanced_early_renewers(frame)
    weighted = frame.assign(pull=frame.w * frame.pull)
    capped = frame.assign(pull=frame.regional_comp)
    out["pull_times_w"] = {"H2b": robustness.compare(weighted, "pull", n, seed), "H3": robustness.h3_posterior(weighted, sigma_v, passed, settings, seed)}
    out["capped_regional_component"] = {"H2b": robustness.compare(capped, "pull", n, seed), "H3": robustness.h3_posterior(capped, sigma_v, passed, settings, seed)}
    out["who_renewed"] = who_renewed(frame)
    out["balance"] = group_table(frame, ("share_85plus_2020", "share_female_2020"))
    out["spending_by_agreement_year"] = spending.to_dict(orient="records")
    return out
