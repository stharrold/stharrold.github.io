# MSSP early-renewal study (issue #73)

Pre-registered analysis of why Medicare Shared Savings Program ACOs renewed early into 2022 agreements.

| File | Purpose |
|---|---|
| `PREREGISTRATION.md` | The plan. Frozen once registered on OSF; changes go in `DEVIATIONS.md`. |
| `DESIGN-NOTES.md` | How the question was chosen, including the designs dropped along the way. |
| `data-snapshot.tsv` | Every CMS file used: size, sha256, URL. |
| `ratchet/` | Python: hash-checked loading, statistics (Bayesian bootstrap, PyMC, resampling, DiD), staged runner. |
| `dbt/` | dbt project (dbt-duckdb): one SQL model per derived table, with schema and data tests; `dbt docs` gives the lineage. |
| `tests/` | Tests on real enrollment data and on synthetic data (no CMS outcome values). |

## Running

From the repository root (the `analysis` dependency group is not installed by the site build):

```bash
uv run --group analysis pytest analysis/mssp-benchmark-ratchet/tests          # tests (about 6 minutes)
uv run --group analysis python analysis/mssp-benchmark-ratchet/ratchet/run.py enrollment   # groups (real data, allowed now)
```

The CMS files are expected in `~/.cache/stharrold-github-io/mssp-snapshot-2026-10-22/` (`--data-dir` to change).
Stages run in the order the plan fixes, and each refuses to start until the previous one has written its output:

```text
enrollment -> validate (results/validation.json) -> power (results/power.json) -> confirm (results/confirm.json)
robustness (results/robustness.json, section 5.5; after power)
did (results/did.json, H4 and its checks, section 5.8; after confirm, because it reads the full PY2022 file)
conventional (results/conventional.json, section 5.7; after did)
exploratory (results/exploratory.json, section 5.6; after confirm)
```

**Outcome lock.** Every file is hashed before it is read. A results, county-spending or county-assignment file that
matches `data-snapshot.tsv` cannot be read until `REGISTRATION.md` exists (`ratchet/snapshot.py`). Synthetic data
directories carry a marker file and load freely; there is no flag to bypass the lock.

**Synthetic dry run.** `ratchet/synthetic.py` writes a made-up snapshot with the real file and column names, and
computes the constructed variables independently in numpy so the SQL can be checked against it:

```bash
uv run --group analysis python -c "import sys; sys.path.insert(0, 'analysis/mssp-benchmark-ratchet'); \
  from pathlib import Path; from ratchet import synthetic; synthetic.generate(Path('/tmp/ratchet-syn'), seed=7)"
for stage in validate power confirm robustness did conventional exploratory; do
  uv run --group analysis python analysis/mssp-benchmark-ratchet/ratchet/run.py $stage \
    --data-dir /tmp/ratchet-syn --out-dir /tmp/ratchet-syn-out --quick
done
```

`--quick` (small resample counts and sampler settings) is refused for real data.

**Runtime with registered settings.** The confirm stage runs about 40,000 MCMC refits (10,000 per core predictor in
H3, plus 10,000 for the overall test). Measured on synthetic data of the same size: about 1.7 s per refit with 5
workers, so roughly 19 hours; `--workers` sets the number of processes (default: half the cores). The robustness and
exploratory stages fit about a dozen models each and take minutes.

## Not yet implemented

The write-up figures. Every analysis in sections 4-6 of the plan is implemented and tested on synthetic data.
