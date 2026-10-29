# Video: "Resetting the Target Early"

The narrated video of the study for the blog's YouTube channel ([@DSDemos](https://www.youtube.com/@DSDemos)),
built from slides, a narration script and one voice recording per clip. It is reporting, not part of the registered
analysis. The same deck, as PowerPoint, is in the post (`content/static/20261027-preregistered-mssp-early-renewal/`,
rendered by `../report/video_slides.py`).

The deck and the scripts were first written in claude.ai and handed over as a reproducible-build document
(2026-10-29); from draft v3 on, the video is built from here.

| Path | Purpose |
|---|---|
| `project/deck.json`, `project/slides/*.html` | The deck in the claude.ai Slides format: 29 slides, 3 of them `hidden` (cut for length). |
| `render/script_video.py` | The narration, one entry per visible slide, one `(clip, text)` per recording. The source of truth for the words. |
| `render/inject_notes.py` | Copies the script into each slide's `<aside>` notes and writes `out/transcript-for-youtube.txt`. |
| `render/render.py` | Slides to 1920 x 1080 PNG frames with headless Chromium, one per clip, including reveal steps (`REVEALS`). |
| `render/thumbs.py` | Two 1280 x 720 thumbnails. |
| `render/vo_prepare.py` | Maps clips to recordings (`CLIP_TO_RECORDING`), decodes them, writes a QA report (loudness, pace, transcript diff). |
| `render/build_video.py` | Cleans and levels each clip, lengthens pauses (`PAUSES`), joins them with room tone, masters to -14 LUFS, crossfades the frames, writes chapters. |

Not in git (`.gitignore`): the recordings (`vo/`), the fonts (`fonts/`) and everything generated (`frames/`,
`thumbs/`, `out/`). The finished video goes to Google Drive and YouTube, not here.

## Build

Needs [uv](https://docs.astral.sh/uv/), ffmpeg (with `afftdn`, `deesser`, `acompressor`, `alimiter`, `ebur128`,
`xfade`) and npm. Playwright is pinned to 1.61.0 because its Chromium (revision 1228) was already cached; another
version needs `playwright install chromium`. Run from this folder:

```bash
PY() { uv run -q --no-project --python 3.12 --with playwright==1.61.0 --with numpy==2.5.4 --with soundfile==0.14.0 python -I "$@"; }

# 1. fonts (OFL, from npm): render.py and thumbs.py look under ./fonts
mkdir -p fonts && (cd fonts && npm pack -s @fontsource-variable/domine@5.3.0 @fontsource-variable/public-sans@5.3.0 &&
  for f in *.tgz; do mkdir -p "${f%.tgz}" && tar xzf "$f" -C "${f%.tgz}"; done)

# 2. recordings: link each recording session's folder as vo/youtube_voiceover*
mkdir -p vo && ln -sfn /path/to/youtube_voiceover vo/youtube_voiceover && ln -sfn /path/to/youtube_voiceover2 vo/youtube_voiceover2

# 3. notes, frames, thumbnails, voiceover QA
PY render/inject_notes.py project/slides     # 26 slides, 33 clips, 2031 words
PY render/render.py project/slides frames    # 33 PNGs
PY render/thumbs.py thumbs
PY render/vo_prepare.py .                    # vo/wav/, vo/map.json, vo/qa_report.txt

# 4. audio and video, about 13 minutes (--audio-only stops after out/voice.wav)
PY render/build_video.py .                   # out/draft.mp4, out/chapters.txt, out/timeline.json
```

The recorder numbers its files `261029_NNN.MP3` and keeps counting across sessions, so a number names one take
wherever it is. The QA report's transcript diff uses the recorder's own Whisper tiny.en output and mishears often
("stairs" for "stayers"); its clipping flag counts samples above 0.99, which also catches clean loud peaks (the
decoded MP3s reach about 1.42), so listen before re-recording.

## Changing the narration

1. Edit the text in `render/script_video.py` and rerun `inject_notes.py`, so the notes and the caption transcript
   match. If a slide's words change, edit its HTML too.
2. Record the clip, then point its label in `CLIP_TO_RECORDING` at the new number. The docstring in
   `vo_prepare.py` lists which takes are unused and why.
3. If a take is too fast in one place, lengthen a pause the speaker already left with `PAUSES` in
   `build_video.py`; it repeats that stretch of the take's own background (the build stops if it is not silent).
4. Rerun steps 3 and 4.

The published deck (`video-slides.pptx`) carries the same narration in its speaker notes; when the words change,
change them there too and rerun `../report/video_slides.py`, which rebuilds the transcript in the post.

## Changes since the claude.ai build

- Draft v3 (2026-10-29): six clips re-recorded (01, 03, 06, 12, 22, 26: takes 041-046). Clips 01 and 22 now say that
  "two thirds" and "their targets mostly went down" come from the check made after the study; the script follows
  the spoken wording in 03 ("sales targets"), 06 ("want to reset") and 22 ("fifty percent"). Slide 1 has the
  post hoc footnote that the published deck gained on 2026-10-29. Clip 26 gets 0.5 s more before "Thanks for
  watching."
