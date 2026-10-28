# Post hoc analyses (not registered)

Analyses added after every registered result had been read, in response to critical assessments of the preprint
(stharrold/mssp-paper-2026). They reuse the registered pipeline's tables and estimators unchanged and change no
registered file (`DEVIATIONS.md` covers changes to registered files; these are new files), so they are reported as
exploratory and never decide a registered hypothesis.

| Script | Output | What it checks |
|---|---|---|
| `validation_change.py` | `validation_change.json` | The expected gain on the change scale for the 101 regular renewers; early renewers' realized 2022 reset from CMS's published benchmarks; the PY2021-PY2022 benchmark update, early renewers vs stayers |
| `pull_savings.py` | `pull_savings.json` | Rank correlations of the regional pull with the PY2020 and PY2021 savings rates and the own-spending component (does the pull restate past savings?), for the 267 early renewers and stayers in the group comparisons |

Run from the repository root: `uv run --group analysis python analysis/mssp-benchmark-ratchet/posthoc/<script>.py`.
