"""Word timestamps for the recordings, for timing animation to the narration.

Usage: python render/words.py <root> [LABEL ...]
Reads vo/map.json (from vo_prepare.py) and the recordings it names under vo/youtube_voiceover*/; writes
vo/words/261029_NNN.json: {"model": ..., "words": [{"w": word, "s": start, "e": end, "p": probability}]}, times in
seconds from the start of the recording. Takes already transcribed are skipped. With labels, only those clips.

faster-whisper large-v3-turbo on the CPU (int8), about 40 s per minute of audio; the model (1.6 GB) downloads to
~/.cache/huggingface on first use. The recorder's own *_results.json come from Whisper tiny with sentence-level
segments only, too coarse to start a motion on a word.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

MODEL = "large-v3-turbo"
ROOT = Path(sys.argv[1]).resolve()
OUT = ROOT / "vo" / "words"
OUT.mkdir(parents=True, exist_ok=True)
SESSIONS = sorted((ROOT / "vo").glob("youtube_voiceover*"))

mp = json.loads((ROOT / "vo" / "map.json").read_text())
labels = sys.argv[2:] or list(mp)
todo = [mp[lab] for lab in labels if not (OUT / f"261029_{mp[lab]}.json").exists()]
if todo:
    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
for num in todo:
    src = next(d / f"261029_{num}.MP3" for d in SESSIONS if (d / f"261029_{num}.MP3").exists())
    # decode with ffmpeg to 16 kHz mono and pass samples, which keeps PyAV (faster-whisper's own decoder) out of it
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, _ = model.transcribe(audio, language="en", word_timestamps=True, condition_on_previous_text=False, beam_size=5)
    words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)} for seg in segs for w in seg.words]
    (OUT / f"261029_{num}.json").write_text(json.dumps({"model": MODEL, "words": words}, indent=0) + "\n")
    print(f"261029_{num}: {len(words)} words")
