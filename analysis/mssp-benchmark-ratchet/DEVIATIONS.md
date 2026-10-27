# Deviations from the registered plan and code

Registered: https://osf.io/c53w9/ (2026-10-26 13:22:16 UTC). Registered plan and code: commit `a4064f5`
(`REGISTRATION.md`). Any change after registration to `PREREGISTRATION.md`, `ratchet/`, `dbt/`, `tests/`,
`data-snapshot.tsv`, `pyproject.toml` or `uv.lock` is logged here before any result produced with it is used,
however small (a crash fix included). Each entry gives the date, the stages affected, what changed and why, whether
outcome values had been seen when the change was made, and the commit. The write-up lists these separately from
the registered analyses.

Each results file records the commit it ran at (`git_commit`). Commits after `a4064f5` that touch only this file,
`REGISTRATION.md`, `BUILD-NOTES.md` or `results/` leave the registered code unchanged; check with

```bash
git diff --stat a4064f5 <git_commit> -- analysis/mssp-benchmark-ratchet/ratchet analysis/mssp-benchmark-ratchet/dbt \
  analysis/mssp-benchmark-ratchet/tests analysis/mssp-benchmark-ratchet/data-snapshot.tsv \
  analysis/mssp-benchmark-ratchet/PREREGISTRATION.md pyproject.toml uv.lock
```

(no output means the registered code ran).

## Log

Stages run with the registered code (code identical to `a4064f5`): validate and power (commit `fd1920f`), robustness
(`1debc2c`), confirm (`3e5cb9b`; finished 2026-10-27 03:11 EDT, exit 0), did (`992d13f`), conventional (`acc8b0e`),
exploratory (`ff6e64b`). Every stage has run with the registered code, and no result comes from a changed file.

### 1. `uv.lock`: dependency security updates, after the analysis (2026-10-27)

- **Stages affected:** none. Every stage had run and its results file was committed (the last, exploratory, at
  `ff6e64b`) before this change, and no stage has been run with it.
- **What changed:** merging `src_master` into the study branch brought its `uv.lock` updates from Dependabot:
  filelock 4.0.12 to 4.2.1 (#76) and virtualenv 21.14.5 to 21.14.13 (#75). Together they fix seven GitHub security
  advisories (Dependabot alerts 7-13). `pyproject.toml` and every other registered file are unchanged.
- **Why:** the branch is merged into the site's main branch to publish the write-up, and the lockfile there must
  keep the security fixes. Waiting until after the last stage kept the analysis on the registered environment.
- **Outcomes seen:** yes; all results were final.
- **Effect:** filelock guards PyTensor's compilation cache and virtualenv is used only by development tools;
  neither enters an estimate. The registered tests pass with the updated lockfile
  (`uv run --group analysis pytest analysis/mssp-benchmark-ratchet/tests`: 81 passed). To rerun the analysis
  exactly as registered, use `uv.lock` from `a4064f5`.
- **Commit:** the merge of `src_master` into `src_feature_mssp_prereg` that adds this entry.
