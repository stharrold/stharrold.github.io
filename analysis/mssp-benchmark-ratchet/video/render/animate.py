"""Animated clips: motion on the slide element the narration is pointing at, started on the word that names it.

Usage: python render/animate.py <root> [LABEL ...]
Needs out/timeline.json (build_video.py, --audio-only is enough), vo/words/ (words.py), vo/wav/ (vo_prepare.py)
and project/slides/. Writes anim/<label>.mp4 for each clip in CUES (or the labels given), which build_video.py
then uses instead of the clip's still frame, and out/anim_check/<label>.png, frames across each motion.

Each cue names an element, a kind of motion and an anchor: words from the narration (as transcribed, numbers
as words) and an offset in seconds. The motion starts 0.15 s before the anchor's first word is heard: Whisper's
word start, moved to the first 10 ms in the word louder than -40 dBFS in the recording, since Whisper often
starts a word at the end of the pause before it. Rules: nothing moves while the clip crossfades in (the first
XF seconds; a cue said then starts as the fade ends), and the last frame must match the still frame from render.py (checked by PSNR), so the finished
state always matches the deck; `dim` (holding the eye on one element) is left out of that check.
"""

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from playwright.sync_api import sync_playwright

ROOT = Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("render", HERE / "render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)

FPS = 30
XF = 0.4  # crossfade, as in build_video.py
EARLY = 0.15  # start a motion this long before its word is heard
DUR = {"build": 0.6, "count": 1.0, "grow": 0.8, "draw": 0.5, "dim": 0.6}

ROW = "section > div:nth-of-type(2) > div:nth-of-type({})"  # f3-cancel chart rows
CARD = "section > div:nth-of-type(2) > div:nth-of-type({})"  # counts cards

# label -> [(selector, kind, anchor words, offset s, options)]
CUES = {
    "10": [
        (CARD.format(1), "build", "twenty nine renewed", 0, {}),
        (CARD.format(1) + " > p:nth-of-type(1)", "count", "twenty nine renewed", 0, {}),
        (CARD.format(2), "build", "two hundred seventy seven stayed", 0, {}),
        (CARD.format(2) + " > p:nth-of-type(1)", "count", "two hundred seventy seven stayed", 0, {}),
        (CARD.format(3), "build", "twenty eight left", 0, {}),
        (CARD.format(3) + " > p:nth-of-type(1)", "count", "twenty eight left", 0, {}),
        # "So what made those twenty-nine different?": the other two step back
        (CARD.format(2), "dim", "twenty nine different", 0, {}),
        (CARD.format(3), "dim", "twenty nine different", 0, {}),
    ],
    "18a": [
        (ROW.format(1) + " > div > div:nth-of-type(2)", "grow", "blue bar", 0, {"origin": "left"}),
        (ROW.format(1) + " > div > div:nth-of-type(3)", "draw", "blue bar", 0.8, {}),
        (ROW.format(1) + " > p:nth-of-type(2)", "build", "one and a half points", 0, {}),
    ],
    "18b": [
        (ROW.format(2) + " > div > div:nth-of-type(2)", "grow", "orange bar", 0, {"origin": "right"}),
        (ROW.format(2) + " > div > div:nth-of-type(3)", "draw", "orange bar", 0.8, {}),
        (ROW.format(2) + " > p:nth-of-type(2)", "build", "about two points", 0, {}),
    ],
    "18c": [
        (ROW.format(3) + " > div > div:nth-of-type(2)", "grow", "gray bar", 0, {"origin": "right"}),
        (ROW.format(3) + " > p:nth-of-type(2)", "build", "minus half a point", 0, {}),
        (ROW.format(3) + " > div > div:nth-of-type(3)", "draw", "range that crosses zero", 0, {}),
    ],
    "18d": [
        ("section > div:nth-of-type(3)", "build", "checked what actually", 0, {}),
    ],
}

# Sets every animated element's style for time t (seconds into the clip). Motion is a pure function of t, so
# frames come out the same on every run.
FRAME_JS = """([cues, t, final]) => {
  const ease = p => 1 - Math.pow(1 - Math.min(Math.max(p, 0), 1), 3);
  const fmt = (el, e) => {
    const m = el.dataset.final.match(/^([^0-9]*)([0-9][0-9,]*(?:[.][0-9]+)?)(.*)$/s);
    const dec = (m[2].split(".")[1] || "").length, v = parseFloat(m[2].replace(/,/g, "")) * e;
    const s = v.toLocaleString("en-US", {minimumFractionDigits: dec, maximumFractionDigits: dec, useGrouping: m[2].includes(",")});
    return m[1] + s + m[3];
  };
  const styles = new Map();
  for (const c of cues) {
    const el = document.querySelector(c.sel);
    if (!styles.has(el)) styles.set(el, {opacity: 1, transforms: []});
    const st = styles.get(el);
    const e = ease((t - c.start) / c.dur);
    if (c.kind === "build") { st.opacity *= e; st.transforms.push(`translateY(${24 * (1 - e)}px)`); }
    if (c.kind === "grow") { st.transforms.push(`scaleX(${e})`); el.style.transformOrigin = c.origin; }
    if (c.kind === "draw") { st.transforms.push(`scaleX(${e})`); el.style.transformOrigin = "center"; }
    if (c.kind === "dim" && !final) st.opacity *= 1 - 0.65 * e;
    if (c.kind === "count") { el.dataset.final ??= el.textContent; el.textContent = fmt(el, e); }
  }
  for (const [el, st] of styles) { el.style.opacity = st.opacity; el.style.transform = st.transforms.join(" "); }
}"""

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def say_int(n: int) -> list[str]:
    if n < 20:
        return [ONES[n]]
    if n < 100:
        return [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
    for size, name in ((10**6, "million"), (1000, "thousand"), (100, "hundred")):
        if n >= size:
            return say_int(n // size) + [name] + (say_int(n % size) if n % size else [])
    return []


def tokens(word: str) -> list[str]:
    """A transcribed word as spoken words: "29" -> twenty nine, "1st," -> one st, "two-thirds" -> two thirds."""
    out = []
    for part in re.split(r"[-\s]+", word.lower()):
        part = part.strip(".,?!:;'\"")
        m = re.fullmatch(r"([$+]?)(\d[\d,]*)(?:\.(\d+))?(%?)([a-z]*)", part)
        if m:
            out += say_int(int(m.group(2).replace(",", ""))) + (["point"] + [ONES[int(d)] for d in m.group(3)] if m.group(3) else [])
            out += (["percent"] if m.group(4) else []) + ([m.group(5)] if m.group(5) else [])
        elif part:
            out.append(re.sub(r"[^a-z']", "", part))
    return [t for t in out if t]


def onset(rec: str, s: float, e: float) -> float:
    """First 10 ms frame in [s, e] louder than -40 dBFS in the recording; s if none."""
    x, sr = sf.read(ROOT / "vo" / "wav" / f"{rec}.wav", dtype="float32", always_2d=True)
    x = x.mean(1)[int(s * sr) : int(e * sr)]
    h = int(0.01 * sr)
    k = len(x) // h
    if k == 0:
        return s
    loud = np.flatnonzero(20 * np.log10(np.sqrt((x[: k * h].reshape(k, h) ** 2).mean(1)) + 1e-9) > -40)
    return s + (loud[0] * 0.01 if len(loud) else 0.0)


def clip_time(clip: dict, t: float) -> float:
    """A time in the recording, in seconds into the clip (see build_video.py's timeline fields)."""
    t_clip = clip["lead_s"] + t - clip["trim_start_s"]
    t_clip += sum(add for at, add in clip["pauses"] if t >= at)
    t_clip -= sum(t1 - t0 - patch for t0, t1, patch in clip["cuts"] if t >= t1)
    return t_clip


def anchor_time(clip: dict, phrase: str) -> float:
    rec = Path(clip["recording"]).stem
    words = json.loads((ROOT / "vo" / "words" / f"{rec}.json").read_text())["words"]
    toks, owner = [], []
    for i, w in enumerate(words):
        for t in tokens(w["w"]):
            toks.append(t)
            owner.append(i)
    want = phrase.split()
    for i in range(len(toks) - len(want) + 1):
        if toks[i : i + len(want)] == want:
            w = words[owner[i]]
            return clip_time(clip, onset(rec, w["s"], w["e"]))
    raise SystemExit(f"{clip['label']}: '{phrase}' is not in {rec}'s transcript: {' '.join(toks)}")


def psnr(a: Path, b: Path) -> float:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(a), "-i", str(b), "-lavfi", "psnr", "-f", "null", "-"], capture_output=True, text=True).stderr
    v = re.search(r"average:(\S+)", r).group(1)
    return float("inf") if v == "inf" else float(v)


def main() -> None:
    timeline = {c["label"]: c for c in json.loads((ROOT / "out" / "timeline.json").read_text())["clips"]}
    labels = sys.argv[2:] or list(CUES)
    (ROOT / "anim").mkdir(exist_ok=True)
    (ROOT / "out" / "anim_check").mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": 1920, "height": 1080})
        for lab in labels:
            clip = timeline[lab]
            sid = clip["frame"].split("-", 1)[1].removesuffix(".png")
            total = clip["dur"] + XF  # the clip's frames also show under the next clip's crossfade
            cues = []
            for sel, kind, phrase, off, opts in CUES[lab]:
                start = anchor_time(clip, phrase) + off - EARLY
                if start < XF:  # said as the clip fades in: start as the fade ends
                    print(f"{lab}: '{phrase}' falls in the crossfade; motion moved {XF - start:.2f} s later")
                    start = XF
                cues.append({"sel": sel, "kind": kind, "start": start, "dur": DUR[kind], "origin": opts.get("origin", "left")})
                print(f"{lab} {start:6.2f}s {kind:5s} {phrase}")

            html = Path(tmp) / "page.html"
            html.write_text(render.page((ROOT / "project" / "slides" / f"{sid}.html").read_text()))
            pg.goto(html.as_uri())
            pg.evaluate("document.fonts.ready")
            groups = render.REVEALS.get(sid, [])
            step = ord(lab[-1]) - ord("a") if lab[-1].isalpha() else 0
            for k, sels in enumerate(groups, 1):
                for sel in sels:
                    pg.eval_on_selector_all(sel, f"els => els.forEach(e => e.style.visibility = '{'visible' if k <= step else 'hidden'}')")

            # one screenshot per frame while something moves, one per still stretch
            n = int(round(total * FPS))
            moving = [any(c["start"] <= i / FPS < c["start"] + c["dur"] for c in cues) for i in range(n)]
            shots, i = [], 0
            while i < n:
                j = i + 1
                if not moving[i]:
                    while j < n and not moving[j]:
                        j += 1
                png = Path(tmp) / f"f{i:05d}.png"
                pg.evaluate(FRAME_JS, [cues, i / FPS, False])
                pg.screenshot(path=str(png))
                shots.append((png, (j - i) / FPS))
                i = j
            final = Path(tmp) / "final.png"
            pg.evaluate(FRAME_JS, [cues, total + 10, True])
            pg.screenshot(path=str(final))
            still = ROOT / "frames" / clip["frame"]
            q = psnr(final, still)
            assert q > 45, f"{lab}: the finished state differs from {still.name} (PSNR {q:.1f} dB)"

            lst = Path(tmp) / "list.txt"
            lst.write_text("".join(f"file '{f}'\nduration {d:.6f}\n" for f, d in shots) + f"file '{shots[-1][0]}'\n")
            out = ROOT / "anim" / f"{lab}.mp4"
            subprocess.run(
                ["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", f"fps={FPS},format=yuv420p", "-t", f"{total:.3f}"]
                + ["-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out)],
                check=True,
            )
            # check sheet: each cue halfway and done, in a 4-wide grid at quarter size
            times = sorted({round(c["start"] + c["dur"] * f, 3) for c in cues for f in (0.5, 1.0)})
            sel = "+".join(f"eq(n\\,{int(t * FPS)})" for t in times)
            rows = -(-len(times) // 4)
            subprocess.run(
                ["ffmpeg", "-loglevel", "error", "-y", "-i", str(out), "-vf", f"select='{sel}',scale=480:-1,tile=4x{rows}", "-frames:v", "1"]
                + ["-fps_mode", "vfr", str(ROOT / "out" / "anim_check" / f"{lab}.png")],
                check=True,
            )
            print(f"{lab}: {len(shots)} screenshots, {total:.2f} s, end state PSNR {q:.1f} dB")
        browser.close()


if __name__ == "__main__":
    main()
