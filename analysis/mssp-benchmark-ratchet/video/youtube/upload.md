# YouTube upload: "Resetting the Target Early"

What to enter in YouTube Studio for the study's video. The video file, the thumbnails and the caption file are on
Google Drive (`My_Drive/Data/stharrold.github.io/youtube/20261027-preregistered-mssp-early-renewal/`, with a README
giving their sha256); this sheet is the text. Built from draft v4 (2026-10-29), code at
[`26c7506`](https://github.com/stharrold/stharrold.github.io/tree/26c750669580104135ad3e25a63215affe076667/analysis/mssp-benchmark-ratchet/video).

Published 2026-10-29 as https://www.youtube.com/watch?v=WZQCHKAt2so (thumbnail A; Paid promotion: no; AI use: no,
since the four synthetic-media cases do not apply and the description discloses Claude's part; Shorts remixing not
allowed, so no clip can drop the post hoc label; educational type: real life application; subtitles auto-synced
from `captions.txt`; end screen: a "best for viewer" video and Subscribe in slide 26's empty right half). No cards,
quiz or background music.

## Details

- Title (84 characters): `Why did 29 Medicare doctor groups reset their targets early? A pre-registered study`
- Thumbnail: `thumbnail-a.png` (navy, "Why reset?", target -1.3%) or `thumbnail-b.png` (cream, "Lower target?!", 2 in 3).
  Custom thumbnails need a phone-verified channel.
- Audience: not made for kids.
- Altered or synthetic content: no. The voice is the author's own recording; the slides are graphics.
- Category: Education. Language and caption language: English.
- Tags: `medicare, accountable care organizations, ACO, shared savings program, pre-registration, causal inference,
  data science, health economics, healthcare`
- Captions: upload `captions.txt` as a transcript with "Auto-sync" (it is the script, word for word).
- Visibility: Private first; Public once the private copy has been watched on YouTube.
- End screen: slide 26 (16:44 to the end, 21 s) is laid out for it; a 20 s end screen from 16:45 fits.

## Description

Links carry `utm_source=youtube` so the site's analytics can attribute visits (CLAUDE.md, "Sharing a post
elsewhere"). YouTube refuses angle brackets in descriptions; there are none. The end slide (26) lists the
write-up, the registered plan and `github.com/stharrold/mssp-paper-2026` under "Links in the description", so all
three must stay here.

```text
In January 2022, 29 groups of doctors and hospitals in Medicare's Shared Savings Program quit their contracts early and signed new ones, which reset the targets Medicare uses to decide whether they earn a share of savings. Why would a group do that? This video walks through a study of that question, with the analysis plan registered publicly before any result was looked at.

Full write-up, with the methods, data and code:
https://stharrold.github.io/20261027-preregistered-mssp-early-renewal.html?utm_source=youtube&utm_medium=social&utm_campaign=20261027-preregistered-mssp-early-renewal

Registered analysis plan (OSF): https://osf.io/c53w9/
Code and paper: https://github.com/stharrold/mssp-paper-2026 (archived on Zenodo: https://doi.org/10.5281/zenodo.23737045)
Analysis pipeline, as registered: https://github.com/stharrold/stharrold.github.io/tree/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet

A note on the numbers: "two thirds ended up with a lower target" and the 1.3% average drop come from a check made after the registered analysis, against Medicare's published 2022 targets. That check was not in the plan, and the video labels it as an add-on.

AI disclosure: an AI tool, Claude Code from Anthropic, proposed this topic and drafted the analysis plan, the code and most of the written post, and separate AI instances reviewed them; the slides and script for this video were drafted with Claude's help too. I chose among its options, registered the plan, ran the analysis, and I'm responsible for the results.

Chapters
00:00 Why reset early?
01:20 How the Medicare deal works
04:50 The puzzle: quit early and sign again
06:55 Calling the shot
08:31 The findings
13:46 What it means
16:13 Takeaways
```

## Short

A 70-second vertical cut of the opening (`render/short.py`): the ratchet idea, then the cold open, ending on
"Here's what I found." and an end card pointing to the full video. File on Drive in `short/` next to the video.

- Title (61 characters): `Why would 29 doctor groups reset their Medicare targets early?`
- Related video: the full video, `WZQCHKAt2so` (a link under the Short).
- Audience, category, language, tags, remixing and comments: as for the full video. Captions are burned in.

```text
The opening of a pre-registered study of Medicare's Shared Savings Program: 29 groups of doctors and hospitals quit their contracts early to reset their targets, and most ended up with lower ones. Why?

Full 17-minute video: https://www.youtube.com/watch?v=WZQCHKAt2so
Write-up, with the methods, data and code: https://stharrold.github.io/20261027-preregistered-mssp-early-renewal.html?utm_source=youtube&utm_medium=social&utm_campaign=20261027-preregistered-mssp-early-renewal

"Two-thirds ended up with a lower target" comes from a check made after the registered analysis, against Medicare's published 2022 targets; it was not in the plan.

AI disclosure: the slides and script were drafted with help from Claude Code (Anthropic), which also proposed the topic and drafted the analysis plan and code; I registered the plan, ran the analysis, and I'm responsible for the results.
```
