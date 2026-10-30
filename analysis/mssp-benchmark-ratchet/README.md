# MSSP early-renewal study (issue #73)

Pre-registered analysis of why Medicare Shared Savings Program ACOs renewed early into 2022 agreements. Write-up:
[the blog post](https://stharrold.github.io/20261027-preregistered-mssp-early-renewal.html). Registration:
[osf.io/c53w9](https://osf.io/c53w9/) (DOI 10.17605/OSF.IO/C53W9). Results notebook exports and the archived data
snapshot: the OSF project [osf.io/z4an5](https://osf.io/z4an5/) (DOI 10.17605/OSF.IO/Z4AN5). Code under the repository's MIT license; the CMS
files are public use files from data.cms.gov.

| File | Purpose |
|---|---|
| `PREREGISTRATION.md` | The plan. Frozen once registered on OSF; changes go in `DEVIATIONS.md`. |
| `DESIGN-NOTES.md` | How the question was chosen, including the designs dropped along the way. |
| `data-snapshot.tsv` | Every CMS file used: size, sha256, URL. |
| `fetch_snapshot.py` | Downloads the snapshot and checks every file's sha256 (standard library only). |
| `compare_results.py` | Compares a rerun's results files with the committed ones (standard library only). |
| `ratchet/` | Python: hash-checked loading, statistics (Bayesian bootstrap, PyMC, resampling, DiD), staged runner. |
| `dbt/` | dbt project (dbt-duckdb): one SQL model per derived table, with schema and data tests. |
| `tests/` | Tests on real enrollment data and on synthetic data (no CMS outcome values). |
| `results/` | One JSON file per stage, committed as each stage finished; each records the commit it ran at. |
| `posthoc/` | Post hoc checks added after every registered result had been read (not registered): scripts and their JSON output. See `posthoc/README.md`. |
| `report/` | Reporting only, not part of the registered analysis: `dashboard_data.py` builds the post's dashboard data from `results/`; `results_notebook.py` is the marimo results notebook; `exports/` holds its `.ipynb` and PDF exports, kept byte-for-byte as uploaded to OSF (sha256 in the post; never re-export). |
| `video/` | Reporting only: the narrated video for YouTube (slides, narration script, render and audio scripts). See `video/README.md`. |
| `REGISTRATION.md`, `DEVIATIONS.md`, `BUILD-NOTES.md` | The registration record, the deviation log, and a running log of how the study was built. |

## Reproduce and adapt

Tested from a fresh clone on macOS (Apple silicon), 2026-10-27, following exactly these steps (see step 4 for what
reproduced exactly). Linux should work the
same way (uv and every pinned package support it); Windows is untested. Commands run from the repository root.

### 1. Get the code

You need [git](https://git-scm.com/) and [uv](https://docs.astral.sh/uv/getting-started/installation/). uv installs
Python 3.12 and the exact package versions in `uv.lock` on first use. The repository also holds a website, so clone
only this study:

```bash
git clone --filter=blob:none --sparse https://github.com/stharrold/stharrold.github.io.git
cd stharrold.github.io
git sparse-checkout set analysis/mssp-benchmark-ratchet
```

The code exactly as registered is commit `a4064f5` (also the zip attached to the OSF registration; `REGISTRATION.md`
has its sha256). `fetch_snapshot.py` and `compare_results.py` were added after registration and change nothing in the
analysis, so use them from the main branch.

### 2. Get the data (about 40 MB, under a minute)

```bash
uv run python analysis/mssp-benchmark-ratchet/fetch_snapshot.py
```

It downloads the 40 CMS files listed in `data-snapshot.tsv` into `~/.cache/stharrold-github-io/mssp-snapshot-2026-10-22/`,
where the pipeline looks for them, and keeps each one only if its sha256 matches. Rerunning it skips files already in
place. CMS sometimes replaces a file in place; any file that no longer matches is taken from the archived copy of the
snapshot on OSF ([`mssp-snapshot-2026-10-22.zip`](https://osf.io/53aqd/), 9.6 MB, sha256
`16f5461579e849aa816291ffc7aa7c73c05fa8e7d11b73a6e3cf4200afa656ea`; `--archive-only` takes everything from it). To put the data elsewhere, pass `--data-dir DIR` here and the same `--data-dir DIR` to
`run.py`.

### 3. Check the installation (about 8 minutes)

```bash
uv run --group analysis pytest analysis/mssp-benchmark-ratchet/tests
```

The `analysis` dependency group (PyMC, dbt-duckdb, statsmodels and the rest) is installed on first use.

### 4. Rerun the analysis

Each stage refuses to start until the files it needs exist in its output directory, in the order the plan fixes.
Times are for 5 worker processes on an Apple M-series Mac.

| Stage | Needs | Writes | Plan section | Time |
|---|---|---|---|---|
| `validate` | the data | `validation.json` | 4.4 | seconds |
| `power` | validation | `power.json` | 6 | about 40 minutes |
| `confirm` | validation, power | `confirm.json` | 5.1-5.4 | about 17 hours |
| `robustness` | validation, power | `robustness.json` | 5.5 | minutes |
| `did` | validation, power, confirm | `did.json` | 5.8 | under a minute |
| `conventional` | validation, power, confirm, did | `conventional.json` | 5.7 | seconds |
| `exploratory` | validation, power, confirm | `exploratory.json` | 5.6 | about 2 minutes |

```bash
OUT=~/mssp-rerun   # keeps the committed results/ untouched; without --out-dir, stages write into results/
for stage in validate power confirm robustness did conventional exploratory; do
  uv run --group analysis python analysis/mssp-benchmark-ratchet/ratchet/run.py $stage --out-dir $OUT || break
done
uv run python analysis/mssp-benchmark-ratchet/compare_results.py $OUT
```

`compare_results.py` checks every number in each rerun file against the committed one and prints `same` or the values
that differ. Expect differences in the simulated numbers. The analysis table is read without a fixed row order
(`select * from analysis` in `ratchet/run.py`), so the seeded random draws fall on the ACOs in a different order
in each run, and every bootstrap interval, permutation p-value, power simulation and MCMC fit varies slightly. In
the fresh-clone test, `validate` reproduced exactly; `power` reproduced every deterministic number (standard
deviations, minimum detectable effects), while its simulated power and detection shares moved by about the
simulation error (for example H1's simulated power 0.776 against 0.804). Deterministic quantities, such as
differences in means and the validation metrics, should match exactly, and no verdict is close enough to its
threshold to change. For bit-for-bit reruns in your own variant, sort the frame (for example `order by aco_id` in
`_frames`); that changes the draws, so it will not reproduce the committed numbers either.

- `--workers N` sets the number of processes (default: half the cores). The confirm stage is about 40,000 MCMC
  refits; with fewer workers it takes proportionally longer.
- To rerun only a later stage without the 17-hour confirm stage, copy the committed files it needs into your output
  directory first, for example `cp analysis/mssp-benchmark-ratchet/results/{validation,power,confirm}.json $OUT/`
  before `did`. Stages check only that those files exist.

### 4b. Rerun the post hoc checks (under a minute; not registered)

The manuscript also reports 2 post hoc checks (eTable 13 of its Multimedia Appendix 1). They rebuild the database
with the registered pipeline and need the data from step 2 in its default location (they take no `--data-dir`):

```bash
uv run --group analysis python analysis/mssp-benchmark-ratchet/posthoc/validation_change.py
uv run --group analysis python analysis/mssp-benchmark-ratchet/posthoc/pull_savings.py
git diff --stat -- analysis/mssp-benchmark-ratchet/posthoc/
```

Each overwrites its committed JSON in `posthoc/`, so `git diff` shows what changed. Tested 2026-10-28: besides the
`generated` timestamp and `git_commit`, `pull_savings.json` matched to 6 decimals, and in `validation_change.json`
every validation metric matched while the resampled PY2021-to-PY2022 comparison moved by simulation error (interval
-1.97 to 2.24 committed, -2.04 to 2.23 rerun; -2.0 to 2.2 as reported either way). `git checkout -- analysis/mssp-benchmark-ratchet/posthoc/`
restores the committed files.

### 5. Adapt it

| To change | Edit |
|---|---|
| Who is in each group | `dbt/models/enrollment/` (`base.sql`, `groups.sql`) |
| A constructed variable (expected gain, regional pull, spending panel) | `dbt/models/full/` (for example `expected_gain.sql`, `region_std.sql`), with tests in `dbt/models/schema.yml` and `dbt/tests/` |
| Which CMS files are read | `data-snapshot.tsv` (add a row: file, url, bytes, sha256) and `ratchet/config.py` (file names), loaded in `ratchet/build.py` |
| Group comparisons, permutation tests | `ratchet/resample.py` |
| The H3 decision model and its tests | `ratchet/decision.py` |
| The H4 difference-in-differences | `ratchet/did.py` |
| Robustness, conventional and exploratory analyses | `ratchet/robustness.py`, `ratchet/conventional.py`, `ratchet/exploratory.py` |
| Resample counts, sampler settings, seed | `ratchet/config.py` (`N_RESAMPLES`, `SEED`), `ratchet/decision.py` (`FULL`, `RETRY`, `REDUCED`) |
| Stages and their order | `ratchet/run.py` (`STAGES`, `REQUIRES`) |

**Look up one ACO's reset components.** The pipeline builds its tables in a DuckDB database, which you can query
directly. This builds it from the snapshot (about 15 seconds) and prints, for each ACO in the two cohorts and the
validation sample, its PY2021 benchmark, the rebuilt benchmark a 2022 reset would have given it, and the expected
gain with its own-spending and regional parts and the regional pull (all in percent of the PY2021 benchmark). These
follow the rules for agreements that began in 2022 (42 CFR 425.601), not the rules for 2024 and later.

```bash
uv run --group analysis python - <<'EOF'
import sys; sys.path.insert(0, "analysis/mssp-benchmark-ratchet")
from ratchet import build
con = build.connect(stage="full")
print(con.sql("""
    select aco_id, round(current_bnchmk) as current_bnchmk, round(new_bnchmk) as new_bnchmk,
           round(gain, 1) as gain, round(own, 1) as own, round(regional_comp, 1) as regional_comp, round(pull, 1) as pull
    from expected_gain order by aco_id
""").df().to_string(index=False))
EOF
```

Add `where aco_id = 'A1001'` for one ACO. Other tables (`show tables` lists them) hold every intermediate step; the
dbt models in `dbt/models/` document what each one contains.

**Try a change on synthetic data first.** `ratchet/synthetic.py` writes a made-up snapshot with the real file and
column names, and computes the constructed variables independently in NumPy; the tests require the dbt SQL to match
it. So when you change a constructed variable, change it in both places. A full dry run with small settings takes a
few minutes (`--quick` is refused for real data):

```bash
uv run --group analysis python -c "import sys; sys.path.insert(0, 'analysis/mssp-benchmark-ratchet'); \
  from pathlib import Path; from ratchet import synthetic; synthetic.generate(Path('/tmp/ratchet-syn'), seed=7)"
for stage in validate power confirm robustness did conventional exploratory; do
  uv run --group analysis python analysis/mssp-benchmark-ratchet/ratchet/run.py $stage \
    --data-dir /tmp/ratchet-syn --out-dir /tmp/ratchet-syn-out --quick
done
```

**Pre-registering your own version.** Every file is hashed before it is read, and a file that matches an outcome entry
in `data-snapshot.tsv` (a performance-year results, county-spending or county-assignment file; `OUTCOME_PREFIXES` in
`ratchet/config.py`) cannot be opened until `REGISTRATION.md` exists (`ratchet/snapshot.py`). Here it exists, so
everything is open. To make your own variant confirmatory rather than exploratory:

1. In your copy, delete `REGISTRATION.md`. The lock closes: the outcome files can no longer be read, and there is no
   flag to bypass it.
2. Write your plan, and develop and test the code on synthetic data and the enrollment files only.
3. Register the plan with an independent registry such as [OSF Registries](https://osf.io/registries), which records
   the time itself (git commit dates can be set by hand).
4. Commit a new `REGISTRATION.md` recording the registration, the plan's sha256 and the code commit, then run the
   stages. Log any later change to the plan or code in a deviation log before using its results.

Without step 1, results from your changes are exploratory, and should be reported that way.

## Status

Registered on OSF on 2026-10-26 ([osf.io/c53w9](https://osf.io/c53w9/), code at `a4064f5`). Every stage has run with
the registered code; the one logged deviation is a `uv.lock` security update made after the last stage. The results
notebook runs outside the lockfile with pinned tools:

```bash
uv run --with marimo==0.25.2 --with matplotlib==3.11.2 --with nbformat==5.11.1 \
    --with 'nbconvert[webpdf]==7.17.2' --with playwright==1.61.0 \
    marimo export html analysis/mssp-benchmark-ratchet/report/results_notebook.py -o results.html
```
