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
entry-A/B sample is 250 ACOs. Status in the scheduled year and after (enrollment files PY2019-PY2026):

| G | ACOs | two-sided at G | at G+1 | at G+2 | exited by G+2 |
|---|---|---|---|---|---|
| 2021 | 138 | 19 (14%) | 37 (27%) | 38 (28%) | 47 (34%) |
| 2022 | 22 | 3 (14%) | 5 (23%) | 2 (9%) | 14 (64%) |
| 2023 | 76 | 9 (12%) | 5 (7%) | 4 (5%)* | 29 (38%)* |
| 2024 | 10 | 1 (10%) | 1 (10%)* | 2 (20%)* | 6 (60%)* |
| 2025 | 4 | 1 (25%)* | 1 (25%)* | - | - |

\* After PY2024: no outcome data exist for these years.

## 3. Implications

- Take-up of the default was low (about 10-28% two-sided in the scheduled years), so an intent-to-treat estimate of
  the default on spending is diluted by roughly 4-7x, and an instrumental-variables estimate has a weak first stage.
- ACOs that did take on two-sided risk chose to, so as-treated comparisons are confounded by self-selection.
- Exits were common (a third or more by G+2). Because exit counts were computed here, **program exit can no longer be
  a blind pre-registered outcome**; any registered plan must disclose this table and treat exit as descriptive.
- Outcome files (Performance Year Financial and Quality Results) have still not been opened.
