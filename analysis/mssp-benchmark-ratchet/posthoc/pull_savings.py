"""Post hoc: how closely the regional pull tracks the ACO's own savings.

NOT REGISTERED. Written on 2026-10-28, after every registered result had been read, in response to a review of the
i-JMR manuscript: the regional pull is measured against the current benchmark, which was set from the ACO's own earlier
spending, so a specialist will ask whether the pull is past savings by another name. This script reports rank
correlations of the pull with the PY2020 and PY2021 savings rates and with the own-spending component, for the ACOs in
the registered group comparisons (early renewers and stayers with the expected-gain variables). It uses the registered
pipeline's tables unchanged (`ratchet.build`), changes no registered file, estimates nothing new and decides nothing.

Writes posthoc/pull_savings.json. Run from the repository root (about 30 seconds; builds the database once):

    uv run --group analysis python analysis/mssp-benchmark-ratchet/posthoc/pull_savings.py
"""

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from ratchet import build  # noqa: E402

PAIRS = {"sav_rate_2020": "savings rate, PY2020", "sav_rate_2021": "savings rate, PY2021", "own": "own-spending component"}


def correlations(d, label: str) -> dict:
    out = {}
    for col, name in PAIRS.items():
        x = d[["pull", col]].dropna()
        out[col] = {
            "with": name,
            "n": int(len(x)),
            "spearman": float(stats.spearmanr(x.pull, x[col]).statistic),
            "pearson": float(stats.pearsonr(x.pull, x[col]).statistic),
        }
    return {"sample": label, "correlations": out}


def main() -> None:
    con = build.connect(stage="full", descriptive=True)
    d = con.sql("select grp, pull, own, sav_rate_2020, sav_rate_2021 from analysis where grp in ('early', 'stayer') and pull is not null").df()
    out = {
        "registered": False,
        "note": "Post hoc, exploratory; written after all registered results were read (see the module docstring).",
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip(),
        "units": "pull and own-spending component in percentage points of the current benchmark; savings rates in percentage points",
        "pooled": correlations(d, "early renewers and stayers"),
        "stayers": correlations(d[d.grp == "stayer"], "stayers"),
        "early": correlations(d[d.grp == "early"], "early renewers"),
        "n_by_group": {g: int((d.grp == g).sum()) for g in ("early", "stayer")},
    }
    path = HERE / "pull_savings.json"
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
