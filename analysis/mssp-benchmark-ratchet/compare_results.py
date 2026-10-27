"""Compare a rerun's results files with the committed ones in results/.

For each stage file present in both directories, every number is compared (to a relative tolerance) and every other
value exactly. Run metadata that is expected to differ is skipped: when and where the run happened (`generated`,
`git_commit`, `settings.data_dir`, `settings.workers`). Standard library only; outside the registered analysis code.

Usage, from the repository root:

    python3 analysis/mssp-benchmark-ratchet/compare_results.py <rerun out-dir>
    python3 analysis/mssp-benchmark-ratchet/compare_results.py <rerun out-dir> --rtol 1e-6 --reference <other dir>
"""

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP = {("generated",), ("git_commit",), ("settings", "data_dir"), ("settings", "workers")}


def differences(a, b, rtol: float, path: tuple = ()) -> list[str]:
    if path in SKIP:
        return []
    where = ".".join(map(str, path)) or "(top)"
    if isinstance(a, dict) and isinstance(b, dict):
        out = [f"{where}: key {k!r} only in one file" for k in sorted(set(a) ^ set(b), key=str)]
        for k in sorted(set(a) & set(b), key=str):
            out += differences(a[k], b[k], rtol, path + (k,))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{where}: {len(a)} items vs {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b, strict=True)) for d in differences(x, y, rtol, path + (i,))]
    numbers = (int, float)
    if isinstance(a, numbers) and isinstance(b, numbers) and not isinstance(a, bool) and not isinstance(b, bool):
        return [] if math.isclose(a, b, rel_tol=rtol, abs_tol=rtol) else [f"{where}: {a!r} vs {b!r}"]
    return [] if a == b else [f"{where}: {a!r} vs {b!r}"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("rerun", type=Path, help="the --out-dir of the rerun")
    parser.add_argument("--reference", type=Path, default=HERE / "results", help="the committed results (default results/)")
    parser.add_argument("--rtol", type=float, default=1e-9, help="relative tolerance for numbers (default 1e-9)")
    args = parser.parse_args()
    files = sorted(p.name for p in args.rerun.glob("*.json") if (args.reference / p.name).is_file())
    if not files:
        sys.exit(f"no results files in {args.rerun} that are also in {args.reference}")
    failed = 0
    for name in files:
        diffs = differences(json.loads((args.rerun / name).read_text()), json.loads((args.reference / name).read_text()), args.rtol)
        print(f"{'same     ' if not diffs else 'DIFFERENT'} {name}" + (f" ({len(diffs)} values)" if diffs else ""))
        for d in diffs[:10]:
            print(f"    {d}")
        failed += bool(diffs)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
