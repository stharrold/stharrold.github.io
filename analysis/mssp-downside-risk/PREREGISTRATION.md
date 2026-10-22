# Pre-registration: Does downside financial risk lower spending in Medicare ACOs?

**Status:** DRAFT v0.1 for author review. Not yet registered. Once registered on OSF Registries, this file is frozen:
the registration link, OSF timestamp, and this file's sha256 go in `REGISTRATION.md`, and any later change goes in
`DEVIATIONS.md`. Issue #73.

**Author:** Samuel Harrold. **Drafted:** 2026-10-22.

## 1. Study information

### 1.1 Research question
When an Accountable Care Organization (ACO) in the Medicare Shared Savings Program moves from one-sided risk (it can
share savings but not losses) to two-sided risk (it also repays a share of losses), does Medicare spending per
assigned beneficiary fall?

### 1.2 Why this design
Under the "Pathways to Success" rules, ACOs that began a BASIC-track agreement period between July 1, 2019 and
December 31, 2023 were advanced automatically one level each performance year, from one-sided Levels A-B into
two-sided Levels C-E, on a schedule set by the agreement start date and entry level rather than by performance
(42 CFR 425.600(a)(4)(i)(A)-(B)). That rule-driven timing is the source of identification. Agreement periods beginning
on or after January 1, 2024 allow inexperienced ACOs to remain one-sided for the whole period
(425.600(a)(4)(i)(C)), so those cohorts are not used to define treatment timing.

### 1.3 Hypotheses
- **H1 (primary):** The scheduled move to two-sided risk lowers log per-capita Medicare expenditure for assigned
  beneficiaries, averaged over event years 0-2 (intent-to-treat).
- **H2 (secondary):** The scheduled move lowers spending relative to the ACO's benchmark (higher savings rate).
- **H3 (secondary, mechanism/threat):** The scheduled move raises average CMS-HCC risk scores (coding response).
- **H4 (secondary):** The scheduled move raises the probability that an ACO leaves the program (attrition).
- Exploratory: readmissions per 1,000, skilled nursing facility payment per stay, quality score.

## 2. Design

Observational ACO-by-performance-year panel, PY2013-PY2024, with staggered treatment adoption. The estimand of
interest is the average treatment effect on the treated by event time, ATT(e), for ACOs in the glide-path cohorts,
with not-yet-treated glide-path ACOs as the comparison group.

## 3. Data

### 3.1 Sources
CMS Medicare Shared Savings Program public use files from data.cms.gov (public data only):
- **Performance Year Financial and Quality Results**, PY2013-PY2024 (outcomes, risk model, track, agreement dates).
- **Accountable Care Organizations**, PY2014-PY2026 (agreement start dates and tracks, used to cross-check treatment
  assignment).

The exact files, sizes, sha256 hashes, and download URLs are in `data-snapshot.tsv` (downloaded 2026-10-22). Analysis
uses only those files; the pipeline verifies every hash before reading.

### 3.2 What the author has and has not seen (data already exist)
The data are public and were downloaded before registration, solely to record their hashes. Before registration the
author consulted: the data.cms.gov catalog, the CMS data dictionaries (variable names and definitions), and the
regulation text (42 CFR 425.600). **No outcome values, distributions, or summary statistics from these files were
viewed.** The author is aware of published research on MSSP savings in general.

### 3.3 Known data issues, decided in advance
- **PY2019 has two performance periods** (January-June and July-December, the start of the new rules). Event time
  uses the July-December 2019 period as PY2019; the January-June 2019 period is dropped.
- **Track coding changes across years** (0/1 flags in earlier files, a single `Current_Track` field in later files).
  Treatment status is harmonized to one rule: two-sided if `Risk_Model` is "Two-Sided", or, where `Risk_Model` is
  absent, if the ACO is in Track 2, Track 3, Track 1+, ENHANCED, or BASIC Levels C-E.
- **Suppressed cells:** values suppressed in the public files are treated as missing, never imputed.
- **ACO identity:** `ACO_ID` links an ACO across performance years and agreement periods.

## 4. Sample

- **Treated cohorts (primary):** ACOs whose agreement period started between 2019-07-01 and 2023-01-01 in the BASIC
  track at Level A or B (one-sided at entry). Excluded from the primary sample: ACOs entering already two-sided
  (Levels C-E or ENHANCED), and ACOs with a documented exception to automatic advancement (e.g. the low-revenue
  new-legal-entity exception in 425.600(a)(4)(i)(B)(2)(ii)), because their schedule is not rule-driven.
- **Comparison:** not-yet-treated ACOs from the same cohorts (later scheduled transition dates).
- **Years:** all available performance years PY2013-PY2024 for those ACOs, including years in earlier agreement
  periods (e.g. Track 1), so pre-periods can extend before 2019.
- **Minimum data:** an ACO enters the analysis if it has at least two observed pre-treatment years.

## 5. Variables

### 5.1 Treatment timing
- **Scheduled transition year G (primary, intent-to-treat):** the first performance year in which the default
  glide path places the ACO in Level C, computed from the agreement start date and the entry level recorded in the
  ACO's first performance year: entry at Level A reaches Level C in the agreement's third performance year; entry at
  Level B in its second; for agreement periods starting July 1, 2019, PY2020 repeats the 2019 level, so each step
  comes one performance year later (425.600(a)(4)(i)(B)(2)). The optional one-year extension in Level B is ignored
  when computing G.
- **Actual transition year (secondary, as-treated):** the first performance year in which the ACO is two-sided
  under the harmonized rule in 3.3.

### 5.2 Outcomes
- **Primary:** `log(Per_Capita_Exp_TOTAL_PY)`, total per-capita expenditure for assigned beneficiaries.
- **Secondary:** savings rate `Sav_rate`; average CMS-HCC risk score, the person-year-weighted mean of
  `CMS_HCC_RiskScore_{ESRD,DIS,AGDU,AGND}_PY` using `N_AB_Year_{ESRD,DIS,AGED_Dual,AGED_NonDual}_PY`; program exit,
  =1 in the last year an ACO appears if it does not appear in the next performance year's file and its agreement
  had not ended.
- **Exploratory:** `readm_Rate_1000`, `SNF_PayperStay`, `QualScore`.
- Risk scores are an **outcome**, not a control, because coding intensity may itself respond to downside risk.

## 6. Analysis plan

### 6.1 Primary estimator
Callaway and Sant'Anna (2021) group-time ATT(g, t), with not-yet-treated ACOs as controls, no covariates, and a
universal base period (e = -1). Aggregated to an event study (e = -4 ... +2) and to the **primary estimate: the
average of ATT(e) over e = 0, 1, 2**. Inference: multiplier bootstrap, clustered by ACO, 999 draws, 95% intervals.
Software: Python package `csdid` (version pinned in `uv.lock` at the time of analysis), cross-checked with
`differences`.

### 6.2 Comparison estimators (reported alongside, not used for the decision)
- Two-way fixed effects event study with ACO and year fixed effects, standard errors clustered by ACO (`pyfixest`).
- Sun and Abraham (2021) interaction-weighted event study.

### 6.3 Pre-trend test
Joint Wald test that ATT(e) = 0 for e = -4, -3, -2 (primary estimator).

### 6.4 Placebo
Shift every ACO's scheduled transition year G two years earlier and re-estimate the primary specification using
only performance years before the true G. The expected effect is zero.

### 6.5 Robustness (all reported)
1. Exclude PY2020 (COVID-19 year).
2. As-treated timing (actual first two-sided year) instead of scheduled timing.
3. Balanced panel: ACOs observed through e = +2.
4. Doubly robust Callaway and Sant'Anna with pre-treatment covariates: number of assigned beneficiaries (log),
   revenue category (`Rev_Exp_Cat`), agreement period number, state.
5. Honest DiD sensitivity (Rambachan and Roth 2023), relative-magnitudes bound with Mbar = 1, for the primary
   estimate.

### 6.6 Attrition
Report exit rates by cohort and event time, and the primary estimate on the balanced panel (robustness 3) next to
the main estimate.

### 6.7 Multiple outcomes
H1 is the single confirmatory test. H2-H4 are reported with Holm-adjusted p-values; exploratory outcomes are labeled
exploratory and not used for conclusions.

## 7. Power analysis (completed and committed before any treatment-effect estimate)
Using only PY2013-PY2018 (all years before the glide path existed), estimate the variance and serial correlation of
the primary outcome after removing ACO and year fixed effects. Simulate the actual cohort structure (numbers of ACOs
by scheduled transition year) under the primary estimator and report the minimum detectable effect (MDE) on the
primary estimate at 80% power and two-sided alpha = 0.05.

## 8. Decision rules (fixed before seeing results)
1. **Identification check.** If the pre-trend test has p < 0.05, or the placebo estimate's 95% interval excludes
   zero, the primary result is reported as "not credibly identified", and the honest DiD interval (robustness 5) is
   reported as the main finding.
2. **If identification checks pass:**
   - 95% interval of the primary estimate entirely below zero: "the scheduled move to downside risk lowered
     spending".
   - Entirely above zero: "it raised spending".
   - Otherwise: "no detectable effect; effects larger than the MDE in either direction are ruled out", stated with
     the MDE from section 7.
3. Results are reported whatever they show, including a null.

## 9. Deviations
Any change after registration is recorded in `DEVIATIONS.md` (date, what changed, why), and the write-up separates
deviations from the registered analyses.

## 10. Registration record
Kept in `REGISTRATION.md` (not here, so this file's hash doesn't change): the OSF Registries link, the OSF
timestamp, and the sha256 of this file exactly as registered.
