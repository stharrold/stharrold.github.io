"""A vertical Short (1080 x 1920, about 70 s) from the video's opening: the ratchet idea, then the cold open.

Usage: python render/short.py <root> audio|words|stills|render
  audio   out/short/voice.wav: clip 03 from "Imagine" on, then clip 01, then 3 s of room tone for the end card,
          sliced from out/voice.wav (build_video.py; already cleaned, patched and mastered) and leveled to -14 LUFS
  words   out/short/words.json: word times in the Short's own audio (faster-whisper large-v3-turbo; run with
          --with 'faster-whisper>=1.1' instead of playwright)
  stills  out/short/check/*.png: each scene's finished state and a caption, to check the layout before rendering
  render  out/short/short.mp4 (H.264 and AAC, 30 fps)

Clip 03 comes first because "Imagine your boss sets next year's sales targets from what you sold this year" is a
stronger first line than the cold open's date; its "First, a familiar idea." is dropped. Clip 01 ends on "Here's
what I found.", and the end card points to the full video. The slides are the deck's two opening slides laid out
for a tall screen, in its colours and fonts; lines build in as the narration reaches them (0.15 s before the word
is heard, as in animate.py). Captions are the transcribed words, a few at a time, with numbers as digits. Text
stays out of the Shorts overlays: the top 220 px, the bottom 480 px and the right 140 px.
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

ROOT = Path(sys.argv[1]).resolve()
STAGE = sys.argv[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "out" / "short"
OUT.mkdir(parents=True, exist_ok=True)
SR = 48000
FPS = 30
W, H = 1080, 1920
EARLY = 0.15  # a line builds in this long before its word is heard
BUILD = 0.6  # seconds a build-in takes
DIP = 0.35  # seconds to fade into navy, and out of it, between the scenes
END_CARD = 3.0  # seconds of end card after the last word
QUIET = -38  # dBFS: below this is the room-tone bed (about -43 after mastering), not speech (about -20)


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(r[r.rfind("Summary") :].split("I:")[1].split("LUFS")[0])


def db(x):
    return 20 * np.log10(np.sqrt((x**2).mean()) + 1e-9)


def audio():
    voice, sr = sf.read(ROOT / "out" / "voice.wav", dtype="float32")
    assert sr == SR
    voice = voice if voice.ndim == 1 else voice.mean(1)
    tl = json.loads((ROOT / "out" / "timeline.json").read_text())["clips"]
    start, t0 = {}, 0.0
    for c in tl:
        start[c["label"]] = (t0, c)
        t0 += c["dur"]
    # clip 03: start in the pause between "idea." and "Imagine" (recording 8.74-9.28 s), at its quietest 10 ms
    s3, c3 = start["03"]
    words = json.loads((ROOT / "vo" / "words" / "261029_042.json").read_text())["words"]
    idea, imagine = next(w for w in words if w["w"] == "idea."), next(w for w in words if w["w"] == "Imagine")
    to_clip = lambda t: c3["lead_s"] + t - c3["trim_start_s"]  # noqa: E731 (no pauses or cuts in take 042)
    a, b = int((s3 + to_clip(idea["e"])) * SR), int((s3 + to_clip(imagine["s"])) * SR)
    h = SR // 100
    frames = voice[a:b][: (b - a) // h * h].reshape(-1, h)
    k = int(np.argmin((frames**2).mean(1)))
    cut = a + k * h
    assert db(voice[cut : cut + h]) < QUIET, f"clip 03 is not silent at the cut ({db(voice[cut : cut + h]):.0f} dBFS)"
    assert db(voice[-int(0.15 * SR) :]) < QUIET, "the end of voice.wav should be room tone"
    part3 = np.concatenate([voice[-int(0.15 * SR) :], voice[cut : int((s3 + c3["dur"]) * SR)]])  # 0.15 s of room tone first
    s1, c1 = start["01"]
    part1 = voice[int(s1 * SR) : int((s1 + c1["dur"]) * SR)]
    tail = voice[-int(END_CARD * SR) :]
    assert db(tail) < QUIET, "the end of voice.wav should be room tone"
    fade = int(0.015 * SR)
    ramp = np.linspace(0, 1, fade, dtype=np.float32)
    pieces = []
    for p in (part3, part1, tail):
        p = p.copy()
        p[:fade] *= ramp
        p[-fade:] *= ramp[::-1]
        pieces.append(p)
    raw = OUT / "_raw.wav"
    sf.write(raw, np.concatenate(pieces), SR)
    gain = -14.0 - lufs(raw)
    out = OUT / "voice.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(raw),
            "-af",
            f"volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.84:level=false:attack=1:release=60,aresample={SR}",
            "-c:a",
            "pcm_f32le",
            str(out),
        ]
    )
    raw.unlink()
    scenes = {"a_end": len(pieces[0]) / SR, "b_end": (len(pieces[0]) + len(pieces[1])) / SR, "total": sum(map(len, pieces)) / SR}
    (OUT / "scenes.json").write_text(json.dumps(scenes, indent=1) + "\n")
    print(f"{scenes['total']:.1f} s, {lufs(out):.1f} LUFS; scene change at {scenes['a_end']:.2f} s, end card at {scenes['b_end']:.2f} s")


def words():
    from faster_whisper import WhisperModel

    cmd = ["ffmpeg", "-loglevel", "error", "-i", str(OUT / "voice.wav"), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]
    pcm = subprocess.run(cmd, capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, _ = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8").transcribe(
        x, language="en", word_timestamps=True, condition_on_previous_text=False, beam_size=5
    )
    ws = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for seg in segs for w in seg.words]
    (OUT / "words.json").write_text(json.dumps({"model": "large-v3-turbo", "words": ws}, indent=0) + "\n")
    print(" ".join(w["w"] for w in ws))


# --- timing: word onsets, cues and caption chunks ---------------------------------------------------------------


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


# Whisper's mishearings in this audio, fixed word for word (same count, times kept); checked against the script.
FIXES = [
    (["So", "I", "do", "it."], ["So", "why", "do", "it?"]),
    (["numbers"], ["numbers,"]),
    (["target,", "a", "more"], ["target.", "A", "more"]),
]


def load_words():
    ws = json.loads((OUT / "words.json").read_text())["words"]
    for w, nxt in zip(ws, ws[1:], strict=False):  # "two" "-thirds" -> "two-thirds"
        if nxt["w"].startswith("-"):
            w["w"], w["e"], nxt["w"] = w["w"] + nxt["w"], nxt["e"], ""
    ws = [w for w in ws if w["w"]]
    for old, new in FIXES:
        hits = [i for i in range(len(ws)) if [w["w"] for w in ws[i : i + len(old)]] == old]
        assert len(hits) == 1, f"{old}: {len(hits)} matches"
        for w, text in zip(ws[hits[0] :], new, strict=False):
            w["w"] = text
    x, _ = sf.read(OUT / "voice.wav", dtype="float32")
    h = SR // 100
    for w in ws:
        a, b = int(w["s"] * SR), int(max(w["e"], w["s"] + 0.02) * SR)
        seg = x[a:b][: (b - a) // h * h].reshape(-1, h) if b - a >= h else x[a : a + h].reshape(1, -1)
        loud = np.flatnonzero(20 * np.log10(np.sqrt((seg**2).mean(1)) + 1e-9) > -40)
        w["on"] = w["s"] + (loud[0] * 0.01 if len(loud) else 0.0)
    return ws


def find(ws, phrase, after=0.0):
    """Onset of the first word of `phrase` (spoken words, lowercased) at or after `after` seconds."""
    want = phrase.split()
    toks = [norm(w["w"]) for w in ws]
    for i in range(len(ws) - len(want) + 1):
        if ws[i]["s"] >= after and toks[i : i + len(want)] == want:
            return ws[i]["on"]
    raise SystemExit(f"cue phrase not heard: {phrase!r}")


def chunks(ws, end):
    """Caption chunks: up to 3 words or 18 characters, broken after punctuation; each shown from its first word's
    onset until the next chunk, or 0.4 s after its last word when a pause follows."""
    out, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        text = " ".join(c["w"] for c in cur)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        if nxt is None or re.search(r"[.,?!:;]$", w["w"]) or len(cur) == 3 or len(text) + 1 + len(nxt["w"]) > 18 or nxt["s"] - w["e"] > 0.5:
            out.append({"text": text, "t0": cur[0]["on"] - 0.05, "last_e": cur[-1]["e"]})
            cur = []
    merged = []  # a lone last word ("it?", "found.") joins the chunk before it when they fit on one line
    for c in out:
        prev = merged[-1] if merged else None
        if prev and " " not in c["text"] and not re.search(r"[.,?!:;]$", prev["text"]) and len(prev["text"]) + 1 + len(c["text"]) <= 22:
            prev["text"], prev["last_e"] = prev["text"] + " " + c["text"], c["last_e"]
        else:
            merged.append(c)
    out = merged
    for k, c in enumerate(out):
        nxt_t0 = out[k + 1]["t0"] if k + 1 < len(out) else end
        c["t1"] = min(nxt_t0, c["last_e"] + 0.4) if nxt_t0 - c["last_e"] > 0.6 else nxt_t0
    return out


# --- the page: two scenes and an end card, driven by setT(t) -----------------------------------------------------

NAVY, CREAM, ORANGE, RUST, INK, SLATE = "#1B2A3A", "#F7F4EE", "#F0A06A", "#B4501A", "#3E4C5A", "#C9D3DC"

BODY = f"""
<div id="a" class="scene" style="background:{CREAM}">
  <p class="kicker" style="color:{RUST}">Start with a familiar idea</p>
  <h2 style="color:{NAVY}">Imagine next year's sales target is set from what you sold this year.</h2>
  <p class="line" id="a2" style="color:{INK}">Have a great year, and next year's target gets harder.</p>
  <p class="line" id="a3" style="color:{INK}">Economists call this a <b>ratchet</b>: it only clicks one way.</p>
  <p class="line big" id="a4" style="color:{RUST}">Medicare has its own version.</p>
</div>
<div id="b" class="scene" style="background:{NAVY}">
  <p class="kicker" style="color:{ORANGE}">Medicare, January 2022</p>
  <h2 style="color:{CREAM}">29 doctor groups quit their contracts early and had their targets reset.</h2>
  <div id="b2"><h2 style="color:{ORANGE}">Two-thirds ended up with a lower one.</h2>
    <p class="note" style="color:{SLATE}">Two-thirds: from a check made after the study, against Medicare's published 2022 targets.</p></div>
  <p class="why" id="b3" style="color:{CREAM}">Why?</p>
</div>
<div id="c" class="scene end" style="background:{NAVY}">
  <p class="kicker" style="color:{ORANGE}">The full study, in 17 minutes</p>
  <h2 style="color:{CREAM}">Resetting the Target Early</h2>
  <p class="line" style="color:{SLATE}">Data Science Demos on YouTube<br>@DSDemos</p>
</div>
<div id="cap"><span></span></div>
"""

CSS = f"""
*{{margin:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{NAVY};font-family:'Public Sans',Arial,sans-serif}}
.scene{{position:absolute;inset:0;padding:260px 140px 0 88px;display:flex;flex-direction:column;gap:44px}}
.end{{justify-content:center;padding-bottom:300px}}
.kicker{{font-size:30px;font-weight:600;letter-spacing:3px;text-transform:uppercase}}
h2{{font-family:'Domine',Georgia,serif;font-size:76px;font-weight:700;line-height:1.16}}
.line{{font-size:46px;line-height:1.32}}
.big{{font-family:'Domine',Georgia,serif;font-size:60px;font-weight:700}}
.note{{font-size:32px;line-height:1.35;margin-top:18px}}
#b h2{{font-size:70px}}
.why{{font-family:'Domine',Georgia,serif;font-size:140px;font-weight:700;line-height:1}}
#cap{{position:absolute;left:88px;right:140px;top:1370px;display:flex;justify-content:center}}
#cap span{{font-weight:800;font-size:64px;line-height:1.15;color:#fff;background:rgba(27,42,58,0.92);border-radius:18px;padding:12px 28px;text-align:center}}
#cap span:empty{{display:none}}
"""

JS = """
const ease = p => p <= 0 ? 0 : p >= 1 ? 1 : 1 - Math.pow(1 - p, 3);
window.setT = (t, S) => {
  const op = (id, v) => { document.getElementById(id).style.opacity = v; };
  // scenes: a until the dip, navy, then b; the end card fades in over b
  const a = 1 - ease((t - (S.a_end - DIP_S)) / DIP_S);
  const b = ease((t - S.a_end) / DIP_S);
  op('a', a); op('b', b);
  op('c', ease((t - S.b_end + 0.6) / 0.5));
  for (const [id, t0] of Object.entries(S.cues)) {
    const p = ease((t - t0) / BUILD_S);
    const el = document.getElementById(id);
    el.style.opacity = p; el.style.transform = `translateY(${(1 - p) * 28}px)`;
  }
  const c = S.caps.find(c => t >= c.t0 && t < c.t1);
  document.querySelector('#cap span').textContent = c ? c.text : '';
  return [a.toFixed(3), b.toFixed(3), document.getElementById('c').style.opacity,
          ...Object.keys(S.cues).map(id => document.getElementById(id).style.opacity),
          c ? c.text : ''].join('|');
};
""".replace("DIP_S", str(DIP)).replace("BUILD_S", str(BUILD))


def timing():
    sc = json.loads((OUT / "scenes.json").read_text())
    ws = load_words()
    a_end = sc["a_end"]
    cues = {
        "a2": find(ws, "you crush it") - EARLY,
        "a3": find(ws, "economists") - EARLY,
        "a4": find(ws, "medicare has") - EARLY,
        "b2": find(ws, "by medicare's", a_end) - EARLY,
        "b3": find(ws, "so why", a_end) - EARLY,
    }
    caps = chunks(ws, sc["b_end"])
    return {**sc, "cues": {k: float(v) for k, v in cues.items()}, "caps": caps}


def page_html():
    spec = importlib.util.spec_from_file_location("render", HERE / "render.py")
    render = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(render)
    faces = (
        f"@font-face{{font-family:'Domine';src:url('{render.DOMINE.as_uri()}');font-weight:400 700}}"
        f"@font-face{{font-family:'Public Sans';src:url('{render.PUBSANS.as_uri()}');font-weight:100 900}}"
    )
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{faces}{CSS}</style></head><body>{BODY}<script>{JS}</script></body></html>"


def with_page(fn):
    from playwright.sync_api import sync_playwright

    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        html = Path(tmp) / "short.html"
        html.write_text(page_html())
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        page.goto(html.as_uri())
        page.evaluate("document.fonts.ready")
        fn(page)
        browser.close()


def stills():
    sched = timing()
    check = OUT / "check"
    check.mkdir(exist_ok=True)
    # each scene finished, with a caption showing, plus the end card
    moments = {
        "a": sched["a_end"] - DIP - 0.8,
        "b": sched["b_end"] - 0.9,
        "end": sched["total"] - 0.1,
    }

    def shoot(page):
        for name, t in moments.items():
            state = page.evaluate("([t, sched]) => setT(t, sched)", [t, sched])
            page.screenshot(path=str(check / f"{name}.png"))
            print(name, f"{t:.2f}s", state.split("|")[-1])

    with_page(shoot)
    print("cues:", {k: round(v, 2) for k, v in sched["cues"].items()})
    print("captions:", " / ".join(c["text"] for c in sched["caps"]))


def render_video():
    sched = timing()
    n = int(np.ceil(sched["total"] * FPS))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        listing, last_state, last_png, shots = [], None, None, 0

        def shoot(page):
            nonlocal last_state, last_png, shots
            for i in range(n):
                state = page.evaluate("([t, sched]) => setT(t, sched)", [i / FPS, sched])
                if state != last_state:
                    last_png = tmp / f"f{i:05d}.png"
                    page.screenshot(path=str(last_png))
                    last_state, shots = state, shots + 1
                listing.append(f"file '{last_png}'\nduration {1 / FPS:.6f}")

        with_page(shoot)
        listing.append(f"file '{last_png}'")
        (tmp / "frames.txt").write_text("\n".join(listing) + "\n")
        out = OUT / "short.mp4"
        run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "frames.txt"), "-i", str(OUT / "voice.wav"),
                "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-r", str(FPS),
                "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-shortest", "-movflags", "+faststart", str(out),
            ]
        )  # fmt: skip
    print(f"{out}: {n} frames, {shots} screenshots, {sched['total']:.1f} s")


{"audio": audio, "words": words, "stills": stills, "render": render_video}[STAGE]()
