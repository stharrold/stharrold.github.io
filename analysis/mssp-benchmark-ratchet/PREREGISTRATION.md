# Pre-registration: Why did Medicare ACOs reset their benchmarks early?

**Status:** DRAFT v0.3 for author review. Not yet registered. Once registered on OSF Registries, this file is frozen:
the registration link, OSF timestamp, and this file's sha256 go in `REGISTRATION.md`, and any later change goes in
`DEVIATIONS.md`. Issue #73. Supersedes drafts v0.1 (a downside-risk question dropped at the design stage) and v0.2
(a single-test version of this plan); see `DESIGN-NOTES.md`.

**Author:** Samuel Harrold. **Drafted:** 2026-10-22.

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

### 1.3 Hypotheses (confirmatory)
Two motives make **opposite** predictions about an early renewer's prior performance:
- **Reset motive (ratchet):** renew when a reset would raise the benchmark, i.e. when spending is running high
  relative to the current benchmark, so **lower** prior savings rates.
- **Sharing-rate motive:** renew to enter ENHANCED and keep 75% of expected savings, i.e. when savings are expected to
  be large, so **higher** prior savings rates.

- **H1 (primary):** Early renewers' PY2020 savings rate differs from stayers'. Two-sided. A negative difference is
  read as the reset motive dominating, a positive one as the sharing-rate motive dominating (section 7).
- **H2 (primary explanatory):** Early renewers had a larger **expected benchmark gain from resetting** (section 4.3)
  than stayers. Predicted sign: positive.
- **H3 (decision model):** In a model of the renewal decision (section 5.4), the probability of renewing early rises
  with the expected benchmark gain (+), with already being at a higher risk level in PY2021 (+, ENHANCED is a smaller
  step), and with ACO size (+, larger ACOs absorb two-sided risk more easily).

Secondary: H1 repeated for the PY2021 savings rate (the year of the decision). Exploratory: section 5.6.

### 1.4 What this is and is not
An analysis of **who chose to reset and why**, not of the causal effect of renewing. Associations with pre-decision
characteristics are interpreted as evidence about motives, not as effects. The question "does spending change once an
ACO's years start counting toward its next benchmark?" is not identifiable in these data (benchmark-year status is
collinear with agreement tenure; `DESIGN-NOTES.md` 4.4) and is reported only descriptively. In the enrollment files no
stayer moved to ENHANCED, and 26 of the 27 early renewers that were in BASIC in PY2021 entered ENHANCED, so the reset
and sharing-rate motives are bundled in one choice; H1's sign and H2 are how they are told apart.

## 2. Data

### 2.1 Sources
CMS Medicare Shared Savings Program public use files (data.cms.gov, public data only):
- **Performance Year Financial and Quality Results:** PY2019 (July-December period), PY2020, PY2021 (outcomes and
  benchmark inputs); PY2022 (validation of the benchmark approximation, section 4.4); PY2016-PY2018 (power analysis
  only).
- **Accountable Care Organizations** enrollment files, PY2021 and PY2022 (groups, risk levels).
- **County-level Aggregate Expenditure and Risk Score Data on Assignable Beneficiaries**, calendar years 2019, 2020,
  2021, the versions published for 2022-2023 starters (`FFS_Data_for_SSP_CRB_PUF_<year>_01_01_Cal_Year_Assignable_
  2022_2023_Starters.csv`) (regional spending).
- **Number of ACO Assigned Beneficiaries by County**, 2021 (each ACO's regional service area in BY3).

Exact files, sizes, sha256 hashes and URLs: `data-snapshot.tsv` (downloaded 2026-10-22). The manifest also lists files
not used here, retained from the design stage. The pipeline verifies every hash before reading.

### 2.2 What the author has and has not seen (data already exist)
The data are public and were downloaded before registration solely to record hashes. Before registration the author
used: the CMS data dictionaries, the regulation (42 CFR 425.20, 425.200, 425.600, 425.601, 425.603), and the
**enrollment** files, from which the groups below, risk levels, take-up of an earlier candidate design, and program
exits were counted (`DESIGN-NOTES.md`). **No values from the results files or the county-level files (spending,
savings, benchmarks, quality, regional expenditures) have been viewed.** The hypotheses were formed from the
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
`ACO_ID`. An ACO missing a variable needed for an analysis (including suppressed values) is excluded from that analysis
and counted; if more than 10% of either compared group is excluded from the primary analysis, this is reported as a
limitation.

## 4. Variables

### 4.1 Outcomes and characteristics from the results files
- `Sav_rate` (PY2020 primary, PY2021 secondary): total benchmark expenditures minus assigned-beneficiary expenditures,
  as a percent of total benchmark expenditures. CMS's final PY2020 results reached ACOs around autumn 2021, during the
  application cycle for 2022 agreements; ACOs also had their own interim data.
- Size: `N_AB` (assigned beneficiaries), PY2020.
- In PY2020 and PY2021 all U.S. counties were treated as affected by an extreme and uncontrollable circumstance
  (COVID-19), which reduces shared losses but not the savings-rate calculation.

### 4.2 Characteristics from the enrollment files
Cohort (2019-07-01, 2020-01-01); PY2021 risk level, coded **high** (BASIC C-E or ENHANCED) or **low** (BASIC A-B);
revenue category (high/low revenue), assignment method (prospective/retrospective), agreement period number.

### 4.3 Expected benchmark gain from resetting (constructed)
An approximation of how much a January 1, 2022 reset would have changed the ACO's benchmark, built from public data
following 42 CFR 425.601 as in force on 2022-01-01. For each ACO:

1. **Rebased historical benchmark, per enrollment type** e in {ESRD, disabled, aged/dual, aged/non-dual}: the equally
   weighted mean (renewing ACO, 425.601(e)(2)(i)) of the ACO's per-capita expenditures for BY1-BY3 = PY2019-PY2021
   (`Per_Capita_Exp_ALL_<e>_PY`, annualized in the files). For PY2019 the ACO's record in the PY2019 results file is
   used (12-month performance year or July-December period, whichever exists for that `ACO_ID`; never the
   January-June "2019A" file); if the ACO has no
   PY2019 record, BY1 is omitted and the mean uses BY2-BY3. BY1 and BY2 are
   trended to BY3 (2021) dollars by the growth in regional per-capita expenditure for type e between the
   benchmark year and 2021. The national-regional blend in 425.601(a)(5)(iv) is approximated by regional growth only,
   because the ACO's share of assignable beneficiaries is not separately published; this simplification is fixed here.
2. **Regional service area spending, per type**, for BY3 = 2021: the mean of county per-capita expenditures for
   assignable beneficiaries of type e (county-level file, 2022-2023 starters version), weighted by the ACO's assigned
   beneficiaries by county in 2021.
3. **Regional adjustment, per type:** w x (regional - rebased), where w follows 425.601(f): the phase-in step is set by
   the number of times the ACO's benchmark has already been regionally adjusted, approximated by agreement period
   number (first agreement under the regional method = step 1, and so on); w = 35%/50%/50%/50% at steps 1-4+ if the
   ACO's weighted spending is below its region and 15%/25%/35%/50% if above (425.601(f)(5)). Each type's adjustment is
   capped at +/-5% of the national per-capita expenditure for that type in 2021, approximated by the assignable-
   beneficiary-weighted national mean in the county file.
4. **Approximate new benchmark** = sum over types of (rebased + adjustment) x the ACO's PY2021 person-year share of
   that type (`N_AB_Year_<e>_PY`).
5. **Expected gain (%)** = 100 x (approximate new benchmark - current benchmark) / current benchmark, where current
   benchmark = the PY2021 per-capita updated benchmark (`UpdatedBnchmk`, already per capita in the files).

Steps that cannot be reproduced exactly from public data (risk adjustment and truncation details, assignment
differences between performance and benchmark years, the national-regional growth blend) are approximated as stated;
section 4.4 measures how good the approximation is before it is used.

### 4.4 Validation of the approximation (run before H2 and H3 are estimated)
Apply steps 1-4 to every **regular renewer** with a January 1, 2022 agreement (agreement period number >= 2 in PY2022,
benchmark years 2019-2021, not one of the 29 early renewers) and compare the approximate new benchmark with the actual
per-capita historical benchmark reported for PY2022 (`HistBnchmk`, already per capita). Early renewers are excluded so
that validation does not reveal their actual reset gain before H2 is estimated. **Pass:** Spearman correlation >= 0.80 and median absolute error <= 5%. If the
approximation fails, H2 and H3 are reported as exploratory, with the validation result, and conclusions rest on H1.

## 5. Analysis plan

### 5.1 H1: savings rate
Difference in mean PY2020 savings rate, early renewers minus stayers, computed within each cohort and averaged with
weights proportional to the number of early renewers in each cohort. **Test:** stratified permutation test
(early-renewer labels shuffled within cohort), 100,000 permutations, two-sided p. **Interval:** 95% interval by
inverting the permutation test over a grid of location shifts in steps of 0.01 percentage points. Seed fixed in code
and recorded in the output.

### 5.2 H2: expected benchmark gain
Same estimator and test as 5.1 with expected gain (section 4.3) as the variable.

### 5.3 Comparison estimates (reported, not used for decisions)
OLS of each H1/H2 variable on an early-renewer indicator and a cohort indicator, HC2 robust standard errors.

### 5.4 H3: decision model
Firth-penalized logistic regression (Python package `firthmodels`, version pinned in `uv.lock`) of early renewal
(1 = early renewer, 0 = stayer) on exactly these predictors: expected gain (per 1 percentage point), high PY2021 risk
level (indicator), log `N_AB` (PY2020), and cohort (indicator, control). The number of predictors is limited by the
29 early renewers. Reported: coefficients, profile-likelihood 95% intervals, and a permutation p-value for the expected
gain coefficient (labels shuffled within cohort, 10,000 permutations). Each H3 prediction is supported if its 95%
interval excludes zero in the predicted direction.

### 5.5 Robustness (all reported)
1. H1 and H2 with PY2021 risk level and log assigned beneficiaries added to the 5.3 regressions.
2. Stratified rank test (van Elteren) for H1 and H2.
3. 2020-01-01 cohort only.
4. H1 for the PY2021 savings rate.
5. H3 with expected gain replaced by the PY2020 savings rate.
6. H2 and H3 using only BY2-BY3 (PY2020-PY2021) in step 1 of 4.3.

### 5.6 Exploratory and descriptive (labeled as such in the write-up)
- Revenue category, assignment method, agreement period number, and census division added to the decision model, one
  at a time.
- Decomposition of expected gain into the own-spending part (step 1 vs. current benchmark) and the regional part
  (step 3).
- Leavers (28): PY2020 savings rate and expected gain, in the same tables.
- Who renewed early: cohort, prior risk level, new track (from enrollment data, already seen).
- Balance: share of beneficiaries aged 85+ and share female, PY2020.
- Per-capita spending by agreement year for 5-year agreements, labeled with benchmark-year status, with the caveat
  that benchmark-year status and tenure cannot be separated.

## 6. Power analysis (run after registration, before any confirmatory estimate)
Minimum detectable difference at 80% power, two-sided alpha = 0.05, for 29 vs 277 ACOs, using the cross-ACO standard
deviation of `Sav_rate` in PY2016-PY2018 (years that play no part in the tests): MDE = 2.80 x SD x
sqrt(1/29 + 1/277), about 0.55 SD, confirmed by simulating the stratified permutation test. For H2 the SD of expected
gain is not available before the validation step; its MDE is reported in SD units and, after validation, in percentage
points. Results are committed before any confirmatory estimate is computed.

## 7. Decision rules (fixed before seeing results)
1. **H1:** p < 0.05 and negative: "early renewers had lower savings rates before renewing, consistent with the reset
   motive dominating". p < 0.05 and positive: "higher savings rates, consistent with the sharing-rate motive
   dominating". Otherwise: "no detectable difference; differences larger than the MDE are ruled out".
2. **H2:** p < 0.05 and positive: "early renewers stood to gain more from a reset". p < 0.05 and negative: "they
   stood to gain less, contrary to the ratchet". Otherwise: no detectable difference, with the MDE. Applies only if
   the approximation passes validation (4.4).
3. **Combined reading:** H1 negative and H2 positive: evidence for the reset motive. H1 positive and H2 not positive:
   evidence for the sharing-rate motive. Other combinations are reported as mixed and described, not resolved.
4. **H3:** each predictor's direction is supported, contradicted, or undetermined by its 95% interval (5.4).
5. Every result describes who chose to reset and why, not the effect of resetting. Results are reported whatever
   they show.

## 8. Deviations
Any change after registration is recorded in `DEVIATIONS.md` (date, what changed, why); the write-up separates
deviations from registered analyses.

## 9. Registration record
Kept in `REGISTRATION.md` (not here, so this file's hash does not change): the OSF Registries link, the OSF timestamp,
and the sha256 of this file exactly as registered.
