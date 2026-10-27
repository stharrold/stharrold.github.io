"""Results notebook for the MSSP early-renewal study (marimo).

Reporting only: it reads results/*.json through dashboard_data.build() and recomputes nothing, so it is outside the
paths DEVIATIONS.md covers. Charts are matplotlib images, so the .ipynb and PDF exports need no JavaScript.

Run and export from the repository root. None of these tools are in uv.lock, so their versions are pinned here;
Playwright 1.61.0 is the version whose Chromium the PDF export uses:

    uv run --with marimo==0.25.2 --with matplotlib==3.11.2 --with nbformat==5.11.1 \
        --with 'nbconvert[webpdf]==7.17.2' --with playwright==1.61.0 \
        marimo export html analysis/mssp-benchmark-ratchet/report/results_notebook.py -o results.html

For the other two exports, replace `html` with `ipynb --include-outputs` (outputs are off by default) or `pdf`.
"""

# A marimo cell shows its last expression, so a bare `_fig` at the end of a cell is its output.
# ruff: noqa: B018

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="MSSP early renewal: results")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Why did Medicare ACOs reset their benchmarks early? Results

        This notebook reports the results of the pre-registered study
        ([OSF registration c53w9](https://osf.io/c53w9/), DOI 10.17605/OSF.IO/C53W9; plan and code at commit `a4064f5`).
        It only reads the pipeline's results files in `analysis/mssp-benchmark-ratchet/results/` and recomputes nothing.
        The blog post is the authoritative report; the verdicts below use the same wording as its dashboard.

        Units: "pp" is percentage points. Benchmark components are in percentage points of the ACO's benchmark.
        Intervals are 95% equal-tailed intervals; p-values are two-sided.
        """
    )
    return


@app.cell
def _():
    import hashlib
    import json
    import sys

    import marimo as mo
    import matplotlib.pyplot as plt

    sys.path.insert(0, str(mo.notebook_dir()))
    import dashboard_data

    return dashboard_data, hashlib, json, mo, plt


@app.cell
def _(dashboard_data):
    results_dir = dashboard_data.DEFAULT_RESULTS
    data = dashboard_data.build(results_dir)
    raw = dashboard_data.load(results_dir)
    return data, raw, results_dir


@app.cell
def _():
    colors = {"ink": "#1f2933", "muted": "#5f6b7a", "grid": "#d9dee5", "mark": "#2b5c9e"}

    def num(x, digits=1):
        if x is None:
            return ""
        text = f"{x:.{digits}f}"
        return text.lstrip("-") if float(text) == 0 else text.replace("-", "\u2212")

    def pval(p):
        return "" if p is None else "< 0.001" if p < 0.001 else f"{p:.3f}"

    def interval(r, digits=1):
        return "" if r.get("lo") is None else f"{num(r['lo'], digits)} to {num(r['hi'], digits)}"

    def table(header, rows):
        lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
        lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
        return "\n".join(lines)

    return colors, interval, num, pval, table


@app.cell
def _(colors, plt):
    def forest(ax, rows, xlabel, band=None):
        """One interval per row, top to bottom, with a zero line; band shades a prior's 95% range."""
        ys = list(range(len(rows)))[::-1]
        if band:
            ax.axvspan(-band, band, color=colors["grid"], alpha=0.5, lw=0)
        ax.axvline(0, color=colors["muted"], lw=1)
        for y, r in zip(ys, rows, strict=True):
            if r.get("lo") is not None:
                ax.plot([r["lo"], r["hi"]], [y, y], color=colors["mark"], lw=2, solid_capstyle="round")
            ax.plot(r["mean"], y, "o", color=colors["mark"], ms=6, mec="white", mew=1.5)
        ax.set_yticks(ys, [r["label"] for r in rows], color=colors["ink"])
        ax.set_xlabel(xlabel, color=colors["ink"])
        ax.tick_params(colors=colors["muted"], length=0)
        ax.grid(axis="x", color=colors["grid"], lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(colors["grid"])
        ax.set_ylim(-0.6, len(rows) - 0.4)

    def figure(n_rows, height_per_row=0.45):
        fig, ax = plt.subplots(figsize=(7.5, 0.8 + height_per_row * n_rows), layout="constrained")
        return fig, ax

    return figure, forest


@app.cell(hide_code=True)
def _(data, hashlib, mo, raw, results_dir, table):
    _rows = []
    for _stage in data["stages"]:
        _path = results_dir / f"{_stage['name']}.json"
        _rows.append([_stage["name"], f"`{raw[_stage['name']]['git_commit'][:7]}`", f"`{hashlib.sha256(_path.read_bytes()).hexdigest()[:16]}`"])
    mo.md(
        "\n\n".join(
            [
                "## Provenance",
                f"Results are {'**synthetic**' if data['synthetic'] else 'from the real CMS data'}. Each stage records the commit it ran at; "
                "all of them contain the registered code unchanged (see `DEVIATIONS.md`).",
                table(["Stage", "Commit", "sha256 of results file (first 16)"], _rows),
            ]
        )
    )
    return


@app.cell(hide_code=True)
def _(dashboard_data, data, json, mo):
    # The site's dashboard is built from the same function; confirm the committed copy matches these results.
    _committed = json.loads((dashboard_data.DEFAULT_OUT).read_text())
    _same = {k: v for k, v in _committed.items() if k != "built"} == {k: v for k, v in data.items() if k != "built"}
    mo.md(f"The post's dashboard data (`data.json`) {'matches' if _same else '**does not match**'} these results.")
    return


@app.cell(hide_code=True)
def _(data, mo, num):
    _v = data["validation"]
    mo.md(
        f"""
        ## Validation of the benchmark approximation

        Passed: **{"yes" if _v["passed"] else "no"}**. Calibration applied: {"yes" if _v["calibrated"] else "no"}.
        Measurement-error SD used in the decision model (pp of benchmark): {num(_v["sigma_v_model"], 2)}.
        """
    )
    return


@app.cell(hide_code=True)
def _(data, interval, mo, num, pval, table):
    _c = data["comparisons"]["rows"]
    _rows = [[r["label"], r["role"], f"{r['n_early']} / {r['n_stayer']}", num(r["mean"]), interval(r), pval(r["p"]), num(r["mde"]), r["verdict"] or ""] for r in _c]
    mo.md(
        "\n\n".join(
            [
                "## Who renewed early (H2b, H2a, H1)",
                "Early renewers minus stayers (Bayesian bootstrap; p-values from stratified permutation).",
                table(["Comparison", "Role", "n early / stayers", "Difference", "95% interval", "p", "MDE", "Verdict"], _rows),
            ]
        )
    )
    return


@app.cell
def _(data, figure, forest):
    _c = {r["key"]: r for r in data["comparisons"]["rows"]}
    _fig, _ax = figure(4)
    forest(_ax, [_c[k] for k in ("H2b_pull", "H2a_own", "regional_comp", "gain")], "Early renewers minus stayers, pp of benchmark")
    _fig
    return


@app.cell
def _(data, figure, forest):
    _c = {r["key"]: r for r in data["comparisons"]["rows"]}
    _fig, _ax = figure(2)
    forest(_ax, [_c[k] for k in ("H1_sav_rate_2020", "H1_sav_rate_2021")], "Early renewers minus stayers, savings rate (pp)")
    _fig
    return


@app.cell(hide_code=True)
def _(data, mo, num, pval, table):
    _h3 = data["h3"]
    _rows = [
        [
            r["label"],
            r["predicted"] or "",
            num(r["mean"], 2),
            f"{num(r['lo'], 2)} to {num(r['hi'], 2)}",
            num(r["p_positive"], 3),
            pval(r["test"]["p"]) if r["test"] else "",
            r["test"]["decision"] if r["test"] else "",
        ]
        for r in _h3["posterior"]["normal"]
    ]
    _o = _h3["overall_test"]
    _s = _h3["sample"]
    mo.md(
        "\n\n".join(
            [
                "## H3: the decision model",
                "Bayesian logistic regression of early renewal, with measurement error on the own-spending component; "
                f"{_s['n']} ACOs, {_s['early']} early renewers ({_s['excluded']['early']} early renewers and {_s['excluded']['stayer']} stayers "
                f"excluded for a missing predictor). Converged: {'yes' if _h3['converged'] else 'no'}. Coefficients are log-odds per 2 SD of a "
                "continuous predictor; tests are by direct simulation under the reduced model.",
                table(["Coefficient", "Predicted", "Posterior mean", "95% interval", "P(> 0)", "p", "Decision"], _rows),
                f"Overall test ({_o['statistic']}): observed {num(_o['observed'], 2)}, p = {pval(_o['p_value'])} ({_o['n_shuffles']:,} shuffles). "
                f"Power to detect the planned effects: {_h3['power_note']}.",
            ]
        )
    )
    return


@app.cell
def _(data, figure, forest):
    _rows = data["h3"]["posterior"]["normal"]
    _fig, _ax = figure(len(_rows))
    forest(_ax, _rows, "Posterior coefficient, log-odds (shaded: the Normal(0, 1) prior's 95% range)", band=data["h3"]["prior_band"]["normal"])
    _fig
    return


@app.cell(hide_code=True)
def _(data, interval, mo, num, pval, table):
    _h4 = data["h4"]
    _rows = [[r["label"], r["role"], num(r["mean"]), interval(r), pval(r["p"])] for r in _h4["estimates"]]
    _pre, _eq = _h4["pre_trend"], _h4["equivalence"]
    mo.md(
        "\n\n".join(
            [
                "## H4: spending after renewal",
                f"Difference-in-differences in per-capita spending, in percent; {_h4['sample']['early']} early renewers and "
                f"{_h4['sample']['comparison']} comparison ACOs. Verdict: **{_h4['verdict']}** (MDE {num(_h4['mde_percent'])}%).",
                table(["Estimate", "Role", "Percent", "95% interval", "p"], _rows),
                f"Pre-trend slope difference: {num(_pre['mean'], 3)} ({num(_pre['lo'], 3)} to {num(_pre['hi'], 3)}), p = {pval(_pre['p'])}. "
                f"Equivalence condition: the pre-trend bound scaled to the post period is {num(_eq['scaled_bound'], 3)} against "
                f"|H4| = {num(_eq['abs_h4'], 3)}, so it {'holds' if _eq['holds'] else 'does not hold'}.",
            ]
        )
    )
    return


@app.cell
def _(data, figure, forest):
    _rows = data["h4"]["estimates"]
    _fig, _ax = figure(len(_rows))
    forest(_ax, _rows, "Early renewers minus comparison: change in per-capita spending growth (%)")
    _fig
    return


@app.cell
def _(colors, data, plt):
    _pts = data["h4"]["event_study"]
    _fig, _ax = plt.subplots(figsize=(7.5, 3.2), layout="constrained")
    _ax.axhline(0, color=colors["muted"], lw=1)
    for _p in _pts:
        if not _p["reference"]:
            _ax.plot([_p["year"], _p["year"]], [_p["lo"], _p["hi"]], color=colors["mark"], lw=2, solid_capstyle="round")
        _ax.plot(_p["year"], _p["mean"], "o", color=colors["muted"] if _p["reference"] else colors["mark"], ms=6, mec="white", mew=1.5)
    _ax.set_xticks([p["year"] for p in _pts])
    _ax.margins(x=0.05, y=0.1)
    _ax.set_ylabel("Percent, relative to 2021", color=colors["ink"])
    _ax.set_title("Two-way fixed effects event study (2021 is the reference year)", color=colors["ink"], fontsize=10, loc="left")
    _ax.tick_params(colors=colors["muted"], length=0)
    _ax.grid(axis="y", color=colors["grid"], lw=0.8)
    _ax.set_axisbelow(True)
    for _side in ("top", "right", "left"):
        _ax.spines[_side].set_visible(False)
    _ax.spines["bottom"].set_color(colors["grid"])
    _fig
    return


@app.cell(hide_code=True)
def _(data, mo, table):
    _rows = [[r["claim"], r["confirmatory"], r["conventional"], "yes" if r["agree"] else "**no**"] for r in data["agreement"]]
    mo.md(
        "## Registered and conventional methods\n\n"
        + table(["Claim", "Registered method", "Conventional method", "Agree"], _rows)
        + "\n\nThe plan's agreement table (section 5.7) calls H4 undetermined unless p < 0.05 in a direction; "
        'that is the same verdict as "no detectable difference" in the H4 section (section 7, rule 5).'
    )
    return


@app.cell(hide_code=True)
def _(data, interval, mo, num, pval, table):
    _rob = data["robustness"]
    _parts = []
    for _g in _rob["groups"] + _rob["h3"]:
        _digits = 2 if _g["unit"] == "log-odds" else 1
        _rows = [[r["label"], num(r["mean"], _digits), interval(r, _digits), pval(r["p"]), "" if r.get("converged", True) else "not converged"] for r in _g["rows"]]
        _parts.append(f"**{_g['label']}** ({_g['unit']})\n\n" + table(["Analysis", "Estimate", "95% interval", "p", ""], _rows))
    mo.md(
        "## Robustness\n\nThe plan's section 5.5 items that rerun each confirmatory estimate. They do not change the "
        "decisions. H3 rows are the coefficient in each refit.\n\n" + "\n\n".join(_parts)
    )
    return


@app.cell(hide_code=True)
def _(data, interval, mo, num, pval, table):
    _exp = data["exploratory"]
    _parts = []
    for _g in _exp["alternative_exposures"]:
        _digits = 2 if _g["unit"] == "log-odds" else 1
        _rows = [[r["label"], num(r["mean"], _digits), interval(r, _digits), pval(r["p"])] for r in _g["rows"]]
        _parts.append(f"**{_g['label']}** ({_g['unit']})\n\n" + table(["Measure", "Estimate", "95% interval", "p"], _rows))
    if _exp["region"]:
        _rows = [[r["label"], num(r["mean"], 2), interval(r, 2)] for r in _exp["region"]["rows"]]
        _parts.append("**Census region in the H3 model** (log-odds)\n\n" + table(["Region", "Posterior mean", "95% interval"], _rows))
    _groups = _exp["groups"]
    _rows = [[label] + [f"{num(_groups[g][v]['mean'])} (n = {_groups[g][v]['n']})" for g in _groups] for v, label in _exp["described"].items()]
    _names = {"early": "Early renewers", "leaver": "Leavers", "stayer": "Stayers"}
    _parts.append("**Means by group**\n\n" + table(["Variable"] + [_names.get(g, g) for g in _groups], _rows))
    mo.md("## Exploratory\n\nLabeled exploratory in the plan (section 5.6): no verdicts.\n\n" + "\n\n".join(_parts))
    return


if __name__ == "__main__":
    app.run()
