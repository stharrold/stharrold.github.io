"""Render Slides-type slide files to 1920x1080 PNGs with headless Chromium.

Usage: python render.py <slides_dir> <out_dir> [slide_id ...]
Reads deck.json order from <slides_dir>/../deck.json when no ids are given.
"""

import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SCRATCH = Path(__file__).resolve().parent.parent
FONTS = SCRATCH / "fonts"
DOMINE = next(FONTS.rglob("domine-latin-wght-normal.woff2"))
PUBSANS = next(FONTS.rglob("public-sans-latin-wght-normal.woff2"))

# Simple stroke icons (24x24 viewBox) for the x-icon names this deck uses.
ICONS = {
    "Clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "Lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "Wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    "CheckCircle": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
    "Search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "Verified": (
        '<path d="M12 3l2.4 1.8 3-.2.9 2.9 2.4 1.8-1 2.8 1 2.8-2.4 1.8-.9 2.9-3-.2L12 21l-2.4-1.8-3 .2-.9-2.9L3.3 14.7l1-2.8-1-2.8 2.4-1.8.9-2.9 3 .2z"/>'
        '<path d="M8.5 12l2.5 2.5 4.5-5"/>'
    ),
}


def style_of(tag: str) -> str:
    m = re.search(r'style="([^"]*)"', tag)
    return m.group(1) if m else ""


def convert_custom(html: str) -> str:
    def shape(m):
        tag = m.group(0)
        kind = re.search(r'kind="([^"]+)"', tag).group(1)
        st = style_of(tag)
        if kind == "ellipse":
            return f'<div style="{st};border-radius:50%"></div>'
        if kind == "arrow-right":
            bg = re.search(r"background:\s*([^;]+)", st).group(1).strip()
            st2 = re.sub(r"background:[^;]+;?", "", st)
            return f'<svg viewBox="0 0 100 50" preserveAspectRatio="none" style="{st2};flex:none"><path d="M0 15H60V0L100 25L60 50V35H0Z" fill="{bg}"/></svg>'
        return f'<div style="{st}"></div>'

    def icon(m):
        tag = m.group(0)
        name = re.search(r'name="([^"]+)"', tag).group(1)
        st = style_of(tag)
        return (
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" style="{st};flex:none">'
            f"{ICONS.get(name, '')}</svg>"
        )

    html = re.sub(r"<x-shape[^>]*>\s*</x-shape>", shape, html)
    html = re.sub(r"<x-icon[^>]*>\s*</x-icon>", icon, html)
    return html


def page(section: str) -> str:
    section = re.sub(r"<aside>.*?</aside>", "", section, flags=re.S)
    section = convert_custom(section)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Domine';src:url('{DOMINE.as_uri()}');font-weight:400 700}}
@font-face{{font-family:'Public Sans';src:url('{PUBSANS.as_uri()}');font-weight:100 900}}
*{{margin:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;font-family:'Public Sans',Arial,sans-serif}}
section{{position:relative;width:1920px;height:1080px;overflow:hidden}}
section > *{{flex-shrink:0}}
h1,h2,h3{{font-weight:600}}
table{{border-collapse:collapse;width:100%}}
th,td{{padding:0.35em 0.6em;border-bottom:1px solid #d9d4ca;text-align:left}}
th{{font-weight:700}}
ul{{padding-left:1.2em}}
a{{color:#2B6595}}
</style></head><body>{section}</body></html>"""


# Reveal groups: slide id -> list of selector groups; group k appears at step k (k >= 1).
REVEALS = {
    "cancel-example": [
        ["section > p:nth-of-type(2) > span:nth-of-type(2)"],
        ["section > p:nth-of-type(2) > span:nth-of-type(3)", "section > h2", "section > p:nth-of-type(3)"],
    ],
    "ranges": [
        ["section > div:nth-of-type(2) > div:nth-of-type(2)"],
    ],
    "f3-cancel": [
        ["section > div:nth-of-type(2) > div:nth-of-type(2)"],
        ["section > div:nth-of-type(2) > div:nth-of-type(3)"],
        ["section > div:nth-of-type(3)"],
    ],
    "f5-after": [
        ["section > div:nth-of-type(3)"],
    ],
}


def main():
    slides_dir = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    ids = sys.argv[3:] or json.loads((slides_dir.parent / "deck.json").read_text())["order"]
    clip = 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        tmp = out / "_page.html"
        for sid in ids:
            src = (slides_dir / f"{sid}.html").read_text()
            if re.match(r"<section[^>]*\shidden[\s>]", src):
                continue
            clip += 1
            groups = REVEALS.get(sid, [])
            tmp.write_text(page(src))
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            steps = len(groups) + 1
            for s in range(steps):
                for k, sels in enumerate(groups, 1):
                    vis = "visible" if k <= s else "hidden"
                    for sel in sels:
                        pg.eval_on_selector_all(sel, f"els => els.forEach(e => e.style.visibility = '{vis}')")
                label = f"{clip:02d}" + (chr(ord("a") + s) if steps > 1 else "")
                pg.screenshot(path=str(out / f"{label}-{sid}.png"))
        tmp.unlink(missing_ok=True)
        b.close()


if __name__ == "__main__":
    main()
