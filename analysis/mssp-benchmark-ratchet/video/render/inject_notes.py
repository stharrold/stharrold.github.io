"""Write the narration script into each visible slide's speaker notes (<aside>), labeled by clip.

Usage: python render/inject_notes.py project/slides
Also writes out/transcript-for-youtube.txt (plain script for YouTube caption auto-sync).
Hidden slides keep their notes (the longer live-talk text).
"""

import html
import re
import sys
from pathlib import Path

slides = Path(sys.argv[1])
ns = {}
exec(Path(__file__).with_name("script_video.py").read_text(), ns)
SCRIPT = ns["SCRIPT"]

paras = []
for sid, parts in SCRIPT:
    text = "\n\n".join(f"[Clip {lab}] {t}" for lab, t in parts)
    assert text.isascii() and len(text) <= 4000, sid  # Slides notes limit is 4,000 characters
    p = slides / f"{sid}.html"
    src = p.read_text()
    assert src.count("<aside>") == 1, sid
    p.write_text(re.sub(r"<aside>.*?</aside>", lambda m, text=text: "<aside>" + html.escape(text, quote=False) + "</aside>", src, flags=re.S))
    for _, t in parts:
        paras += [x.strip() for x in t.split("\n\n") if x.strip()]

out = Path("out")
out.mkdir(exist_ok=True)
(out / "transcript-for-youtube.txt").write_text("\n\n".join(paras) + "\n")
words = sum(len(t.split()) for _, parts in SCRIPT for _, t in parts)
print(f"{len(SCRIPT)} slides, {sum(len(p) for _, p in SCRIPT)} clips, {words} words")
