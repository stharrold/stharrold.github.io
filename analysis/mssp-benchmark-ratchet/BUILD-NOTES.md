# Build notes: how this study was built (for the #73 blog post)

A running log of the process, kept for the write-up: what was tried, what was dropped and why, which checks caught
which problems, and how the plan was registered. `DESIGN-NOTES.md` holds the technical detail of the design decisions;
this file is the story. Commit hashes refer to branch `src_feature_mssp_prereg`. Newest entries at the bottom.

## Ground rules (2026-10-22)

- Pre-register before looking at outcomes. Only CMS enrollment files, data dictionaries and regulation text
  (42 CFR 425, via the eCFR API) were used for design. Outcome files (performance-year results, county spending,
  county assignment) were downloaded once to record sha256 hashes (`data-snapshot.tsv`) and left unopened.
- The registration needs an independent timestamp (OSF Registries), because git commit dates can be set by hand.
- The author reviews every rule before registering; the registration is permanent and public.

## Three questions dropped at the design stage (2026-10-22)

1. **Downside risk (the BASIC glide path).** Idea: the glide path forces ACOs into two-sided risk on a schedule, a
   natural experiment. The regulation text (425.600(a)(4)(i)(B)) showed the glide path is a default with opt-outs,
   and enrollment data showed only 10-28% take-up. Dropped (7c82955-1d7fa32).
2. **Benchmark ratchet (spending in benchmark years).** Idea: ACOs spend less once their years start counting toward
   the next benchmark. Enrollment data showed benchmark-year status is collinear with agreement tenure, so the effect
   is not identifiable. Dropped, kept as a descriptive table (3d011d6-e02ac9a).
3. A correction along the way: an unverified inference that "all 139 stay-outs were early renewers" was wrong; agreement
   extensions explained most of them, and only 29 ACOs renewed early into 2022 (e6fb9c3).

## The question that survived: why did 29 ACOs renew early? (2026-10-22)

- v0.2 tested one thing: did early renewers have lower savings? (e0ac5a9)
- The author asked whether the scope was too narrow to explain anything ("are we purposefully limiting the scope...").
  v0.3 became an explanatory plan with two opposing motives: the reset motive (a new benchmark would be higher) and
  the sharing-rate motive (renewal is the only way into the ENHANCED track's 75% sharing) (d3113b5).
- Review caught that the savings rate cannot separate the motives, and that the planned "regional component" contains
  the own-spending term with a negative sign (regional = w x pull - w x own). The primary test became **regional pull**,
  which has no own-spending term (83ff0c2, 2aa2be5).

## Methods chosen by the author (2026-10-22)

- Bayesian estimation throughout, significance by resampling, following VanderPlas, "Statistics for Hackers"
  (PyCon 2016) and the author's 2015 work (`ARCHIVED_2015_Harrold_SDSSJ1600`: shuffled time series for significance,
  emcee MCMC for parameters) (357db23-d354451).
- A side agent pointed out 29 early renewers support only ~3 predictors at 10 events per predictor; the decision model
  was kept small with priors doing the stabilizing.
- Review caught that shuffling labels in a multi-predictor model tests "nothing matters", not "this factor matters
  given the others"; per-factor significance became direct simulation under the reduced model (a parametric
  bootstrap), with the label shuffle kept as an overall test (120053a).

## Writing the code before registering (2026-10-25)

Writing the pipeline before registration exposed gaps in the plan while it could still change.

- **Stack:** DuckDB SQL for the constructed variables (one file per step of section 4.3), PyMC for models, numpy for
  resampling. The author asked whether DuckDB could pre-compute the MCMC runs; it cannot (NUTS is iterative), but it
  made the construction readable and testable.
- **Outcome lock:** every file is hashed before reading; a real outcome file cannot be read until `REGISTRATION.md`
  exists. Synthetic data directories carry a marker. There is no bypass flag.
- **Two implementations:** the synthetic-data generator computes section 4.3 independently in numpy; tests require the
  SQL to match it.
- **Header-only reads** (column names, no values) of outcome files, disclosed in plan section 2.2, found naming drift:
  `ACO_Num` in PY2016-2017, `Sav_Rate` in PY2021, `AGED_Dual` vs `AGDU`.
- Gaps found and pinned by coding: how calibration splits between components, how "below its region" is compared,
  power-simulation sizes, per-refit seeds, the census-region rule, date formats in unseen files.
- **Measured cost:** ~40,000 MCMC refits for the confirmatory stage, ~1.7 s each with 5 workers on synthetic data,
  about 19 hours. (An early estimate of 6 hours missed the overall test.)

## What reviewers and side agents caught (2026-10-25)

- **Suppressed values.** The results files are CMS's suppressed versions; the draft rule dropped any ACO with one
  hidden value, which could cost early renewers. Added a fallback chain (exact recovery of person-years from totals,
  shown years, region x own-to-region ratio) with a complete-case robustness check (b6a190b).
- **Risk adjustment.** The main test compared raw regional spending with each ACO's benchmark. 42 CFR 425.601(c)(4),
  (a)(8)(i)(C) and (a)(3) show CMS risk-adjusts regional spending to the ACO's case mix and restates benchmark years
  to BY3 risk. Implemented, with unadjusted pull kept as a robustness item (3391940).
- **A second validation.** CMS's own benchmark-year spending (PY2022 file, regular renewers only) validates the
  own-spending part separately and sets the measurement-error SD (f062e01).
- **Leak guard.** The PY2022 file would reveal early renewers' actual reset; it is filtered at load to the validation
  sample, and the descriptive stage that needs it runs only after the confirmatory results exist.
- **Fork deadlock risk.** Parallel chains forked a multi-threaded process; switched to `forkserver` (a6a92f1).

## Registration (2026-10-25, in progress)

- All analyses in sections 4-6 coded and tested (72 tests, synthetic data only). Plan v0.5, commit a6a92f1.
- Code zip made with `git archive` at a6a92f1, including `pyproject.toml` and `uv.lock` so package versions are
  frozen; sha256 checked before upload.
- OSF account created via ORCID; email confirmed; draft created (Open-Ended Registration). Title and description
  entered; license CC-By 4.0 (matching the blog); subjects Health Services Research, Health Economics, Health Policy.
- The author asked why register at all; answer recorded: proof the plan predates the results, a credible
  confirmatory/exploratory line, and it unlocks the pipeline. Alternatives considered: AsPredicted, OpenTimestamps.
- Before submitting, the author asked whether conventional methods should be reported side by side for credibility.

## Before registering: conventional methods and an effect question (2026-10-25)

- The author asked whether conventional methods should sit beside the Bayesian and resampling results for
  credibility. Decision: a reported-only comparison section (Welch t, OLS with HC2 errors, maximum-likelihood
  logistic regression) and a table of where the two approaches agree. Adds `statsmodels`.
- The author then asked whether the study should also use difference-in-differences. The plan so far asked only who
  chose to reset and why, not what renewing did. Decision: add H4, the effect of early renewal on per-capita spending
  (PY2022-2024 vs PY2019-2021, early renewers vs stayers from the same cohorts), pre-registered in the same plan before
  any post-period spending is seen. Threats stated up front: selection on recent spending (mean reversion), few
  COVID-era pre-periods, and a bundled treatment (reset + ENHANCED + a change in which years count as benchmark years).
- Registration paused with a private OSF draft until H4 is specified, coded and tested.
