"""Render YouTube thumbnail variants (1280x720 PNG)."""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SCRATCH = Path(__file__).resolve().parent.parent
DOMINE = next((SCRATCH / "fonts").rglob("domine-latin-wght-normal.woff2")).as_uri()
PUB = next((SCRATCH / "fonts").rglob("public-sans-latin-wght-normal.woff2")).as_uri()

HEAD = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Domine';src:url('{DOMINE}');font-weight:400 700}}
@font-face{{font-family:'Public Sans';src:url('{PUB}');font-weight:100 900}}
*{{margin:0;box-sizing:border-box}}
body{{width:1280px;height:720px;overflow:hidden;font-family:'Public Sans',sans-serif}}
</style></head><body>"""

ARROW = (
    '<svg width="120" height="120" viewBox="0 0 24 24">'
    '<path d="M12 3v15M5 12l7 7 7-7" fill="none" stroke="#F0A06A" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

A = (
    HEAD
    + f"""
<div style="width:1280px;height:720px;background:#1B2A3A;display:flex;align-items:center;padding:0 72px;gap:56px">
  <div style="flex:1;display:flex;flex-direction:column;gap:20px">
    <div style="font-family:Domine;font-weight:700;font-size:150px;line-height:1;color:#F7F4EE">Why<br>reset?</div>
    <div style="font-weight:700;font-size:40px;letter-spacing:3px;text-transform:uppercase;color:#F0A06A">Medicare puzzle</div>
  </div>
  <div style="width:420px;display:flex;flex-direction:column;align-items:center;gap:8px">
    <div style="font-weight:800;font-size:44px;letter-spacing:3px;color:#8FA1B3">TARGET</div>
    {ARROW}
    <div style="font-family:Domine;font-weight:700;font-size:150px;line-height:1;color:#F0A06A">-1.3%</div>
  </div>
</div></body></html>"""
)

B = (
    HEAD
    + """
<div style="width:1280px;height:720px;background:#F7F4EE;display:flex;align-items:center;padding:0 72px;gap:48px">
  <div style="flex:1;font-family:Domine;font-weight:700;font-size:140px;line-height:1.02;color:#1B2A3A">Lower<br>target<span style="color:#B4501A">?!</span></div>
  <div style="width:460px;display:flex;flex-direction:column;align-items:center;gap:8px">
    <div style="font-family:Domine;font-weight:700;font-size:170px;line-height:1;color:#B4501A">2 in 3</div>
    <div style="font-weight:800;font-size:44px;letter-spacing:2px;color:#1B2A3A">GOT ONE</div>
  </div>
</div></body></html>"""
)


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        for name, html in (("thumbnail-a.png", A), ("thumbnail-b.png", B)):
            tmp = out / "_t.html"
            tmp.write_text(html)
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(out / name))
            tmp.unlink()
        b.close()


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
