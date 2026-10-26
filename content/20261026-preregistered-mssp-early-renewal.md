Title: Why did Medicare ACOs reset their benchmarks early? A pre-registered study
Status: draft
Date: 2026-10-26T12:00:00Z
Modified: 2026-10-26T12:00:00Z
Tags: causal-inference, pre-registration, bayesian, resampling, difference-in-differences, healthcare, medicare, dbt, duckdb, python
Category: Causal Inference
Slug: 20261026-preregistered-mssp-early-renewal
Authors: Samuel Harrold
Summary: A study of Medicare Shared Savings Program ACOs that ended their agreements early to reset their benchmarks, registered on OSF before any outcome data were read: the plan, the methods, the pipeline and the results.

<!-- DRAFT. Sections marked "Pending" are filled from analysis/mssp-benchmark-ratchet/results/ once every stage has run.
     Report H2b (primary) first, then H2a, H1, H3, H4; robustness after the confirmatory results; deviations in their own
     section (plan section 8). Before publishing: set Date and the slug's date prefix, rename content/static/<slug>/,
     remove the slug from STATIC_EXCLUDES in publishconf.py, and change the dashboard's root-relative /static/ links
     to {static} (Pelican copies {static}-linked files even when STATIC_EXCLUDES lists them, so a draft must not use
     them; once published, {static} makes the build check that the files exist). Check H1's units (fraction or percent
     in the PY2020-PY2021 files) against power.json's before comparing H1 with its MDE. Finally delete this comment
     and every "pending" comment: HTML comments are published in the page source. -->

[TOC]

## Overview

In the Medicare Shared Savings Program (MSSP), an accountable care organization (ACO) earns a share of the savings
when its patients' spending comes in below a benchmark. The benchmark is reset at the start of each agreement period
from the ACO's own recent spending, pulled toward its region's. An ACO can end its agreement early and start a new
one, which resets the benchmark early. For the 2022 agreement cycle, 29 of the 306 ACOs in agreements that began in
2019 or 2020 ended them early and started new ones.

This post asks why they did, and what renewing changed:

* **Who chose to reset, and why (H1-H3).** Did early renewers stand to gain from a reset because their regions spent
  more than their benchmarks (the primary test), because their own spending had run high, or because renewing was
  the only way into the track that shares 75% of savings?
* **What renewing did (H4).** Did early renewers' spending change afterwards, relative to ACOs that had not yet
  renewed? A difference-in-differences estimate.

The analysis plan was registered on [OSF Registries](https://osf.io/c53w9/) (DOI
[10.17605/OSF.IO/C53W9](https://doi.org/10.17605/OSF.IO/C53W9)) before any outcome value was read, together with the
analysis code, which was written and tested on synthetic data first. Every result below is reported, whatever it
shows; changes made after registration are listed separately under [Deviations](#deviations).

*Pending: a three-sentence summary of the results, primary test first.*

<!-- pending: confirm.json, did.json -->

## Why pre-register

The CMS public use files used here are public. Anyone analyzing them can try many specifications and
report the one that works, often without meaning to. A pre-registration fixes the question, the variables, the tests
and the decision rules before the outcomes are seen, so a reader can tell confirmatory results from exploration.

Two details make that claim checkable here:

* **An independent timestamp.** Git commit dates can be set by hand, so the plan was registered on OSF, which records
  the time itself. The plan file's sha256 and the registered code commit are recorded in
  [`REGISTRATION.md`](https://github.com/stharrold/stharrold.github.io/blob/src_master/analysis/mssp-benchmark-ratchet/REGISTRATION.md),
  so the repository copy can be matched to the registered one.
* **An outcome lock in the code.** Every data file is hashed before it is read. A file whose hash matches a
  performance-year results file or a county spending file could not be opened until `REGISTRATION.md` existed. There
  was no bypass flag. Before registration only the enrollment files, the CMS data dictionaries and the regulation
  text were used, plus the column names (not the values) of the outcome files, to write the code.

## How the question was chosen

The question in this post was the fourth candidate. The first three were dropped at the design stage, using only the
regulation and the enrollment files:

1. **Downside risk.** The program's "glide path" moves ACOs into two-sided risk on a schedule, which looked like a
   natural experiment. The regulation (42 CFR 425.600) showed it is a default that ACOs can opt out of, and the
   enrollment files showed that only about 10-28% of ACOs were in two-sided risk in the years the schedule called
   for it. Not a usable treatment.
2. **The benchmark ratchet.** Do ACOs spend less once their spending starts counting toward the next benchmark? In
   the enrollment data, benchmark-year status is collinear with how long the ACO has been in its agreement, so the
   effect cannot be separated from tenure. Kept only as a descriptive table.
3. **A correction.** An early tabulation found 139 ACOs leaving their benchmark-year schedule at the 2022
   transition, and an unverified inference treated them all as early renewers. Accounting for the optional
   one-year extension of agreements that began in 2018 showed that only 29 renewed early into a January 1, 2022
   agreement.

Those 29 became the question. A first version asked only whether they had lower savings rates. That was too narrow
to explain anything, so the plan became explanatory, with two motives that predict different things.

## Design

### Groups

The base population is the 334 ACOs whose agreements began July 1, 2019 or January 1, 2020. Both cohorts' agreements
run to December 31, 2024, so a January 1, 2022 agreement start means an early renewal (42 CFR 425.20, 425.200).

| Group | 2019-07-01 cohort | 2020-01-01 cohort | All |
|---|---|---|---|
| Early renewers | 11 | 18 | 29 |
| Stayers | 159 | 118 | 277 |
| Left after PY2021 | 19 | 9 | 28 |

### Two motives, and why the savings rate cannot separate them

* **The reset motive.** A new benchmark would be higher than the current one.
* **The sharing-rate motive.** Renewing is the only way for an ACO in the BASIC track to move to the ENHANCED track,
  which shares 75% of savings (and losses). In the enrollment files, 26 of the 27 early renewers that were in BASIC
  moved to ENHANCED, and no stayer did.

The expected benchmark gain from a reset has two parts: an **own-spending** part (how the ACO's recent spending
compares with its current benchmark) and a **regional** part (the adjustment toward the region). The own-spending
part is close to a restatement of the savings rate. Writing out the regional adjustment shows that it contains the
own-spending part too, with a negative sign. With phase-in weight $w$, before capping,

$$\text{regional component} = w \times (\text{pull} - \text{own})$$

where "pull" is the regional pull defined below and "own" the own-spending component, so the regional part is also
tied to past savings. The primary test therefore uses the **regional pull**: how far the region's
spending, adjusted to the ACO's case mix the way CMS adjusts it, sits above the ACO's current benchmark,

$$\text{regional pull} = 100 \times \frac{\sum_e s_e\, R_e - B}{B}$$

where $R_e$ is the risk-adjusted regional spending for enrollment type $e$ (ESRD, disabled, aged/dual,
aged/non-dual), $s_e$ the ACO's share of person-years of that type, and $B$ its current per-capita benchmark. It has
no own-spending term. An ACO can be beating its own benchmark and still stand to gain from a reset because its
region spends more; that is the part of the reset motive a savings rate cannot show.

### Hypotheses

| | Hypothesis | Role |
|---|---|---|
| **H2b** | Early renewers had a larger regional pull than stayers | Primary |
| H2a | Early renewers had a larger own-spending component | Secondary (close to H1 restated) |
| H1 | Difference in PY2020 savings rate | Descriptive context, no motive attributed |
| H3 | Among BASIC-track ACOs, the probability of renewing rises with regional pull, own-spending component and a higher BASIC level | Decision model |
| H4 | Early renewal changed per-capita spending in PY2022-PY2024 | Effect estimate, two-sided |

H1-H3 describe who chose to reset and why; they are associations, not effects. H4 estimates the effect of a bundled
package (a new benchmark, for almost all a move to ENHANCED, and a change in which years count toward the next
benchmark) and cannot separate its parts.

### Building the expected gain from public data

CMS does not publish what an ACO's benchmark would have been had it reset. The plan rebuilds it from 42 CFR 425.601
in six steps: the mean of the ACO's per-capita spending in the three benchmark years (PY2019-PY2021), restated to
the latest year's risk scores and trended to 2021 dollars with the national-regional blend; risk-standardized
regional spending from the county files, weighted by where the ACO's beneficiaries live and adjusted to the ACO's
case mix; the regional adjustment with the phase-in weights and caps; and the shares that combine the four
enrollment types.

Because several steps can only be approximated from public files, the approximation was **validated before it was
used**: rebuilt for the 101 regular renewers whose 2022 benchmarks CMS does publish, with a pass rule fixed in the
plan (Spearman correlation at least 0.80, median absolute percentage error at most 5%). Early renewers were kept
out of the validation sample, and the 2022 results file was filtered as it was loaded, so validation could not
reveal their actual reset.

## Methods

### Estimates and significance

Every confirmatory estimate is Bayesian, and significance is measured by resampling, following Jake VanderPlas's
"Statistics for Hackers" (PyCon 2016): simulate the null instead of looking up a distribution.

* **Group comparisons (H1, H2a, H2b, H4).** The estimate is the difference in means, early renewers minus stayers,
  within each cohort and averaged with weights proportional to the early renewers in each cohort. Its posterior is a
  Bayesian bootstrap (Rubin 1981): 10,000 draws of Dirichlet(1, ..., 1) weights over the ACOs in each cohort-by-group
  cell.
* **Significance by stratified permutation.** Early-renewer labels are shuffled within cohort 10,000 times, and the
  estimate is recomputed on each shuffle. The two-sided p-value is

    $$p = \frac{1 + \#\{\,|\hat\theta_\text{shuffled}| \ge |\hat\theta_\text{observed}|\,\}}{1 + 10{,}000}$$

  The resampling p-value decides, by rules written before the results (below). When it and the credible interval
  disagree, both are reported.

### H3: a Bayesian decision model with measurement error

A logistic regression of early renewal on the three core predictors (regional pull, own-spending component, higher
BASIC level) and five adjustment factors (cohort, size, revenue category, assignment method, first or later
agreement), fit with PyMC (NUTS, 4 chains of 2,000 draws). Continuous predictors are scaled by two standard
deviations (Gelman 2008), so each coefficient is a log-odds difference per 2 SD. With 27 events and 9 parameters,
the Normal(0, 1) priors keep the estimates stable, so a second fit with Student-t priors is reported for sensitivity.
A Firth-penalized logistic regression (Firth 1993) with the core predictors and cohort is always run beside it, and
decides H3 only if the Bayesian model fails its convergence checks.

The own-spending component is an approximation, so it enters as a latent true value observed with error,

$$x_\text{observed} = x_\text{true} + \varepsilon, \qquad \varepsilon \sim \mathcal{N}(0, \sigma_v)$$

with $\sigma_v$ set by the validation step before the model is fit (4.38 percentage points, from CMS's own
benchmark-year spending for the validation sample).

Shuffling labels in a model with several predictors would test "nothing matters", not "this factor matters given the
others". Each core predictor is instead tested by **direct simulation under the reduced model** (a parametric
bootstrap): fit the model without that predictor, simulate 10,000 sets of outcomes from its posterior, refit the
full model to each, and compare the observed coefficient with that null distribution. That is about 40,000 MCMC
refits, roughly 19 hours on 5 cores.

### H4: difference-in-differences with an equivalence rule for pre-trends

The outcome is log per-capita spending. For each ACO,

$$\Delta = \overline{y}_\text{PY2022-24} - \overline{y}_\text{PY2020-21}$$

and the H4 estimate is the same cohort-weighted difference in means as above, applied to $\Delta$. Comparison ACOs
are those **not yet renewed**: a stayer's years after it renews into a 2023 or 2024 agreement are dropped, following
the not-yet-treated idea of Callaway and Sant'Anna (2021).

The main threat is selection on the outcome's own path: if early renewers renewed after unusually high spending,
their spending could fall afterwards by mean reversion alone. There is only one pre-period change (PY2020 to PY2021,
both affected by COVID-19), and with about 29 treated ACOs a non-significant pre-trend test proves little (Roth
2022). So H4 counts as an effect only if an **equivalence condition** holds: the pre-trend interval, scaled to the
distance between period midpoints, must rule out a trend difference large enough to produce the estimate. A
trend-adjusted estimate (the pre-period slope carried forward, in the spirit of Rambachan and Roth 2023) is reported
beside it, along with propensity-weighted, risk-adjusted, balanced-panel and single-cohort versions.

### Conventional methods, side by side

For comparison, and not used for any decision: Welch t-tests and OLS with HC2 robust errors for H1, H2a and H2b;
maximum-likelihood logistic regression for H3; and two-way fixed effects with an event study, errors clustered by
ACO, for H4. An agreement table puts each registered verdict next to the conventional one.

### Decision rules

Fixed before the results (plan section 7). For H2b: p < 0.05 and positive means "early renewers' regions spent more
relative to their current benchmarks, evidence for the reset motive beyond past savings"; p < 0.05 and negative is
evidence against it; otherwise "no detectable difference", reported with the credible interval and the minimum
detectable effect. No test here can rule the sharing-rate motive in or out, because in these data it is bundled with
the reset in a single choice.

## Pipeline

The pipeline is in
[`analysis/mssp-benchmark-ratchet/`](https://github.com/stharrold/stharrold.github.io/tree/src_master/analysis/mssp-benchmark-ratchet):

* **Data snapshot.** Every CMS file used is listed with its size, sha256 and URL in `data-snapshot.tsv`, and each
  hash is checked before the file is read.
* **dbt for the SQL.** The constructed variables are a [dbt-duckdb](https://github.com/duckdb/dbt-duckdb) project:
  28 models, one per derived table, in three tagged stages, with schema and data tests (unique keys, accepted
  values, components adding to the gain, shares summing to one, no early renewer in the validation load). Python
  loads every raw table after its hash check, so dbt never reads a file directly.
* **Two implementations.** A synthetic-data generator writes made-up files with the real file and column names and
  computes the constructed variables independently in numpy. The tests require the SQL to match it, and every stage
  runs end to end on synthetic data, including the recovery of a planted -4% effect in H4.
* **Staged runner.** Stages run in the plan's order (validate, power, confirm, robustness, did, conventional,
  exploratory), and each refuses to start until the output it depends on exists, so the power analysis is
  committed before any confirmatory estimate.
* **Reproducible environment.** uv with a lockfile; PyMC, `firthmodels` and `statsmodels` are pinned in `uv.lock`, and
  every refit has its own seed from a fixed seed sequence, so results do not depend on the number of processes.

Writing the code before registering found gaps in the plan while it could still change: column names that drift
between years (`ACO_Num` and `ACO_ID`, `Sav_Rate` and `Sav_rate`), how calibration splits between the gain's two
parts, how "below its region" is compared, and the per-refit seeds.

## What review caught before registration

Independent reviews of the plan and code, each given only the files, found problems that would have been permanent
once registered:

* **The first primary test was mechanically tied to past savings.** The "regional component" contains the
  own-spending part with a negative sign; the primary test became the regional pull.
* **Raw regional spending is not what CMS compares.** The regulation risk-adjusts regional spending to the ACO's case
  mix and restates benchmark years to the latest year's risk; both were implemented, with the unadjusted version
  kept as a robustness check.
* **Suppressed values.** The results files hide small cells, and the first rule dropped any ACO with one hidden
  value. A fallback chain (exact recovery from totals, then shown years, then a regional ratio) replaced it, with a
  complete-case check.
* **A permutation test that tests the wrong null** in a multi-predictor model, replaced by direct simulation (above).
* **Pre-trend testing with one pre-period**, replaced by the equivalence condition (above).
* **A status line** in the plan that still said "DRAFT ... Not yet registered", and would have been frozen into the
  public record.

## Registration

| Item | Value |
|---|---|
| Registration | [osf.io/c53w9](https://osf.io/c53w9/), DOI [10.17605/OSF.IO/C53W9](https://doi.org/10.17605/OSF.IO/C53W9) |
| Registered | 2026-10-26 13:22:16 UTC, public, no embargo |
| Plan | `PREREGISTRATION.md` v0.6, sha256 `d0e374c8b493eb2f2fa7da1c0d8cbe46745a601233f11a81d2b2be73c402e8f2` |
| Code | commit [`a4064f5`](https://github.com/stharrold/stharrold.github.io/tree/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet), zip sha256 `4c98d76a586151ab608851c69217a5ddb6b394201643a3de89a839bb1f659cd4` |

The zip can be rebuilt from the repository and checked against the registered copy:

```bash
git archive --format=zip a4064f5 analysis/mssp-benchmark-ratchet pyproject.toml uv.lock | shasum -a 256
```

Registering had its own lessons. OSF's summary field does not render Markdown and deletes anything that looks like an
HTML tag, so the summary is a plain-text copy of the plan with placeholders such as `<e>` written `{e}`; the
attached Markdown file is the authoritative version. Checking the saved draft through the OSF API, not the page,
caught two silent losses before submission.

## Power

Computed after registration and committed before any confirmatory estimate, as the plan requires. Minimum detectable
effects at 80% power, two-sided alpha 0.05, for 29 vs 277 ACOs:

| Test | Minimum detectable effect |
|---|---|
| H1 savings rate | 2.7 percentage points (simulated power 80.4%) |
| H2b regional pull | 2.5 percentage points |
| H2a own-spending component | 1.8 percentage points (0.55 SD) |
| H4 spending change | 3.8% (log 0.038) |

**H3 is underpowered.** At a true log-odds difference of 0.5 per 2 SD, the 95% interval excludes zero in only 17%
(regional pull), 0% (own-spending component) and 14% (BASIC level) of simulated datasets. An "undetermined" H3
verdict is therefore the expected outcome, whatever the motives were.

## Results

*Pending. Filled from `results/confirm.json`, `results/did.json` and `results/conventional.json` after every stage has
run, in this order:*

1. *Validation of the benchmark approximation (passed: Spearman 0.94, median absolute percentage error 1.6%, 101
   ACOs).*
2. *H2b, the primary test: estimate, 95% credible interval, permutation p-value, verdict by rule 1.*
3. *H2a, then H1 (descriptive), with the total gain and the regional component alongside.*
4. *H3: each core predictor supported, contradicted or undetermined; adjustment factors as estimates only; prior
   sensitivity and posterior predictive checks.*
5. *H4: estimate as a percent difference in spending growth, the pre-trend estimate and whether the equivalence
   condition holds, the trend-adjusted estimate.*
6. *The agreement table with the conventional methods.*

<!-- pending: confirm.json, did.json, conventional.json -->

### Interactive results

<!-- The dashboard reads data.json, built by analysis/mssp-benchmark-ratchet/report/dashboard_data.py from results/.
     It shows a banner while the data are synthetic; rebuild data.json from the real results before publishing. -->

<link rel="stylesheet" href="/static/20261026-preregistered-mssp-early-renewal/dashboard.css">
<div id="mssp-dashboard" class="mssp-dash" aria-live="polite"><p>Loading the interactive results...</p></div>
<script src="/static/20261026-preregistered-mssp-early-renewal/dashboard.js" defer></script>

## Robustness

*Pending. The nine robustness checks of plan section 5.5 and the five H4 checks of section 5.8, read only after the
confirmatory results. They do not change the verdicts.*

## Exploratory

*Pending. Labeled exploratory: census region in the decision model, ACOs that left, the two early renewers already
in ENHANCED, the phase-in-weighted pull, and spending by agreement year.*

## Deviations

*Pending. Every change after registration to the plan or the registered code, from
[`DEVIATIONS.md`](https://github.com/stharrold/stharrold.github.io/blob/src_master/analysis/mssp-benchmark-ratchet/DEVIATIONS.md),
with whether outcome values had been seen when it was made. Stages run so far used the registered code unchanged.*

## Limitations

* **Bundled motives.** In these data, renewing early and moving to ENHANCED are one choice, so no test here can
  separate the sharing-rate motive from the reset motive. The regional pull is the part of the reset motive that is
  not a function of past savings, not a test that rules the other motive out.
* **An approximate benchmark.** The expected gain is rebuilt from public files; the validation bounds the error but
  does not remove it, and the regional part has no published counterpart to check against.
* **Few early renewers.** 29 ACOs, 27 in the decision model: the power analysis shows what can and cannot be detected.
* **One COVID-era pre-period** for H4, which is why the equivalence condition, not a pre-trend test, decides whether
  H4 is read as an effect.

## Reproduce

```bash
git clone https://github.com/stharrold/stharrold.github.io.git && cd stharrold.github.io
uv run --group analysis pytest analysis/mssp-benchmark-ratchet/tests
uv run --group analysis python analysis/mssp-benchmark-ratchet/ratchet/run.py validate   # then power, confirm, ...
```

The CMS files are listed in `data-snapshot.tsv` with their URLs and hashes; the runner checks every hash before
reading. `ratchet/synthetic.py` writes a synthetic snapshot for a dry run without CMS data.

## References

* 42 CFR Part 425, Medicare Shared Savings Program, as in force on 2022-01-01 (eCFR).
* Callaway, B. and Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. *Journal of
  Econometrics* 225(2), 200-230.
* Gelman, A. (2008). Scaling regression inputs by dividing by two standard deviations. *Statistics in Medicine*
  27(15), 2865-2873.
* Rambachan, A. and Roth, J. (2023). A more credible approach to parallel trends. *Review of Economic Studies* 90(5),
  2555-2591.
* Roth, J. (2022). Pretest with caution: event-study estimates after testing for parallel trends. *American Economic
  Review: Insights* 4(3), 305-322.
* Rubin, D. B. (1981). The Bayesian bootstrap. *Annals of Statistics* 9(1), 130-134.
* VanderPlas, J. (2016). Statistics for Hackers. PyCon 2016.
* Firth, D. (1993). Bias reduction of maximum likelihood estimates. *Biometrika* 80(1), 27-38.
