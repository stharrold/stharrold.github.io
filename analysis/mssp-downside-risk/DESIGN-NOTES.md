# Design notes (pre-registration stage)

Working notes from the design stage of #73, kept for the record. They use **enrollment data only** (the ACOs files:
agreement start dates, tracks, BASIC levels, low-revenue flags), never the outcome files. Computed 2026-10-22.

## 1. The glide path was a default, not a mandate

42 CFR 425.600(a)(4)(i)(B) (eCFR, current as of 2026-10-20) moves BASIC-track ACOs up one level each performance
year, but every scheduled step into two-sided risk had an opt-out:

- (B)(2)(iii): any ACO could freeze its level for PY2021.
- (B)(2)(iv): any ACO could freeze its level for PY2022.
- (B)(2)(vi): from PY2023, an ACO in Level A or B could remain there for the rest of the agreement period.
- (B)(2)(vii): the same for PY2024, for agreement periods that began January 1, 2023.
- (B)(2)(ii): new legal entities identified as low-revenue ACOs could stay one extra year in Level B.
- (B)(2)(i): agreement periods beginning July 1, 2019 repeat their entry level in PY2020.
- (B)(1)(ii): ACOs with prior Track 1 experience cannot enter at Level A (affects entry level only).

## 2. Cohorts and take-up of the default schedule

BASIC entrants by agreement start and entry level (first performance year of the agreement):

| Start | A | B | C | D | E | All |
|---|---|---|---|---|---|---|
| 2019-07-01 | 33 | 75 | 5 | 1 | 41 | 155 |
| 2020-01-01 | 22 | 67 | 11 | 0 | 28 | 128 |
| 2022-01-01 | 19 | 77 | 5 | 1 | 26 | 128 |
| 2023-01-01 | 11 | 1 | 1 | 0 | 11 | 24 |

No agreement periods started in 2021. Default first two-sided year G: entry A reaches Level C two levels later, entry
B one level later, with the PY2020 repeat for July 2019 starters. Excluding 55 new low-revenue legal entities, the
entry-A/B sample is 250 ACOs. Status in the scheduled year G and after, tracked by `aco_id` across all
enrollment files PY2019-PY2026. "New agreement" means the ACO re-entered or renewed early under a different agreement
start date; "left" means it appears in no later file.

| G | ACOs | k | two-sided, same agreement | one-sided, same agreement | new agreement (two-sided / one-sided) | left program |
|---|---|---|---|---|---|---|
| 2021 | 138 | 0 | 19 (14%) | 110 (80%) | 0 / 0 | 9 (7%) |
| | | 1 | 37 (27%) | 76 (55%) | 2 / 0 | 23 (17%) |
| | | 2 | 38 (28%) | 53 (38%) | 4 / 0 | 43 (31%) |
| 2022 | 22 | 0 | 3 (14%) | 13 (59%) | 2 / 0 | 4 (18%) |
| | | 1 | 5 (23%) | 6 (27%) | 3 / 0 | 8 (36%) |
| | | 2 | 2 (9%) | 6 (27%) | 6 / 0 | 8 (36%) |
| 2023 | 76 | 0 | 9 (12%) | 56 (74%) | 1 / 0 | 10 (13%) |
| | | 1 | 5 (7%) | 51 (67%) | 5 / 1 | 14 (18%) |
| | | 2* | 4 (5%) | 43 (57%) | 6 / 3 | 20 (26%) |
| 2024 | 10 | 0 | 1 (10%) | 3 (30%) | 4 / 0 | 2 (20%) |
| 2025* | 4 | 0 | 1 (25%) | 2 (50%) | 0 / 0 | 1 (25%) |

\* After PY2024: no outcome data exist for these years. An earlier version of this table keyed status by
(ACO, agreement start date) and so counted early renewals as exits; corrected here.

## 3. Implications

- Take-up of the default was low (about 10-28% two-sided in the scheduled years), so an intent-to-treat estimate of
  the default on spending is diluted by roughly 4-7x, and an instrumental-variables estimate has a weak first stage.
- ACOs that did take on two-sided risk chose to, so as-treated comparisons are confounded by self-selection.
- Leaving the program was common in the largest cohort (31% by G+2 for G = 2021); early renewal into a new agreement
  was rare there but common in the small 2022 cohort. Because these counts were computed here, **program exit and
  early renewal can no longer be blind pre-registered outcomes**; any registered plan must disclose this table and
  treat them as descriptive.
- Outcome files (Performance Year Financial and Quality Results) have still not been opened.

## 4. Decision (2026-10-22): switch #73 to benchmark rebasing

The author chose to replace the downside-risk question with the benchmark-rebasing ("ratchet") question and to do
it properly rather than within the original one-week time box. The directory will be renamed when the new plan is
drafted.

### 4.1 Rules (eCFR, current as of 2026-10-20)
- **Reset:** an ACO's benchmark is reset at the start of each subsequent agreement period from the three calendar
  years before that start (BY1-BY3); for renewing and re-entering ACOs the years are weighted equally
  (42 CFR 425.601(e), 425.603), versus 10/30/60% for initial agreements (425.601(a)(7)). A regional adjustment and,
  from 2024, a prior-savings adjustment soften the ratchet.
- **Default agreement terms** (425.200(b)): 2012 starts 3 years 9 months or 3 years 6 months; 2013-2018 starts
  3 years (optional extensions: 2016 starts to June 30, 2019; 2018 starts by 12 months to Dec 31, 2021; some
  2014-2015 Track 1 starts a fourth year); July 1, 2019 start 5 years 6 months; 2020+ starts 5 years.
- **Early renewal** (425.20 "renewing ACO" (2)): an ACO may terminate and immediately enter a new agreement period.
- **Implication:** under 3-year agreements every year is a benchmark year for the next agreement; under 5-year
  agreements years 1-2 are not and years 3-5 are. The ratchet predicts weaker savings effort once an ACO's years start
  counting toward its next benchmark.

### 4.2 Benchmark-year (BY) status from enrollment data
BY status for ACO i in year t uses the **default** next start date N (no optional extensions, intent-to-treat):
BY if N-3 <= t <= N-1. Built from the ACOs files PY2016-PY2026 (the PY2014-PY2015 files have no ACO ID or dates):
1,075 ACOs, 5,392 ACO-years. Year-to-year transitions:

| t-1 -> t | switch on (out -> BY) | stay out | switch off (BY -> out) | stay in BY |
|---|---|---|---|---|
| 2020->2021 | 0 | 334 | 142 | 1 |
| 2021->2022 | 277 | 139 | 1 | 0 |
| 2022->2023 | 0 | 187 | 8 | 223 |
| 2023->2024 | 137 | 77 | 34 | 163 |
| 2024->2025* | 28 | 136 | 145 | 112 |
| 2025->2026* | 66 | 241 | 10 | 121 |

\* PY2025 and PY2026 outcome files had not been published as of 2026-10-22, so analyses of these transitions are
fully prospective.

Switchers and stay-out controls by agreement start:
- 2021->2022: switch on = 2019-07-01 (159) and 2020-01-01 (118) cohorts; all 139 stay-outs are 2022-01-01 starts
  that were in years 1-2 of a 2019/2020 agreement in 2021, i.e. **early renewers**.
- 2023->2024: switch on = 2022-01-01 cohort (137); stay out = 2023-01-01 cohort in years 1->2 (40, clean) and
  2024-01-01 starts (37, early renewers).
- 2024->2025: switch on = 2023-01-01 cohort (28); stay out = 2024-01-01 cohort (108, clean) and 2025-01-01 starts (28).
- 2025->2026: switch on = 2024-01-01 cohort (66); stay out = 2025-01-01 (189) and 2026-01-01 (52) starts.

### 4.3 Design implications
- Treatment switches on and off, so a staggered-adoption estimator does not fit. The natural estimator is
  de Chaisemartin and D'Haultfoeuille (switchers vs. stayers with the same prior status, year by year). No maintained
  Python package exists (checked PyPI 2026-10-22); the reference implementation is the R package `DIDmultiplegtDYN`.
- Early renewal is a choice that also resets the benchmark, so early renewers are excluded as controls; the 2022
  early-renewal wave (about 140 ACOs) is itself consistent with ratchet behavior and is a descriptive finding.
- Clean contrasts in published data: 2023->2024 (137 vs 40). Prospective: 2024->2025 (28 vs 108) and 2025->2026.
- Outcome files have still not been opened.
