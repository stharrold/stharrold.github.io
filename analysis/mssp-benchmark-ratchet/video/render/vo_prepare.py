"""Decode the voiceover recordings, map them to script clips, and print a QA report.

Usage: python render/vo_prepare.py <root>
Expects:
  <root>/vo/youtube_voiceover/261029_NNN.MP3   recorder files (Zoom-style numbering)
  <root>/vo/youtube_voiceover/261029_NNN_results.json   optional Whisper results (start/end/text)
  render/script_video.py                        the narration script (SCRIPT)
Writes:
  <root>/vo/wav/261029_NNN.wav   44.1 kHz float WAV of every recording
  <root>/vo/map.json             clip label -> recorder number
  <root>/vo/qa_report.txt        loudness, clipping, pace and transcript-vs-script diff per clip

The mapping below was made by matching each recording's transcript to the script.
Recorder files not listed are deliberately unused:
  001  room tone (10 s, used for noise reduction and gap fill by build_video.py)
  002  quiet background sound, no speech
  017, 019, 037  extra takes of hidden slides (why-shot, questions, honesty)
  029, 033       numbers skipped by the recorder (deleted takes)
"""

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(sys.argv[1]).resolve()
SRC = ROOT / "vo" / "youtube_voiceover"
WAV = ROOT / "vo" / "wav"
WAV.mkdir(parents=True, exist_ok=True)
PREFIX = "261029_"

CLIP_TO_RECORDING = {
    "01": "003",
    "02": "004",
    "03": "005",
    "04": "006",
    "05": "007",
    "06": "008",
    "07": "009",
    "08a": "010",
    "08b": "011",
    "08c": "012",
    "09": "013",
    "10": "014",
    "11": "015",
    "12": "016",
    "13": "018",
    "14": "020",
    "15a": "021",
    "15b": "022",
    "16": "023",
    "17": "024",
    "18a": "025",
    "18b": "026",
    "18c": "027",
    "18d": "028",
    "19": "030",
    "20a": "031",
    "20b": "032",
    "21": "034",
    "22": "035",
    "23": "036",
    "24": "038",
    "25": "039",
    "26": "040",
}
ROOM_TONE = "001"

ns = {}
exec(Path(__file__).with_name("script_video.py").read_text(), ns)
TEXT = {lab: t for _, parts in ns["SCRIPT"] for lab, t in parts}
assert set(TEXT) == set(CLIP_TO_RECORDING), "script labels and mapping differ"


def decode(num):
    src = SRC / f"{PREFIX}{num}.MP3"
    dst = WAV / f"{PREFIX}{num}.wav"
    if not dst.exists():
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-c:a", "pcm_f32le", str(dst)], check=True)
    return dst


def lufs_tp(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    tail = r[r.rfind("Summary") :]
    i = float(tail.split("I:")[1].split("LUFS")[0])
    tp = float(tail.split("Peak:")[1].split("dBFS")[0])
    return i, tp


def analyze(path):
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    m = x.mean(1)
    hop = int(0.02 * sr)
    k = len(m) // hop
    e = 20 * np.log10(np.sqrt((m[: k * hop].reshape(k, hop) ** 2).mean(1)) + 1e-9)
    floor = float(np.percentile(e, 5))
    v = e > -42
    v[:15] = False
    v[-25:] = False
    runs, i = [], 0
    while i < k:
        if v[i]:
            j = i
            while j < k and v[j]:
                j += 1
            if j - i >= 5:
                runs.append((i, j))
            i = j
        else:
            i += 1
    start, end = (runs[0][0] * 0.02, runs[-1][1] * 0.02) if runs else (0.0, len(m) / sr)
    a = np.abs(x[:, 0])
    s = a > 0.99
    d = np.diff(np.r_[0, s.astype(int), 0])
    st, en = np.where(d == 1)[0], np.where(d == -1)[0]
    clip_times = sorted({round(float(t) / sr, 1) for t, n in zip(st, en - st, strict=True) if n >= 3 and start <= t / sr <= end})
    return dict(start=start, end=end, floor_db=floor, clip_events=clip_times)


NUM = set(
    (
        "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
        "sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred "
        "thousand million point half percent dollars first second third"
    ).split()
)


def toks(s):
    w = re.findall(r"[a-z']+|\d[\d,.]*", s.lower().replace("-", " "))
    return [x.strip("'") for x in w if not re.match(r"\d", x) and x not in NUM and x not in ("and", "a", "the", "s")]


lines = []
decode(ROOM_TONE)
for lab, num in CLIP_TO_RECORDING.items():
    wav = decode(num)
    i, tp = lufs_tp(wav)
    a = analyze(wav)
    words = len(TEXT[lab].split())
    wpm = words / max(a["end"] - a["start"], 0.1) * 60
    flags = []
    if wpm > 170:
        flags.append(f"FAST {wpm:.0f} wpm")
    if a["clip_events"]:
        flags.append(f"brief clipping at {a['clip_events'][:4]}s")
    lines.append(
        f"{lab:4s} <- {PREFIX}{num}  speech {a['start']:.1f}-{a['end']:.1f}s  {wpm:4.0f} wpm  "
        f"I={i:.1f} LUFS  TP={tp:+.1f} dBTP  floor={a['floor_db']:.0f} dB  {'; '.join(flags)}"
    )
    res = SRC / f"{PREFIX}{num}_results.json"
    if res.exists():
        heard = " ".join(seg["text"] for seg in json.loads(res.read_text())["transcript"])
        sm = difflib.SequenceMatcher(a=toks(TEXT[lab]), b=toks(heard), autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                lines.append(f"       {op}: script[{' '.join(sm.a[i1:i2])}] heard[{' '.join(sm.b[j1:j2])}]")

(ROOT / "vo" / "map.json").write_text(json.dumps(CLIP_TO_RECORDING, indent=1))
report = "\n".join(lines) + "\n"
(ROOT / "vo" / "qa_report.txt").write_text(report)
print(report)
print("Transcript diffs come from the recorder's Whisper tiny.en model; listen before re-recording.")
