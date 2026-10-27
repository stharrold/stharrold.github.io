"""Turn a saved Scholar Labs result (the skill's raw JSON) into one record per paper.

Each paper on a Scholar Labs page is: optional access lines ("[PDF] host", "Quick read - nih.gov"), the title, an
"authors - venue, year - host" line, a summary sentence, labeled bullets ("Label: text"), and a footer ("Save Cite
Cited by N Related articles All K versions"). The raw JSON keeps titles and URLs in `sources` and everything else in
the page text `body`; this joins them. The text is Scholar Labs' own, copied verbatim. Standard library only.

Usage: python3 parse_scholar_labs.py <raw.json> [<raw.json> ...]   (writes <name>_papers.json next to each)
"""

import json
import re
import sys
from pathlib import Path

BULLET = re.compile(r"^([A-Z][^:]{2,80}): (.+)$")
FOOTER = re.compile(r"Save Cite(?: Cited by (\d+))?")


def _norm(text: str) -> str:
    return re.sub(r"^\[(PDF|HTML|BOOK|CITATION)\]\s*", "", text).rstrip(" …").strip()


def parse(raw: dict) -> list[dict]:
    """Papers are delimited by their "Save Cite ..." footers, in the same order as `sources`."""
    lines = [ln.strip() for ln in raw["body"].split("\n") if ln.strip()]
    footers = [i for i, ln in enumerate(lines) if ln.startswith("Save Cite")]
    papers = []
    for k, source in enumerate(raw["sources"]):
        lo = footers[k - 1] + 1 if k > 0 else 0
        hi = footers[k] if k < len(footers) else len(lines)
        head = _norm(source["title"])[:50]
        start = next((i for i in range(lo, hi) if _norm(lines[i]).startswith(head)), None)
        if start is None:
            papers.append({**source, "parsed": False})
            continue
        block = lines[start + 1 : hi]
        footer = FOOTER.match(lines[hi]) if hi < len(lines) else None
        bullets = [{"label": m.group(1), "text": m.group(2)} for m in map(BULLET.match, block[2:]) if m]
        papers.append(
            {
                "title": source["title"],
                "url": source["url"],
                "byline": block[0] if block else None,
                "summary": block[1] if len(block) > 1 else None,
                "bullets": bullets,
                "cited_by": int(footer.group(1)) if footer and footer.group(1) else None,
                "parsed": True,
            }
        )
    return papers


def main() -> None:
    for name in sys.argv[1:]:
        path = Path(name)
        raw = json.loads(path.read_text())
        papers = parse(raw)
        out = path.with_name(path.name.replace("_raw", "").removesuffix(".json") + "_papers.json")
        out.write_text(json.dumps({"query_url": raw.get("url"), "papers": papers}, indent=1, ensure_ascii=False) + "\n")
        print(f"{out.name}: {len(papers)} papers, {sum(len(p.get('bullets', [])) for p in papers)} bullets, {sum(not p['parsed'] for p in papers)} unparsed")


if __name__ == "__main__":
    main()
