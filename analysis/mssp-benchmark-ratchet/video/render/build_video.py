"""Assemble the narrated video from per-clip recordings and rendered slide frames.

Usage: python build_video.py <root> [--audio-only]
Inputs (under root):
  vo/map.json            clip label -> recorder number (e.g. "01": "003")
  vo/wav/261029_NNN.wav  decoded recordings
  vo/wav/261029_001.wav  room tone (used for gaps and the noise profile)
  frames/<label>-<slide>.png
Outputs: out/draft.mp4, out/chapters.txt, out/timeline.json
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

S = Path(sys.argv[1]).resolve()
OUT = S / "out"
OUT.mkdir(exist_ok=True)
SR = 48000
XF = 0.4  # crossfade between frames, seconds
LEAD = 0.30  # silence before speech in each clip
TAIL_STEP = 0.35  # silence after a reveal step (same slide continues)
TAIL_SLIDE = 0.70  # silence after the last clip of a slide
END_HOLD = 21.0  # minimum on-screen time for the end screen (YouTube end screens: last 5-20 s)
TARGET_CLIP_LUFS = -18.0
# Pauses lengthened inside a take: recording number -> [(seconds into the recording, seconds to add)]. The point
# must sit in a pause the speaker already left, at least half the added length from either edge (checked below);
# that stretch of the take's own background is repeated, so the pause keeps the take's noise floor (room tone
# here would be about 10 dB quieter than the processed take and sound like a dropout).
PAUSES = {
    # clip 26: "...in the comments." ends at 18.43 s and "Thanks for watching." starts at 18.99 s; the 0.55 s
    # pause becomes about 1.05 s, so the sign-off gets its own beat. The rest of the take runs at about 180 wpm.
    "046": [(18.71, 0.50)],
}

mp = json.loads((S / "vo/map.json").read_text())
labels = list(mp.keys())
frames = {p.name.split("-")[0]: p for p in (S / "frames").glob("*.png")}
assert all(lab in frames for lab in labels), [lab for lab in labels if lab not in frames]


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def load(path):
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    if sr != SR:
        tmp = OUT / "_rs.wav"
        run(["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", str(SR), str(tmp)])
        x, _ = sf.read(tmp, dtype="float32")
    return x


def speech_span(x):
    """First and last sustained voiced region (>= 0.1 s above -42 dBFS), ignoring clicks."""
    hop = int(0.02 * SR)
    k = len(x) // hop
    e = 20 * np.log10(np.sqrt((x[: k * hop].reshape(k, hop) ** 2).mean(1)) + 1e-9)
    v = e > -42
    v[:15] = False  # start-button bump
    v[-25:] = False  # stop-button click
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
    return runs[0][0] * hop, runs[-1][1] * hop


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    tail = r[r.rfind("Summary") :]
    return float(tail.split("I:")[1].split("LUFS")[0])


room = load(S / "vo/wav/261029_001.wav")[int(0.5 * SR) : int(10.5 * SR)]
room_path = OUT / "_room.wav"
sf.write(room_path, room, SR)

timeline, pieces = [], []
for n, lab in enumerate(labels):
    x = load(S / f"vo/wav/261029_{mp[lab]}.wav")
    a, b = speech_span(x)
    a = max(0, a - int(0.08 * SR))
    b = min(len(x), b + int(0.12 * SR))
    speech = x[a:b]
    raw = OUT / f"_raw_{lab}.wav"
    sf.write(raw, speech, SR)
    clean = OUT / f"_clean_{lab}.wav"
    # high-pass rumble, gentle spectral denoise at the measured -52 dB floor, de-ess lightly
    run(["ffmpeg", "-y", "-i", str(raw), "-af", "highpass=f=80,afftdn=nf=-50:nr=8:tn=1,deesser=i=0.3", str(clean)])
    gain = TARGET_CLIP_LUFS - lufs(clean)
    y, _ = sf.read(clean, dtype="float32")
    y = y * (10 ** (gain / 20))
    for t, add in sorted(PAUSES.get(mp[lab], []), reverse=True):
        i, half = int(t * SR) - a, int(add * SR / 2)
        quiet = 20 * np.log10(np.sqrt((x[a + i - half : a + i + half] ** 2).mean()) + 1e-9)
        assert quiet < -42, f"261029_{mp[lab]} is not silent around {t} s ({quiet:.0f} dBFS)"
        y = np.concatenate([y[:i], y[i - half : i + half], y[i:]])
    nxt = labels[n + 1] if n + 1 < len(labels) else None
    same_slide = nxt is not None and nxt[:2] == lab[:2]
    tail = TAIL_STEP if same_slide else TAIL_SLIDE
    lead = 0.15 if n == 0 else LEAD
    body = np.concatenate([np.zeros(int(lead * SR), np.float32), y, np.zeros(int(tail * SR), np.float32)])
    if nxt is None and len(body) < END_HOLD * SR:
        body = np.concatenate([body, np.zeros(int(END_HOLD * SR) - len(body), np.float32)])
    pieces.append(body)
    timeline.append(
        {
            "label": lab,
            "recording": f"261029_{mp[lab]}.MP3",
            "dur": len(body) / SR,
            "speech_s": round(len(y) / SR, 2),
            "gain_db": round(gain, 1),
            "frame": frames[lab].name,
        }
    )

audio = np.concatenate(pieces)
# fill digital silence with quiet room tone so gaps don't sound dead
reps = int(np.ceil(len(audio) / len(room)))
bed = np.tile(room, reps)[: len(audio)] * 0.5
silent = np.abs(audio) < 1e-7
audio = np.where(silent, bed, audio).astype(np.float32)
pre = OUT / "_voice.wav"
sf.write(pre, audio, SR)

# loudness to YouTube's -14 LUFS reference: static gain, then a 4x-oversampled peak limiter at -1.5 dBFS.
# (loudnorm in linear mode stops short of the target when the true-peak ceiling binds; this does not.)
# Speech peaks sit ~20 dB above its loudness, so a gentle 3:1 compressor first keeps the limiter from
# eating the gain; then gain + limit is repeated until within 0.3 LU of the target.
voice = OUT / "voice.wav"
comp = OUT / "_comp.wav"
run(["ffmpeg", "-y", "-i", str(pre), "-af", "acompressor=threshold=0.1:ratio=3:attack=5:release=120:knee=4:makeup=1", "-c:a", "pcm_f32le", str(comp)])
cur = comp
for k in range(3):
    gain = -14.0 - lufs(cur)
    nxt = OUT / f"_lim{k}.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(cur),
            "-af",
            f"volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.84:level=false:attack=1:release=60,aresample={SR}",
            "-c:a",
            "pcm_f32le",
            str(nxt),
        ]
    )
    cur = nxt
    if abs(lufs(cur) + 14.0) <= 0.3:
        break
cur.replace(voice)
print(f"final loudness {lufs(voice):.1f} LUFS")
if "--audio-only" in sys.argv:
    sys.exit(0)

# video: one still per clip, crossfaded at each clip boundary (offset = cumulative audio time)
durs = [t["dur"] for t in timeline]
inputs, filt = [], []
for i, t in enumerate(timeline):
    v = durs[i] + (XF if i < len(durs) - 1 else 0)
    inputs += ["-loop", "1", "-framerate", "30", "-t", f"{v:.3f}", "-i", str(S / "frames" / t["frame"])]
    filt.append(f"[{i}:v]format=yuv420p,setsar=1[v{i}]")
prev, acc = "v0", 0.0
for i in range(1, len(durs)):
    acc += durs[i - 1]
    out = f"x{i}"
    filt.append(f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={acc:.3f}[{out}]")
    prev = out
inputs += ["-i", str(voice)]
run(
    [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        ";".join(filt),
        "-map",
        f"[{prev}]",
        "-map",
        f"{len(durs)}:a",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-tune",
        "stillimage",
        "-crf",
        "20",
        "-r",
        "30",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        "-shortest",
        str(OUT / "draft.mp4"),
    ]
)

# chapters from the plan doc's breaks
CHAPTERS = [
    ("01", "Why reset early?"),
    ("04", "How the Medicare deal works"),
    ("09", "The puzzle: quit early and sign again"),
    ("12", "Calling the shot"),
    ("14", "The findings"),
    ("21", "What it means"),
    ("25", "Takeaways"),
]
start, t0 = {}, 0.0
for t in timeline:
    start[t["label"]] = t0
    t0 += t["dur"]
lines = [f"{int(start[lab] // 60):02d}:{int(start[lab] % 60):02d} {name}" for lab, name in CHAPTERS]
(OUT / "chapters.txt").write_text("\n".join(lines) + "\n")
(OUT / "timeline.json").write_text(json.dumps({"total_s": round(t0, 2), "clips": timeline}, indent=1))
for p in OUT.glob("_*.wav"):
    p.unlink()
print(f"total {t0 / 60:.2f} min")
print("\n".join(lines))
