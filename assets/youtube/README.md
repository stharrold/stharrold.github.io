# YouTube channel assets

The blog's videos go on its own YouTube channel, named after the site: **Data Science Demos**,
[@DSDemos](https://www.youtube.com/@DSDemos) (created 2026-10-29, a Brand Account managed by the site's Google
account). One post, one video, and each video links back to its post.

Nothing here is published by Pelican (it is outside `content/`). Each video's title, description and settings sit
with the code that built it (for #73: `analysis/mssp-benchmark-ratchet/video/youtube/upload.md`); the video files,
thumbnails and captions are too large or too generated for git and are kept on Google Drive, in
`My_Drive/Data/stharrold.github.io/youtube/<post slug>/`, with a README giving each file's sha256. That folder sits
inside the analytics archive, whose generated README does not list it; the archive job never touches it.

## Files

| File | What | Made by |
|---|---|---|
| `avatar.png` | Channel picture, 800 x 800: the site's "DS" monogram, white Lato on navy `#2c3e50` (as `content/extra/apple-touch-icon.png`) | `uv run --no-sync python scripts/youtube_art.py` |
| `banner.png` | Channel banner, 2560 x 1440: "Data Science Demos", a teal rule, "stharrold.github.io", all inside the 1546 x 423 centre that every device shows | `uv run --no-sync python scripts/youtube_art.py` |

## Channel profile

- Description: "Data Science Demos is the video companion to stharrold.github.io, the blog of Samuel Harrold, a data
  scientist in healthcare. Each video walks through one post: the question, how it was tested, and what the data
  showed. The code and data are public, so you can rerun the analyses yourself."
- Links: Blog `https://stharrold.github.io/` (untagged: the About panel shows the address), GitHub
  `https://github.com/stharrold`, LinkedIn `https://www.linkedin.com/in/samuelharrold`. Links in video descriptions
  carry `?utm_source=youtube&utm_medium=social&utm_campaign=<post slug>` (CLAUDE.md, "Sharing a post elsewhere") so `/analytics` can attribute them.
- Contact email: a `+dsdemos` alias of the site's Google account, so mail from the listing can be filtered.
- Video watermark: `avatar.png`, shown for the entire video (on desktop it doubles as a Subscribe button).

## Uploaded to YouTube

| Date | What | File (sha256) |
|---|---|---|
| 2026-10-29 | Channel picture | `avatar.png` (`a8d355a548a6e18241ddf7be450c4bfd24750d9adcb3ca991847b189c3b255d0`) |
| 2026-10-29 | Banner | `banner.png` (`a290da832442612adf0debea10caa265f0039875f4008d50e0da971f2ca03920`) |
| 2026-10-29 | Video watermark, entire video | `avatar.png` (`a8d355a548a6e18241ddf7be450c4bfd24750d9adcb3ca991847b189c3b255d0`) |
| 2026-10-29 | Description, links and contact email as in "Channel profile" above | |
| 2026-10-29 | Video [`WZQCHKAt2so`](https://www.youtube.com/watch?v=WZQCHKAt2so), "Why did 29 Medicare doctor groups reset their targets early? A pre-registered study" (#73), public; text and settings in `analysis/mssp-benchmark-ratchet/video/youtube/upload.md`, subtitles from `captions.txt`, end screen 16:44-17:04 | `resetting-the-target-early.mp4` (`c408f725a0bdf6744920ab3cee9afd2801ece42a6f0288ae21281b6e8378f5d3`), thumbnail `thumbnail-a.png` (`d05ce3512bb435f976440223794faa7c8e8ed49a9aa048218fbd65e88e202406`) |
| 2026-10-29 | Short [`LuxBRi1q0Eg`](https://www.youtube.com/shorts/LuxBRi1q0Eg), "Why would 29 doctor groups reset their Medicare targets early?" (#73), public; 70 s vertical cut of the opening (`analysis/mssp-benchmark-ratchet/video/render/short.py`), related video `WZQCHKAt2so`, captions burned in and as `captions.srt`, Shorts remixing audio only; text in `video/youtube/upload.md` ("Short") | `resetting-the-target-early-short.mp4` (`149e81ea075690b361413c01e38f0b20de1cf42bfaf16b5c6cd8f833355663e4`) |

How these were chosen: `analysis/youtube-channel/BUILD-NOTES.md`.
