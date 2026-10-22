# Pre-registration: Did Medicare ACOs that reset their benchmark early have weaker savings?

**Status:** DRAFT v0.2 for author review. Not yet registered. Once registered on OSF Registries, this file is frozen:
the registration link, OSF timestamp, and this file's sha256 go in `REGISTRATION.md`, and any later change goes in
`DEVIATIONS.md`. Issue #73. Supersedes draft v0.1 (a downside-risk question dropped at the design stage; see
`DESIGN-NOTES.md`).

**Author:** Samuel Harrold. **Drafted:** 2026-10-22.

## 1. Study information

### 1.1 Background
In the Medicare Shared Savings Program, an ACO earns shared savings when its assigned beneficiaries' spending falls
below a benchmark. The benchmark is **reset at the start of each new agreement period** from the ACO's own spending in
the three preceding years (42 CFR 425.601(e)). This creates a "ratchet": the closer an ACO's recent spending is to or
above its benchmark, the more a reset helps it; the further below, the more a reset hurts. ACOs may end an agreement
early and immediately start a new one (a "renewing ACO", 42 CFR 425.20), which resets the benchmark early.

### 1.2 Research question
Among ACOs in agreement periods that began July 1, 2019 or January 1, 2020, did those that renewed early into a
January 1, 2022 agreement have lower savings rates before renewing than those that stayed in their agreement?

### 1.3 Hypothesis
- **H1 (primary):** Early renewers had a lower PY2020 savings rate than stayers (the ratchet predicts that ACOs reset
  when their spending is running high relative to their benchmark). Tested two-sided; the predicted sign is negative.
- **H2 (secondary):** The same difference holds for the PY2021 savings rate.
- Exploratory: the PY2019 (July-December) savings rate for the 2019 cohort; per-capita spending growth; quality score.

### 1.4 What this is and is not
A pre-registered test of a behavioral prediction (who chooses to reset), not an estimate of the causal effect of
renewing. The question "does spending change once an ACO's years start counting toward its next benchmark?" is not
identifiable in these data (benchmark-year status is collinear with agreement tenure; `DESIGN-NOTES.md` 4.4) and is
reported only descriptively, with that caveat.

The test also cannot separate two motives for renewing early. A BASIC-track ACO can enter the ENHANCED track (75%
sharing rate) only by starting a new agreement: in the enrollment files, no stayer moved to ENHANCED within its
agreement, while 26 of the 27 early renewers that were in BASIC in PY2021 entered ENHANCED in PY2022 (the other two
early renewers were already in ENHANCED). So a difference between groups may reflect resetting the benchmark, moving to
a higher sharing rate, or both. The two early renewers already in ENHANCED are the only resets without a track change;
they are reported individually and are too few to test.

## 2. Data

### 2.1 Sources
CMS Medicare Shared Savings Program public use files (data.cms.gov, public data only):
- **Performance Year Financial and Quality Results**, PY2019-PY2021 (outcomes).
- **Accountable Care Organizations** enrollment files, PY2021 and PY2022 (group assignment).

Exact files, sizes, sha256 hashes and URLs: `data-snapshot.tsv` (downloaded 2026-10-22). The manifest also lists files
not used here (PY2013-PY2024 results and PY2014-PY2026 enrollment files), retained from the design stage; PY2016-PY2018
results are used only for the power analysis (section 6). The pipeline verifies every hash before reading.

### 2.2 What the author has and has not seen (data already exist)
The data are public and were downloaded before registration solely to record hashes. Before registration the author
used: the CMS data dictionaries, the regulation (42 CFR 425.20, 425.200, 425.600, 425.601, 425.603), and the
**enrollment** files, from which the groups below, take-up of an earlier candidate design, and program exits were
counted (`DESIGN-NOTES.md`). The enrollment files show that 28 of the 29 early renewers entered the ENHANCED track.
**No values from the Performance Year Financial and Quality Results files (spending, savings, benchmarks, quality)
have been viewed.** The hypothesis was formed from the regulation and the existence of the early-renewal group, not
from outcomes. The author is aware of published research on MSSP savings in general.

## 3. Sample and groups

Base population: ACOs whose PY2021 enrollment record shows an agreement start of 2019-07-01 or 2020-01-01
(334 ACOs). Groups, from the PY2022 enrollment file:

| Group | 2019-07-01 cohort | 2020-01-01 cohort | All |
|---|---|---|---|
| **Early renewers:** 2022-01-01 agreement in PY2022 | 11 | 18 | 29 |
| **Stayers:** same agreement in PY2022 | 159 | 118 | 277 |
| Left after PY2021 (not in PY2022 file) | 19 | 9 | 28 |

**Why a 2022 start means early renewal:** agreements starting July 1, 2019 run 5 years 6 months and those starting
January 1, 2020 run 5 years (42 CFR 425.200(b)(4)(ii), (b)(5)), so both end December 31, 2024. An ACO from these cohorts
in a new agreement on January 1, 2022 therefore terminated its agreement early and renewed (42 CFR 425.20, "renewing
ACO" (2)).

Early renewers are compared with stayers. Leavers are reported descriptively. ACOs are linked across files by
`ACO_ID`. An ACO with a missing or suppressed primary outcome is excluded from that analysis and counted; if more than
10% of either compared group is excluded, this is reported as a limitation.

## 4. Variables
- **Primary outcome:** `Sav_rate`, PY2020: total benchmark expenditures minus assigned-beneficiary expenditures, as a
  percent of total benchmark expenditures. PY2020 is the last complete performance year before the renewal decision
  (agreements starting January 1, 2022 were applied for and executed during 2021). CMS's final PY2020 results reached
  ACOs around autumn 2021, during the application cycle; ACOs also had their own interim data.
- **Secondary outcome:** `Sav_rate`, PY2021, the year in which the renewal decision was made.
- **Exploratory:** `Sav_rate` for the July-December 2019 performance period (2019 cohort only); log change in
  `Per_Capita_Exp_TOTAL_PY` PY2020-PY2021; `QualScore` PY2021.
- **Stratifier:** agreement start cohort (2019-07-01, 2020-01-01).
- **Robustness covariates (PY2021 enrollment file):** risk model in PY2021 (BASIC A/B, BASIC C-E, ENHANCED); log
  number of assigned beneficiaries (`N_AB`, PY2020).
- Note: in PY2020 and PY2021 all U.S. counties were treated as affected by an extreme and uncontrollable circumstance
  (COVID-19), which reduces shared losses but not the savings-rate calculation.

## 5. Analysis plan

### 5.1 Primary estimate and test
Difference in mean PY2020 savings rate, early renewers minus stayers, computed within each cohort and averaged with
weights proportional to the number of early renewers in each cohort. **Test:** stratified permutation test,
reassigning early-renewer labels within cohort, 100,000 permutations, two-sided p-value. **Interval:** 95% interval by
inverting the permutation test over a grid of location shifts in steps of 0.01 percentage points. The random seed is fixed in the code and recorded in the output.

### 5.2 Comparison estimate (reported, not used for the decision)
OLS of PY2020 savings rate on an early-renewer indicator and a cohort indicator, HC2 robust standard errors.

### 5.3 Robustness (all reported)
1. Add PY2021 risk model and log assigned beneficiaries to the 5.2 regression.
2. Stratified rank test (van Elteren) instead of the mean difference.
3. 2020-01-01 cohort only (its PY2020 is the first full year of its agreement).
4. Secondary outcome PY2021 (H2) with the same method.

### 5.4 Balance and negative control
Early renewers vs stayers on share of beneficiaries aged 85+ and share female (PY2020): no prediction; reported to
show comparability. `QualScore` is exploratory, with no ratchet prediction.

### 5.5 Descriptive (not confirmatory)
- Who renewed early: cohort, prior risk level, new track (from enrollment data, already seen).
- Leavers (28 ACOs that left after PY2021): PY2020 savings rate reported in the same table as the two compared
  groups, as the third route out of an agreement.
- Per-capita spending by agreement year for 5-year agreements, labeled with benchmark-year status, with the explicit
  caveat that benchmark-year status and tenure cannot be separated.

## 6. Power analysis (run after registration, before the primary estimate)
Minimum detectable difference at 80% power, two-sided alpha = 0.05, for 29 vs 277 ACOs, using the cross-ACO standard
deviation of `Sav_rate` in PY2016-PY2018 (years that play no part in the test). Normal approximation:
MDE = 2.80 x SD x sqrt(1/29 + 1/277), about 0.55 SD, confirmed by simulating the stratified permutation test. Results
are committed before the primary estimate is computed.

## 7. Decision rules (fixed before seeing results)
1. Permutation p < 0.05 and estimate below zero: "early renewers had lower savings rates before renewing, as the
   ratchet predicts".
2. Permutation p < 0.05 and estimate above zero: "early renewers had higher savings rates, contrary to the ratchet
   prediction".
3. Otherwise: "no detectable difference; differences larger than the MDE are ruled out", stated with the MDE from
   section 6.
4. In every case, the result describes who chose to reset, not the effect of resetting.
5. Results are reported whatever they show.

## 8. Deviations
Any change after registration is recorded in `DEVIATIONS.md` (date, what changed, why); the write-up separates
deviations from registered analyses.

## 9. Registration record
Kept in `REGISTRATION.md` (not here, so this file's hash does not change): the OSF Registries link, the OSF timestamp,
and the sha256 of this file exactly as registered.
