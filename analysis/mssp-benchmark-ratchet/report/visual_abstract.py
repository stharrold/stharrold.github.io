"""Visual abstract for the post: one 1200 x 630 image (the link-preview size) built from the dashboard data.

Reporting only: every number comes from content/static/<slug>/data.json (built from results/ by dashboard_data.py),
so the image cannot drift from the results. Writes visual-abstract.png and visual-abstract.svg next to data.json.

Run from the repository root (matplotlib is not in uv.lock, so it is pinned here, as for the results notebook):

    uv run --with matplotlib==3.11.2 python analysis/mssp-benchmark-ratchet/report/visual_abstract.py
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dashboard_data  # noqa: E402

# Reference palette (light mode): one mark color, text inks, recessive grid.
SURFACE, INK, MUTED, GRID, MARK, BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#dddcd7", "#2a78d6", "#eef3fb"


def fmt(x: float, digits: int = 1, sign: bool = True) -> str:
    text = f"{x:+.{digits}f}" if sign else f"{x:.{digits}f}"
    return text.replace("-", "−")


def forest(ax, rows, xlabel, xlim):
    """Rows of (label, mean, lo, hi, bold); one interval per row with its value printed beside it."""
    ys = list(range(len(rows)))[::-1]
    ax.axvline(0, color=MUTED, lw=1, zorder=1)
    for y, (label, mean, lo, hi, bold) in zip(ys, rows, strict=True):
        ax.plot([lo, hi], [y, y], color=MARK, lw=3, solid_capstyle="round", zorder=2)
        ax.plot(mean, y, "o", color=MARK, ms=9, mec=SURFACE, mew=2, zorder=3)
        ax.text(
            xlim[0],
            y + 0.34,
            label,
            ha="left",
            va="bottom",
            fontsize=11.5,
            color=INK,
            fontweight="bold" if bold else "normal",
            bbox={"facecolor": SURFACE, "edgecolor": "none", "pad": 1.5},
            zorder=4,
        )
        # The value sits in its own column right of the plot, on the interval's line, so it never meets the label.
        ax.text(1.04, y, f"{fmt(mean)} [{fmt(lo)}, {fmt(hi)}]", transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=10.5, color=INK)
    ax.set_xlim(*xlim)
    ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.set_yticks([])
    ax.set_xlabel(xlabel, fontsize=10, color=MUTED, labelpad=4)
    ax.tick_params(axis="x", colors=MUTED, labelsize=9.5, length=0)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)


def main() -> None:
    data = json.loads((dashboard_data.DEFAULT_OUT).read_text())
    c = {r["key"]: r for r in data["comparisons"]["rows"]}
    h4 = data["h4"]["estimates"][0]
    n_early, n_stayer = c["H1_sav_rate_2020"]["n_early"], c["H1_sav_rate_2020"]["n_stayer"]

    fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=SURFACE)
    # Title band.
    fig.text(0.035, 0.925, "Why did Medicare ACOs reset their benchmarks early?", fontsize=24, fontweight="bold", color=INK, va="center")
    fig.text(
        0.035,
        0.862,
        f"A pre-registered study of Shared Savings Program ACOs: {n_early} renewed early in 2022, {n_stayer} stayed. Estimates [95% intervals]",
        fontsize=13,
        color=MUTED,
        va="center",
    )

    # Left panel: question and design.
    left = fig.add_axes((0.035, 0.205, 0.255, 0.58))
    left.axis("off")
    left.add_patch(plt.Rectangle((0, 0), 1, 1, transform=left.transAxes, color=BAND, zorder=0))
    lines = [
        ("The question", 0.92, 14, "bold", INK),
        ("Did ACOs renew early to get a", 0.80, 11.5, "normal", INK),
        ("higher benchmark, and did", 0.72, 11.5, "normal", INK),
        ("renewing change their spending?", 0.64, 11.5, "normal", INK),
        ("The design", 0.48, 14, "bold", INK),
        ("Public CMS data, 2019-2024", 0.36, 11.5, "normal", INK),
        ("Plan registered on OSF before", 0.28, 11.5, "normal", INK),
        ("any outcome was read", 0.20, 11.5, "normal", INK),
        ("Decision rules fixed in advance", 0.10, 11.5, "normal", INK),
    ]
    for text, y, size, weight, color in lines:
        left.text(0.07, y, text, fontsize=size, fontweight=weight, color=color, va="center", transform=left.transAxes)

    # Middle panel: who renewed early.
    fig.text(0.33, 0.765, "Who renewed early", fontsize=14, fontweight="bold", color=INK, va="center")
    mid = fig.add_axes((0.33, 0.27, 0.255, 0.44))
    rows = [
        ("Region spends more than benchmark", c["H2b_pull"]["mean"], c["H2b_pull"]["lo"], c["H2b_pull"]["hi"], True),
        ("Regional part of a reset", c["regional_comp"]["mean"], c["regional_comp"]["lo"], c["regional_comp"]["hi"], False),
        ("Own-spending part of a reset", c["H2a_own"]["mean"], c["H2a_own"]["lo"], c["H2a_own"]["hi"], False),
        ("Total expected gain from a reset", c["gain"]["mean"], c["gain"]["lo"], c["gain"]["hi"], False),
    ]
    forest(mid, rows, "Early renewers minus stayers, % of benchmark", (-6.5, 6.5))

    # Right panel: spending after renewal.
    fig.text(0.735, 0.765, "Spending after renewal", fontsize=14, fontweight="bold", color=INK, va="center")
    right = fig.add_axes((0.735, 0.535, 0.13, 0.175))
    forest(right, [("Change in spending growth", h4["mean"], h4["lo"], h4["hi"], True)], "Early renewers minus comparison, %", (-6.5, 6.5))
    note = ["No detectable difference, 2022-2024.", "A pre-existing trend could hide", "a small effect, so it is not read", "as an effect of renewing."]
    for i, text in enumerate(note):
        fig.text(0.735, 0.43 - i * 0.042, text, fontsize=11, color=INK, va="center")

    # Takeaway band.
    fig.patches.append(plt.Rectangle((0.035, 0.035), 0.93, 0.125, transform=fig.transFigure, color=BAND, zorder=0))
    fig.text(
        0.055,
        0.115,
        "Early renewers were low-cost relative to their regions, and almost all moved to the 75% sharing rate,",
        fontsize=13,
        fontweight="bold",
        color=INK,
        va="center",
    )
    fig.text(
        0.055,
        0.07,
        "but the reset did not raise their benchmarks on average. Associations, not effects; 2022 rules.",
        fontsize=12,
        color=INK,
        va="center",
    )
    fig.text(0.955, 0.07, "stharrold.github.io", fontsize=10.5, color=MUTED, va="center", ha="right")

    out = dashboard_data.DEFAULT_OUT.parent
    fig.savefig(out / "visual-abstract.png", dpi=100, facecolor=SURFACE)
    fig.savefig(out / "visual-abstract.svg", facecolor=SURFACE, metadata={"Date": None})
    print(f"wrote {out / 'visual-abstract.png'} and .svg")


if __name__ == "__main__":
    main()
