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
