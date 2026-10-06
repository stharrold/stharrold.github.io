"""Print a Markdown summary of a lychee JSON report (used for the link-check job summary)."""

import json
import sys


def main(path):
    report = json.load(open(path))
    counts = {k: v for k, v in report.items() if isinstance(v, int)}
    print("## Link check (log only)\n")
    print("| Metric | Count |\n|---|---|")
    for key, value in counts.items():
        print(f"| {key} | {value} |")
    error_map = report.get("error_map") or report.get("fail_map") or {}
    if not error_map:
        print("\nNo broken links.")
        return
    print("\n### Broken links by page\n")
    for page, entries in sorted(error_map.items()):
        print(f"**{page}**\n")
        for entry in entries:
            status = entry.get("status", {})
            detail = status.get("text") or status.get("code") or status if isinstance(status, dict) else status
            print(f"- {entry.get('url')} ({detail})")
        print()


if __name__ == "__main__":
    main(sys.argv[1])
