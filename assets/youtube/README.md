# YouTube channel assets

The blog's videos go on its own YouTube channel, named after the site: **Data Science Demos**,
[@DSDemos](https://www.youtube.com/@DSDemos) (created 2026-10-29, a Brand Account managed by the site's Google
account). One post, one video, and each video links back to its post.

Nothing here is published by Pelican (it is outside `content/`). Each video's own files (title, description,
chapters, captions) sit with that post's static files; the video files themselves are too large for git and are
kept on Google Drive, in `My_Drive/Data/stharrold.github.io/youtube/`.

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

## Uploaded to YouTube

| Date | What | File (sha256) |
|---|---|---|
| | | |

How these were chosen: `analysis/youtube-channel/BUILD-NOTES.md`.
