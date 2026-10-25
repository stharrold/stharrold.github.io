# Pre-registration: Why did Medicare ACOs reset their benchmarks early?

**Status:** DRAFT v0.5 (author decisions of 2026-10-22 and 2026-10-25 applied; analysis code written and tested on
synthetic data). Not yet registered. Once registered on OSF Registries, this file is frozen:
the registration link, OSF timestamp, and this file's sha256 go in `REGISTRATION.md`, and any later change goes in
`DEVIATIONS.md`. Issue #73. Supersedes drafts v0.1 (a downside-risk question dropped at the design stage), v0.2
(a single-test version of this plan) and v0.3 (frequentist tests) and v0.4 (before the code); see `DESIGN-NOTES.md`.

**Author:** Samuel Harrold. **Drafted:** 2026-10-22. **Revised:** 2026-10-25.

## 1. Study information

### 1.1 Background
In the Medicare Shared Savings Program, an ACO earns shared savings when its assigned beneficiaries' spending falls
below a benchmark. The benchmark is **reset at the start of each new agreement period** from the ACO's own spending in
the three preceding years, adjusted toward its region's spending (42 CFR 425.601, version in force 2022-01-01). This
creates a "ratchet": the more an ACO's recent spending runs above its current benchmark, the more a reset raises its
benchmark; the further below, the more a reset lowers it. ACOs may end an agreement early and immediately start a new
one (a "renewing ACO", 42 CFR 425.20), which resets the benchmark early. Renewing is also the only way for a BASIC-track
ACO to enter the ENHANCED track, which shares 75% of savings and losses.

### 1.2 Research question
Among ACOs in agreement periods that began July 1, 2019 or January 1, 2020, why did some renew early into a
January 1, 2022 agreement while others stayed in their agreement?

### 1.3 Hypotheses
Two motives can lead an ACO to renew early: the **reset motive** (a new benchmark would be higher) and the
**sharing-rate motive** (enter ENHANCED and keep 75% of savings). They are bundled in one choice here (1.4), and they
need not point to different ACOs: a reset can itself create expected savings that make ENHANCED attractive. The
expected benchmark gain (section 4.3) has two parts: an **own-spending** part (how the ACO's recent spending compares
with its current benchmark) and a **regional** part (the regional adjustment). The own-spending part is close to a
restatement of the savings rate, so a low savings rate and a positive own-spending gain are the same fact. The
regional part, as an adjustment of the rebased benchmark toward the region, also contains the own-spending part with a
negative sign (it equals w x regional pull - w x own-spending part, section 4.3 step 6), so it too is mechanically tied
to the savings rate. The primary test therefore uses the **regional pull**: how far the region's spending, adjusted
to the ACO's case mix as CMS adjusts it (4.3 step 2), sits above the ACO's current benchmark, with no own-spending
term. An ACO can be beating its own benchmark and still stand to gain
from a reset because its region spends more; that is the part of the reset motive the savings rate cannot show.

- **H2b (primary):** Early renewers had a larger **regional pull** than stayers. Predicted sign: positive.
- **H2a (secondary):** Early renewers had a larger **own-spending component** of the expected gain. Predicted sign:
  positive.
- **H3 (Bayesian decision model, BASIC-track ACOs):** The probability of renewing early rises with the regional pull
  (+), the own-spending component (+), and being at a higher BASIC level in PY2021 (+, a smaller step to two-sided risk
  under ENHANCED), adjusting for cohort, size, revenue category, assignment method and first vs later agreement, which
  are estimated with no predicted direction. Section 5.4.
- **H1 (pre-registered, descriptive context):** Difference in PY2020 savings rate, early renewers minus stayers,
  two-sided, with no motive attributed to its sign. Repeated for PY2021, the year of the decision.

Exploratory: section 5.6.

### 1.4 What this is and is not
An analysis of **who chose to reset and why**, not of the causal effect of renewing. Associations with pre-decision
characteristics are interpreted as evidence about motives, not as effects. The question "does spending change once an
ACO's years start counting toward its next benchmark?" is not identifiable in these data (benchmark-year status is
collinear with agreement tenure; `DESIGN-NOTES.md` 4.4) and is reported only descriptively. In the enrollment files no
stayer moved to ENHANCED, and 26 of the 27 early renewers that were in BASIC in PY2021 entered ENHANCED, so the reset
and sharing-rate motives are bundled in one choice. The regional pull (H2b) is the part of the analysis that
bears on the reset motive without being a mechanical function of past savings; no test here can rule the sharing-rate motive in or out.

## 2. Data

### 2.1 Sources
CMS Medicare Shared Savings Program public use files (data.cms.gov, public data only):
- **Performance Year Financial and Quality Results:** PY2019 (July-December period), PY2020, PY2021 (outcomes and
  benchmark inputs); PY2022 (validation of the benchmark approximation, section 4.4); PY2016-PY2018 (power analysis
  only).
- **Accountable Care Organizations** enrollment files, PY2021 and PY2022 (groups, risk levels, validation sample);
  PY2016-PY2020, including both PY2019 files (agreement history for the phase-in step, section 4.3 step 3).
- **County-level Aggregate Expenditure and Risk Score Data on Assignable Beneficiaries**, calendar years 2019, 2020,
  2021, the versions published for 2022-2023 starters (`FFS_Data_for_SSP_CRB_PUF_<year>_01_01_Cal_Year_Assignable_
  2022_2023_Starters.csv`) (regional spending).
- **Number of ACO Assigned Beneficiaries by County**, 2021 (each ACO's regional service area in BY3, and its share s
  of assignable beneficiaries, section 4.3; census region, section 5.6).
- **Performance Year Financial and Quality Results**, PY2023 and PY2024: only for the descriptive spending-by-
  agreement-year table (section 5.6).

Exact files, sizes, sha256 hashes and URLs: `data-snapshot.tsv` (downloaded 2026-10-22). The manifest also lists files
not used here, retained from the design stage. The pipeline verifies every hash before reading.

### 2.2 What the author has and has not seen (data already exist)
The data are public and were downloaded before registration solely to record hashes. Before registration the author
used: the CMS data dictionaries, the regulation (42 CFR 425.20, 425.200, 425.600, 425.601, 425.603), and the
**enrollment** files, from which the groups below, risk levels, take-up of an earlier candidate design, and program
exits were counted (`DESIGN-NOTES.md`). **No values from the results files or the county-level files (spending,
savings, benchmarks, quality, regional expenditures) have been viewed.** On 2026-10-25, to write the analysis code, the
first row (column names only) of the PY2016-PY2022 results files, the 2019-2021 county-level expenditure files
and the 2021 county assignment file was read, and on 2026-10-25 also of the PY2023 and PY2024 results files; no data
rows. The analysis code was tested on synthetic data with made-up
values. The hypotheses were formed from the
regulation and the existence of the early-renewal group. The author is aware of published research on MSSP savings in
general.

## 3. Sample and groups

Base population: ACOs whose PY2021 enrollment record shows an agreement start of 2019-07-01 or 2020-01-01
(334 ACOs). Groups, from the PY2022 enrollment file:

| Group | 2019-07-01 cohort | 2020-01-01 cohort | All |
|---|---|---|---|
| **Early renewers:** 2022-01-01 agreement in PY2022 | 11 | 18 | 29 |
| **Stayers:** same agreement in PY2022 | 159 | 118 | 277 |
| Left after PY2021 (not in PY2022 file) | 19 | 9 | 28 |

**Why a 2022 start means early renewal:** agreements starting July 1, 2019 run 5 years 6 months and those starting
January 1, 2020 run 5 years (42 CFR 425.200(b)(4)(ii), (b)(5)), so both end December 31, 2024; a 2022 agreement from
these cohorts is an early renewal (425.20, "renewing ACO" (2)).

Early renewers are compared with stayers; leavers are reported descriptively. ACOs are linked across files by
`ACO_ID`. Non-numeric cells (such as suppression markers; the results files are CMS's suppressed versions) are read
as missing. **Hidden values in the expected-gain construction (4.3)** are filled, in this order, and the ACO is
flagged as imputed: (1) a single hidden PY2021 person-year count for a type = the total (`N_AB_Year_PY`) minus the
other three types (exact); (2) a type's per-capita spending hidden in some benchmark years = the mean of that type's
trended spending over the years in which it is shown; (3) a type's spending hidden in every benchmark year = for each
year, the region's spending for that type (4.3 step 2) times the ACO's own-to-region spending ratio that year over its
types with positive share and spending shown, then trended and averaged as in step 1; (4) a hidden ACO risk score
for a type and year = no restatement of that year (4.3 step 1) and, in step 2, the region's weighted mean county risk
score for that type in place of the ACO's. A type with zero PY2021 share does not enter the benchmark, so its hidden values need no filling. Any ACO still missing a variable needed for an
analysis (for example, two or more hidden person-year counts) is excluded from that analysis and counted. The number
of imputed ACOs is reported by group. If more than 10% of either compared group is excluded from the primary
analysis, this is reported as a limitation.

## 4. Variables

### 4.1 Outcomes and characteristics from the results files
- `Sav_rate` (PY2020 primary, PY2021 secondary): total benchmark expenditures minus assigned-beneficiary expenditures,
  as a percent of total benchmark expenditures. CMS's final PY2020 results reached ACOs around autumn 2021, during the
  application cycle for 2022 agreements; each ACO also received CMS quarterly reports during 2020-2021, so its own
  PY2020 position was broadly known to it before the decision.
- Size: `N_AB` (assigned beneficiaries), PY2020.
- In PY2020 and PY2021 all U.S. counties were treated as affected by an extreme and uncontrollable circumstance
  (COVID-19), which reduces shared losses but not the savings-rate calculation.

### 4.2 Characteristics from the enrollment files
Cohort (2019-07-01, 2020-01-01); PY2021 track and level (BASIC A-E or ENHANCED); for H3, **higher BASIC level**
= BASIC C-E (two-sided) vs BASIC A-B (one-sided);
revenue category (high/low revenue), assignment method (prospective/retrospective), agreement period number.

### 4.3 Expected benchmark gain from resetting (constructed)
An approximation of how much a January 1, 2022 reset would have changed the ACO's benchmark, built from public data
following 42 CFR 425.601 as in force on 2022-01-01. For each ACO:

1. **Rebased historical benchmark, per enrollment type** e in {ESRD, disabled, aged/dual, aged/non-dual}: the equally
   weighted mean (renewing ACO, 425.601(e)(2)(i)) of the ACO's per-capita expenditures for BY1-BY3 = PY2019-PY2021
   (`Per_Capita_Exp_ALL_<e>_PY`, annualized in the files). For PY2019 the ACO's record in the PY2019 results file is
   used (12-month performance year or July-December period, whichever exists for that `ACO_ID`; never the
   January-June "2019A" file); if the ACO has no
   PY2019 record, BY1 is omitted and the mean uses BY2-BY3 (PY2020 and PY2021 records are required; hidden values
   within a record follow section 3). BY1 and BY2 are restated to BY3 case mix by multiplying by the ratio of the
   ACO's PY2021 to that year's mean prospective CMS-HCC risk score for the type (`CMS_HCC_RiskScore_<e>_PY`;
   425.601(a)(3)), and
   trended to BY3 (2021) dollars with the national-regional blend of 425.601(a)(5)(iv): growth factor =
   s x national growth + (1 - s) x regional growth for type e from the benchmark year to 2021, where regional growth
   uses the ACO's risk-standardized regional spending (step 2, before the case-mix adjustment), national growth uses the assignable-beneficiary-weighted
   national mean of the county file (`PER_CAPITA_EXP_<e>` weighted by `PERSON_YEARS_<e>`), and s, the ACO's share of
   assignable beneficiaries in its regional service area (425.601(a)(5)(v)), = sum over counties of (ACO assigned
   person-years in county, `Tot_AB_Psn_Yrs` / county assignable person-years, the sum over types of
   `PERSON_YEARS_<e>`), weighted by the ACO's share of its `Tot_AB_Psn_Yrs` in each county, from the 2021 files.
2. **Regional service area spending, per type**, for BY3 = 2021: county per-capita expenditures for assignable
   beneficiaries of type e are risk-standardized by dividing by the county's mean risk score (`PER_CAPITA_EXP_<e>` /
   `AVG_RISK_SCORE_<e>`, county-level file, 2022-2023 starters version; 425.601(c)(4)), averaged with weights equal to
   the ACO's assigned person-years of type e by county in 2021 (`AB_Psn_Yrs_<e>` in
   `Number_Of_ACO_Assigned_Beneficiaries_by_County_PUF_2021_01_01.csv`, the 2021
   performance-year assignment, used as the BY3 proxy; true BY3 assignment uses the 2022 participant list, which is
   not published; 425.601(d)), and multiplied by the ACO's PY2021 mean prospective CMS-HCC risk score for the type
   (`CMS_HCC_RiskScore_<e>_PY`), adjusting the region to the ACO's case mix (425.601(a)(8)(i)(C)). The same
   calculation for 2019 and 2020 (with that year's county file and the ACO's risk score for that year) is used only
   in section 3, rule 3.
3. **Regional adjustment, per type:** w x (regional - rebased), where w follows 425.601(f): the phase-in step for the
   2022 reset = 1 + the number of the ACO's earlier agreement periods whose benchmark was regionally adjusted, i.e.
   renewals starting 2017-01-01 through 2019-01-01 (425.603(c)) and any agreement starting 2019-07-01 or later
   (425.601), counted from the distinct `current_start_date` values for the `ACO_ID` in the PY2016-PY2021 enrollment
   files (no regional adjustment existed before 2017); w = 35%/50%/50%/50% at steps 1-4+ if the
   ACO's share-weighted rebased spending (sum over types of rebased x PY2021 share) is below its share-weighted
   regional spending (step 2) and 15%/25%/35%/50% if above (425.601(f)(5)). Each type's adjustment is
   capped at +/-5% of the national per-capita expenditure for that type in 2021, approximated by the assignable-
   beneficiary-weighted national mean in the county file.
4. **Approximate new benchmark** = sum over types of (rebased + adjustment) x the ACO's PY2021 person-year share of
   that type (`N_AB_Year_<e>_PY`, with a single hidden count recovered as in section 3).
5. **Expected gain (%)** = 100 x (approximate new benchmark - current benchmark) / current benchmark, where current
   benchmark = the PY2021 per-capita updated benchmark (`UpdatedBnchmk`, already per capita in the files). Both are in
   2021 dollars. **Components:** own-spending component = 100 x (sum over types of rebased x share - current) /
   current; regional component = 100 x (sum over types of adjustment x share) / current; they add to the expected
   gain.
6. **Regional pull (%)** = 100 x (sum over types of regional spending x share - current) / current, using the step 2
   regional spending and the step 4 shares. Uncapped and without the phase-in weight, so it depends on the region and
   the current benchmark but not on the ACO's own BY1-BY3 spending. Before capping and with one weight w for all
   types, regional component = w x regional pull - w x own-spending component.

Steps that cannot be reproduced exactly from public data (risk-score renormalization and the exact case-mix
adjustment, truncation details, assignment differences between performance and benchmark years, the national-regional
growth blend) are approximated as stated;
section 4.4 measures how good the approximation is before it is used.

### 4.4 Validation of the approximation (run before H2a, H2b and H3 are estimated)
Apply steps 1-4 to every **regular renewer** with a January 1, 2022 agreement (agreement period number >= 2 in PY2022,
benchmark years 2019-2021, not one of the 29 early renewers, and with a PY2021 enrollment record under the same
`ACO_ID`; 111 ACOs by the enrollment files, 110 of them in agreements that began 2018-01-01; 20 re-entering ACOs
without a PY2021 record are excluded) and compare the approximate new benchmark with the actual
per-capita historical benchmark reported for PY2022 (`HistBnchmk`, already per capita); the validation n is the number
of these ACOs with `HistBnchmk` present. Early renewers are excluded so that validation does not reveal their actual
reset gain before H2a, H2b and H3 are estimated: the code reads PY2022 results only for the validation sample, filtered
as the file is loaded, because its `Per_Capita_Exp_ALL_<e>_BY1`-`BY3` columns would show early renewers' actual
rebased spending. The regional pull
(step 6) uses no own-spending data, so it does not depend on validation; it is still reported only after the
validation step. Reported overall and by phase-in step (step 3 of 4.3; steps with at least 3 ACOs): Spearman correlation, median absolute percentage error, and the OLS slope and intercept of actual on
approximate. The **validation error SD** is the standard deviation of 100 x (approximate - actual) / actual across
these ACOs, after calibration if calibration is applied.

**Step-1 check (own-spending part).** The PY2022 results file also reports, for these ACOs, CMS's own benchmark-year
spending and risk scores by type (`Per_Capita_Exp_ALL_<e>_BY1`-`BY3`, raw annualized per-capita spending under the
2022 participant list, and `CMS_HCC_RiskScore_<e>_BY1`-`BY3`). Step 1 of 4.3 is recomputed from those values with the
same restatement (BY3 to BYx risk ratio), trend factors and PY2021 shares (step 4), and compared with
the approximate rebased benchmark (after calibration, if applied): Spearman correlation, median absolute percentage
error, OLS slope and intercept, and the **own-spending error SD** = the standard deviation of 100 x (approximate
rebased - CMS rebased) / current benchmark, in percentage points of the current benchmark like the own-spending
component. This check is reported and does not change the pass rule above. sigma_v in 5.4 is the own-spending error
SD if at least 30 ACOs have complete values for this check, and otherwise the validation error SD.

**Pass:** Spearman correlation >= 0.80 and median absolute percentage error <= 5%, overall.
- If it passes and the slope is within [0.9, 1.1]: the approximation is used as is.
- If it passes and the slope is outside [0.9, 1.1]: the approximate new benchmark is calibrated with the validation
  regression (actual = intercept + slope x approximate) before computing the gain and its components: the
  intercept is assigned to the own-spending component and both components are multiplied by the slope, so they still
  add to the gain; the regional pull is unchanged.
- If it fails: H2a and the own-spending predictor in H3 are reported as exploratory with the validation result; H2b
  and H3 without the own-spending predictor remain confirmatory, since the regional pull does not use the
  approximation of the rebased benchmark. If the county-weighted regional spending itself cannot be checked (it has no
  published counterpart), this is stated as a limitation.

## 5. Analysis plan

**Approach:** every confirmatory estimate is Bayesian; significance is measured by resampling. Each confirmatory quantity is
summarized by its posterior mean, 95% equal-tailed credible interval, and posterior probability of a positive value.
For the group comparisons (H1, H2a, H2b) its **significance** is a stratified permutation test of the posterior mean: early-renewer labels are shuffled within
cohort (predictors fixed), the same estimation procedure is rerun on each shuffled dataset, and the two-sided p-value is
(1 + number of shuffles with |posterior mean| >= |observed|) / (1 + number of shuffles), with 10,000 shuffles for every
test; the core predictors of H3 use direct simulation instead (5.4). **The resampling p-value decides** (section 7); when it and the credible interval disagree, both are reported
and the disagreement is noted. Seeds are fixed in code and recorded in the output.

### 5.1 H1: savings rate (descriptive)
Difference in mean PY2020 savings rate, early renewers minus stayers, computed within each cohort and averaged with
weights proportional to the number of early renewers in each cohort. **Estimate:** Bayesian bootstrap (Rubin 1981):
in each of 10,000 draws, Dirichlet(1, ..., 1) weights are drawn over the ACOs in each cohort-by-group cell, giving
weighted cell means and the weighted difference above; the draws form the posterior. Under the Bayesian bootstrap the
posterior mean of this difference equals the observed difference in means, so each shuffle in the permutation test
recomputes that difference directly. **Significance:** as above.

### 5.2 H2b and H2a: regional pull and own-spending component
Same estimate and significance as 5.1, applied separately to the regional pull (H2b, primary) and the own-spending
component (H2a, secondary). Error in the approximation adds noise to the own-spending component as an outcome here but
does not bias a difference in means, so no measurement-error model is used in H2a. The total expected gain and the
regional component (4.3 step 5) are reported alongside, descriptively.

### 5.3 Covariate-adjusted estimates (reported, not used for decisions)
Bayesian linear regression (PyMC, MCMC) of each H1, H2a and H2b variable, standardized over the compared ACOs, on an
early-renewer indicator and a 2020-01-01 cohort indicator (both 0/1): Student-t errors, Normal(0, 1) on the intercept
and coefficients, Exponential(1) on the scale, Gamma(2, 0.1) on the degrees of freedom; same sampler settings,
convergence checks and single rerun as 5.4. Reported: the early-renewer coefficient's posterior mean and 95% interval,
in SD units and in the variable's units.

### 5.4 H3: Bayesian decision model (BASIC-track ACOs)
**Sample:** ACOs in the BASIC track in PY2021 (27 early renewers; the 2 early renewers already in ENHANCED in PY2021,
and stayers in ENHANCED, are excluded because they could not be moving to ENHANCED). ACOs missing any predictor are
excluded and counted (section 3).

**Model:** logistic regression of early renewal (1 = early renewer, 0 = stayer) on exactly these predictors:
- *Core, with predicted directions:* regional pull (+), own-spending component (+), higher BASIC level in PY2021
  (BASIC C-E vs A-B) (+).
- *Adjustment, estimated with no predicted direction:* cohort (2020-01-01 vs 2019-07-01), log assigned beneficiaries
  (`N_AB`, PY2020), revenue category (high vs low revenue), assignment method (prospective vs retrospective), and later
  agreement (agreement period number >= 2 in PY2021 vs 1).

Continuous predictors are centered and divided by 2 standard deviations, binary predictors are centered (Gelman 2008),
so each coefficient is a log-odds difference per 2 SD or per category. **Priors:** Normal(0, 1) on each coefficient
(about 95% of prior odds ratios between 1/7 and 7); Normal(-2.2, 1) on the intercept, which, with centered
predictors, is the log-odds of early renewal at average predictor values, centered at a 10% share (29 of 306 compared
ACOs renewed early, known from the enrollment data). With 27 events and 9 parameters
the priors, not the data alone, keep the estimates stable, so prior sensitivity is reported (below).

**Measurement error in the own-spending component:** if the validation (4.4) passes, the own-spending component enters
as a latent true value: observed = true + error, error ~ Normal(0, sigma_v), with sigma_v fixed as stated in 4.4
(the own-spending error SD from the step-1 check); true values ~ Normal(mu, tau), mu ~ Normal(0, 10), tau ~ HalfNormal(10) (percentage points). The latent value
is scaled with the observed variable's mean and 2 SD, and the latent values use a non-centered parameterization.
If the step-1 check falls back to the validation error SD (4.4), that SD covers the whole approximate benchmark, so it
treats regional-adjustment error as part of own-spending error; the write-up says so. If the validation fails, the own-spending predictor is dropped
(section 7, rule 6).

**Fitting:** PyMC (version pinned in `uv.lock`), NUTS, 4 chains of 2,000 tuning and 2,000 retained draws,
target acceptance 0.95, seed fixed in code and recorded; every refit below has its own seed from a fixed seed
sequence, so results do not depend on the number of parallel processes. BASIC-track ACOs with no recorded BASIC level
are excluded and counted. **Convergence:** R-hat <= 1.01 and bulk and tail effective
sample size >= 400 for every coefficient, and no divergent transitions. If not met, the model is rerun once with 4,000
retained draws and target acceptance 0.99; if still not met, the Bayesian results are reported as not converged and the
Firth model (5.5, item 5), with the same direct-simulation test of its core coefficients (10,000 simulations),
decides H3 as a fallback; that model drops the adjustment factors and the measurement-error
layer, so it tests the core predictions in a different model, and the write-up says so.

**Significance (core predictors only): direct simulation under the reduced model.** Shuffling the labels would test
the joint null that no predictor matters, not that one predictor does not matter given the others, so each core
predictor k is tested separately (a parametric bootstrap):
1. Fit the model without predictor k (same priors and settings; the measurement-error layer is kept unless k is the
   own-spending component).
2. 10,000 times: pick a posterior draw of that reduced model at random (with replacement), simulate an early-renewal
   outcome for every ACO from it, refit the full model to the simulated outcomes, and record the posterior mean of
   coefficient k.
3. Two-sided p = (1 + number of simulations with |posterior mean| >= |observed|) / (1 + 10,000).

Refits in step 2 use 2 chains of 1,000 tuning and 1,000 retained draws, and the observed posterior mean in step 3 is
computed with the same reduced settings on the real data; the full-settings fit above is the reported estimate. Every
refit's statistic is included whether or not it passes the convergence checks, and the share failing them is
reported. A core prediction is supported if p < 0.05 with the posterior mean in the predicted direction, contradicted
if p < 0.05 in the opposite direction, and undetermined otherwise. **Overall test (reported, not used for decisions):**
early-renewer labels shuffled within cohort, 10,000 refits, statistic = the largest absolute posterior mean among the
three core coefficients. Adjustment factors are reported as posterior mean, 95% interval and
P(coefficient > 0), with no test and no claim made.

**Also reported:** prior predictive distribution of the early-renewal share; posterior predictive check (observed
number of early renewers against the 95% interval of replicated counts, and observed vs predicted rates by decile of
predicted probability); the same model with Student-t(3, 0, 2.5) priors on the coefficients, with any core conclusion
that differs between the two priors flagged in the write-up.

### 5.5 Robustness (all reported)
Each item is reported as estimates: for H1, H2a and H2b the Bayesian bootstrap posterior and the stratified permutation
p-value (as in 5.1, 10,000 resamples); for H3 the posterior summaries of the 5.4 model (means and 95% intervals,
full settings, same convergence checks and rerun), without the direct-simulation test, which is run only for the
confirmatory model (5.4) and the Firth model (item 5). Robustness results do not change the section 7 decisions.
1. H1, H2a and H2b with PY2021 track/level (indicators for BASIC C-E and ENHANCED; BASIC A-B reference) and
   standardized log assigned beneficiaries (`N_AB`, PY2020) added to the 5.3 regressions.
2. H1, H2a and H2b as differences in medians (Bayesian bootstrap for the interval; the permutation test uses the
   observed difference in medians).
3. 2020-01-01 cohort only: H1, H2a and H2b, and H3 with the cohort predictor dropped.
4. H1 for the PY2021 savings rate.
5. H3 as a Firth-penalized logistic regression (`firthmodels`, version pinned in `uv.lock`) with the three core
   predictors and cohort only (about 7 events per parameter), own-spending component at its observed value;
   profile-likelihood 95% intervals and the direct-simulation test of 5.4 (10,000 simulations). Its complete-case
   sample uses only these predictors; if the validation fails, the own-spending predictor is dropped here too (section
   7, rule 6). Always run; it also serves as the convergence fallback of 5.4.
6. H2a and H3 using only BY2-BY3 (PY2020-PY2021) in step 1 of 4.3, with the main validation's calibration and
   sigma_v (not re-validated).
7. The Bayesian H3 model with the own-spending component at its observed value (no measurement-error model).
8. Complete cases: H2a, H3, the total gain and the regional component without the ACOs imputed under section 3.
9. H2b and H3 with the regional pull computed from unadjusted county spending (no risk standardization or case-mix
   adjustment), to show how much the case-mix adjustment matters.

### 5.6 Exploratory and descriptive (labeled as such in the write-up)
Exploratory analyses use the same estimators as above (Bayesian bootstrap and permutation p for group comparisons;
H3 posterior summaries only).
- Census region (4 levels: the region with the largest share of the ACO's 2021 assigned person-years, from
  `State_Name` in the county assignment file) added to the decision model as 3 centered indicators with Normal(0, 1)
  priors, Northeast as the reference; ACOs with no region (territories) are excluded from this model and counted.
- Leavers (28): PY2020 savings rate, regional pull and both gain components, in the same tables.
- The 2 early renewers already in ENHANCED in PY2021, whose renewal could not change their sharing rate: savings rate,
  regional pull and both gain components, reported individually against the stayer distribution.
- Regional pull weighted by the phase-in weight w, and the capped regional component, in place of the regional pull in
  H2b and H3.
- Who renewed early: cohort, prior track and level, new track (from enrollment data, already seen).
- Balance: share of beneficiaries aged 85+ (`N_Ben_Age_85plus` / sum of the `N_Ben_Age_*` bins) and share female
  (`N_Ben_Female` / (`N_Ben_Female` + `N_Ben_Male`)), PY2020; means by group.
- Per-capita spending by agreement year for 5-year agreements, labeled with benchmark-year status, with the caveat
  that benchmark-year status and tenure cannot be separated: agreements starting 2020-01-01, 2021-01-01 and
  2022-01-01, `Per_Capita_Exp_TOTAL_PY` from the PY2020-PY2024 results files (ACO and start date from
  `Current_Start_Date` in each file), agreement year = performance year - start year + 1; agreement years 3-5 are the
  scheduled benchmark years of the next agreement. Mean and ACO count by start year and agreement year; early renewers
  out of a 2020 agreement are shown separately. This table reads the full PY2022 results file, so it is computed only after the
  confirmatory results (5.1-5.4) have been written.

## 6. Power analysis (run after registration, before any confirmatory estimate)
Minimum detectable difference at 80% power, two-sided alpha = 0.05, for 29 vs 277 ACOs: MDE = 2.80 x SD x
sqrt(1/29 + 1/277), about 0.55 SD of the variable, with the group sizes as analyzed. For H1 the SD is the mean of the
three yearly cross-ACO standard deviations of `Sav_rate` in PY2016-PY2018 (years that play no part in the tests), and
the MDE is confirmed by simulating the stratified permutation test of 5.1 (which, for the Bayesian bootstrap, is a
permutation test of the difference in means) on 1,000 normal datasets with 999 permutations each. For H2a and H2b
the SD is not available before the variables are built; their MDEs are reported in SD units and, after validation,
in percentage points using the SD among stayers. For H3, with the actual predictor values, outcomes are simulated
with one core coefficient set to 0.5 (log-odds per 2 SD or per category) and all others 0, the intercept set to match
the observed early-renewal share, 500 datasets per core predictor, each fit with the reduced settings of 5.4;
reported: the share of datasets in which the 95%
credible interval excludes zero in the predicted direction, as an approximation of the direct-simulation test's
power (running 10,000 MCMC refits per simulated dataset is not feasible), and the median interval width. Results are committed before any confirmatory estimate is computed.

## 7. Decision rules (fixed before seeing results)
1. **H2b (primary):** p < 0.05 and positive: "early renewers' regions spent more relative to their current
   benchmarks, evidence for the reset motive beyond past savings". p < 0.05 and negative: "their regions spent less
   relative to their benchmarks, contrary to the reset motive". Otherwise: "no detectable difference", with the 95% credible interval and the MDE reported.
2. **H2a (secondary):** same wording for the own-spending component. Because H2a is close to H1 restated, it is not
   counted as separate evidence for the reset motive.
3. **H1 (descriptive):** the sign and size of the savings-rate difference are reported as context; no motive is
   attributed to the sign.
4. **H3:** each core predictor's direction is supported, contradicted, or undetermined by its direct-simulation
   p-value (5.4); adjustment factors are estimates only.
5. **p-values** in rules 1-4 are two-sided resampling p-values with 10,000 resamples: stratified permutation for H1,
   H2a and H2b (section 5), direct simulation under the reduced model for H3 (5.4).
6. **If the approximation fails validation (4.4):** H2a and the own-spending predictor are exploratory; H2b stands,
   and H3 is refit without the own-spending predictor, with its other rules unchanged.
7. Every result describes who chose to reset and why, not the effect of resetting. No test here can rule the
   sharing-rate motive in or out. Results are reported whatever they show.

## 8. Deviations
Any change after registration is recorded in `DEVIATIONS.md` (date, what changed, why); the write-up separates
deviations from registered analyses.

## 9. Registration record
Kept in `REGISTRATION.md` (not here, so this file's hash does not change): the OSF Registries link, the OSF timestamp,
and the sha256 of this file exactly as registered. The registration is made public immediately, with no embargo.
The analysis code (`ratchet/`, `tests/`, tested on synthetic data before registration) is attached to the
registration as a zip of this directory at the registered git commit; `REGISTRATION.md` records the commit and the
zip's sha256. Code added after registration to implement analyses not yet coded at registration (listed in the
directory's README) and any change to registered code are recorded in `DEVIATIONS.md` with the commit.
