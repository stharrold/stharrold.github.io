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

None so far. Stages run with the registered code (code identical to `a4064f5`): validate and power (commit `fd1920f`),
robustness (`1debc2c`), confirm (`3e5cb9b`; finished 2026-10-27 03:11 EDT, exit 0).
