# Critical assessment: "Why did Medicare ACOs reset their benchmarks early? A pre-registered study"

**Date:** 2026-10-27
**Reviewed:** `content/20261026-preregistered-mssp-early-renewal.md` at commit `2e116ce` (branch `src_feature_mssp_prereg`); registered plan `git show a4064f5:analysis/mssp-benchmark-ratchet/PREREGISTRATION.md`; `analysis/mssp-benchmark-ratchet/results/*.json`; `DEVIATIONS.md`, `BUILD-NOTES.md`, `DESIGN-NOTES.md`, `ratchet/run.py`, `ratchet/conventional.py`, `ratchet/validate.py`. Line numbers refer to the post.

## Verdict

**Publishable after minor fixes.** Minor means little effort, not little importance: several fixes change what a reader takes away. The analysis does not need to be rerun, and no registered verdict changes. Every number in the Results, Robustness, Exploratory and Power tables matches the JSON to rounding. The only number problems are the conventional test shown in the agreement table (M4), the MDE unit conversion (S5), the run time (S8), exclusion medians with no results file behind them (S9) and the 306/334 count (S10). The code at all six run commits is identical to `a4064f5` (the `git diff --stat` check in `DEVIATIONS.md` prints nothing for each one). The decision rules are applied as registered. The problems are in the summary and in reporting. The "In short" paragraph uses effect language for H4 that rule 5 withholds. It frames H2b as support for "the reset motive" without saying that, by the post's own approximation, a reset would on average have *lowered* early renewers' benchmarks. One registered reporting item (H4 attrition by group and year) is missing, and that attrition is badly uneven between the groups. The agreement table shows a different conventional test from the one the plan names.

## Must fix before publishing

**M1. The summary uses effect language for H4 (line 50).** "Renewing early had no detectable effect on spending growth in PY2022-PY2024." Rule 5 (plan section 7) says H4 "is interpreted as an effect ... only if the equivalence condition ... holds". `did.json` shows `pre_trend_check.equivalence.holds: false` and `H4.interpretable_as_effect: false`. The next clause ("so that estimate is not read as an effect") contradicts the clause before it. The headings "What renewing did (H4)" (line 38) and "H4: what renewing did to spending" (line 424) make the same slip. *Fix:* "Early renewers' spending growth in PY2022-PY2024 did not differ detectably from that of ACOs not yet renewed (-0.4%, -4.0% to +2.5%). A continuing pre-period difference in trends cannot be ruled out, so this is not read as an effect of renewing." Retitle the section, for example "H4: spending after renewal".

**M2. "The primary test supported the reset motive" (line 46) overstates the finding, and the sign of the expected gain is never stated.** Rule 1's registered wording is "evidence for the reset motive beyond past savings". The post's own definition of the motive is "A new benchmark would be higher than the current one" (line 112). The gain components add to the total (plan 4.3 step 5, enforced by `assert_components_add_to_gain.sql`), so the unweighted group means in `exploratory.json` give the average expected gain:

- Early renewers: `leavers.early.own.mean` -5.26 + `leavers.early.regional_comp.mean` 3.69 = **-1.6%**.
- Stayers: -3.20 + 2.15 = **-1.05%**.

So on the approximation, an early reset would have lowered the average early renewer's benchmark, slightly more than a stayer's (`confirm.json` `groups.gain` -0.5, p 0.33). Lines 384-386 say the gain "does not differ" but never give its sign. A reader of the summary will assume early renewers stood to gain. *Fix:* in the summary, use rule 1's wording, then add one sentence: "By the approximation, a reset would on average have lowered both groups' benchmarks (by about 1.6% for early renewers and 1% for stayers); early renewers stood to gain more from the regional adjustment and lose more on their own spending." Repeat it in the paragraph at lines 384-389. This follows from the post's own lines 119-120: a negative own-spending component is what a positive savings rate implies, because rebasing to an ACO's own spending lowers the benchmark of any ACO that has been beating it. The group means show it: stayers save 4.6% and have an own component of -3.2; early renewers save 6.4% and have -5.3 (`exploratory.json` `leavers`).

**M3. The registered H4 attrition report is missing, and the attrition is uneven.** Plan 4.5: "attrition is reported by group and year". The post says only "one stayer has no spending value" (line 426). The dashboard (`dashboard.js`, `data.json`), the data builder (`dashboard_data.py`) and the notebook (`results_notebook.py`) contain no attrition output (searched for "attrition", "absent", "later renewal"). `did.json` `attrition`:

| | PY2022 included | PY2023 included | PY2024 included | PY2024 absent | PY2024 later renewal |
|---|---|---|---|---|---|
| Early renewers (29) | 29 | 28 | 25 | 1 | 3 |
| Stayers (277) | 276 | 222 | 162 | 72 | 42 |

By PY2024, 42% of the comparison group has gone (left the program or renewed) against 14% of early renewers. Exits are unlikely to be random: leavers had the lowest savings rates (line 511). The balanced panel (-1.6%, p 0.30) is the only check on this, and the post does not present it that way. *Fix:* add the table or its counts, and add a sentence to Limitations about differential attrition and selection in the comparison group's later years.

**M4. The agreement table shows the wrong conventional counterpart for H2a and H2b (lines 452-453).** Plan 5.7 defines the counterpart as "OLS with HC2 errors for H2a and H2b", and the code builds the agreement from that test (`conventional.py:99`, `conventional[label]["ols_hc2"]`). The post shows Welch results instead. The registered counterparts in `conventional.json` are:

- H2b: `ols_hc2` +3.35 (1.30 to 5.40), p = 0.0013
- H2a: `ols_hc2` -2.08 (-3.81 to -0.36), p = 0.018

The verdicts are the same. *Fix:* put the OLS-HC2 values in the table, and give Welch in a note if you want it.

## Should fix

**S1. The own-spending component has very low reliability, and the post says so only in passing (lines 207-212, 347-350, 416-418).** The measurement-error SD used in the model, σ_v = 4.38 (`validation.json` `sigma_v_model` 4.375), is larger than the variable's own SD among stayers, 3.33 (`power.json` `h2.own.sd_stayers`). Under the classical error model the plan assumes, observed variance cannot be smaller than error variance. So either the validation-sample error does not carry over to this sample, or the variable is mostly noise. "Validation passed (Spearman 0.94, error 1.6%)" checks benchmark *levels*, which vary widely across ACOs. It says little about a *difference* such as the own-spending component. The full-benchmark error has an SD of 4.37% against a median of 1.6%, which points to heavy tails. This affects H2a, the total-gain null, and the "parts offset" argument (M2). *Fix:* add two sentences to the validation subsection and to Limitations. The H1 result, which uses CMS's own savings rates, is the robust evidence that early renewers were beating their benchmarks.

**S2. The regional pull does contain some of the ACO's own data, and the post claims it does not (lines 133-134, 542-544).** "It has no own-spending term" is true only of BY1-BY3 spending. Two parts of the pull come from the ACO itself:

- The current benchmark B was built from the ACO's earlier spending (425.601(a)).
- R_e is multiplied by the ACO's own PY2021 risk score (plan 4.3 step 2), so the pull carries a coding-intensity term.

High pull therefore partly measures how low-cost the ACO had historically been relative to its region, which is also a plausible reason to want ENHANCED's 75% rate. That is a specific mechanism linking the pull to the sharing-rate motive, not just a formal "cannot rule out". The case-mix adjustment also matters a lot and was never validated. Unadjusted, the pull difference is +6.9 rather than +3.4 (`robustness.json` `9_unadjusted_pull.H2b`), and H3's pull interval reaches zero (0.75, -0.02 to 1.56). *Fix:* add both points to Limitations, and qualify "not a function of past savings" (line 543).

**S3. Say plainly that the equivalence condition could not have held for a near-null estimate (lines 436-443).** The condition needed |H4| > 0.115 log points (about 12%), three times the MDE. For any plausible estimate the H4 rule could only end in "not read as an effect". "The rule working as written" is accurate, but readers need to know this was a property of the design, fixed at registration. State what the data do bound: the interval is -4.0% to +2.5%, and the trend-adjusted interval of -12.0% to +2.7% is too wide to be informative.

**S4. Registered reporting items are missing.**

- Plan 4.4 asks for the validation slope and intercept, which decide whether calibration is applied: 0.944 and 664, so no calibration.
- Plan 4.4 also asks for results by phase-in step (n 62 and 39) and the step-1 check (Spearman 0.946, error 1.4%, n 101).
- Plan 5.4 asks for the share of refits that failed convergence (0.34-0.43%, `tests.*.share_refits_not_converged`) and the prior predictive share (median 17%, 95% range 1-70%).
- The 10 of 111 regular renewers dropped from validation (`validation.json` `excluded: 10`) are not mentioned. "The 101 regular renewers whose 2022 benchmarks CMS does publish" (line 168) implies none were dropped.

A short "other registered outputs" list, or a dashboard panel, would cover all of these.

**S5. H4 percentages are converted inconsistently (lines 332, 436).** "3.8% (log 0.038)" is 100 × the log value. H4 itself is reported as 100 × (exp − 1), which gives +3.9% / −3.7% for the MDE. *Fix:* "3.8 log points (about 3.7% to 3.9%)".

**S6. The H3 power statement overgeneralizes (lines 335-336).** "An 'undetermined' H3 verdict is therefore the expected outcome, whatever the motives were." Power was simulated only at a coefficient of 0.5. *Fix:* "...if the true effects were about 0.5 log-odds per 2 SD".

**S7. The post never says what the H3 BASIC-level result means (lines 401, 408).** The overview asks "why", and H3 finds a higher BASIC level supported (p = 0.003), but the motives discussion never interprets it. In `exploratory.json` `who_renewed`, 16 of the 27 BASIC-track early renewers were already at Level E. The registered rationale is "a smaller step to two-sided risk under ENHANCED" (plan 1.3), which bears on the sharing-rate side. Give it one sentence, and mention H3 in the summary.

**S8. Pipeline claims that do not quite match the record.**

- Line 270 says stages run in the order "validate, power, confirm, robustness, ..." and that "each refuses to start until the output it depends on exists". In `run.py`, `REQUIRES["robustness"]` needs only validation and power. Robustness ran alongside confirm and was committed (`8c05b79`, 2026-10-26 10:18 EDT) about 17 hours before the confirm results (`992d13f`).
- Line 483 says robustness was "read only after the confirmatory results". BUILD-NOTES says "read only together with". Pick one wording and state that the run was concurrent.
- Line 218 says "roughly 19 hours". The actual run took 17 h 3 min (BUILD-NOTES).

**S9. The exclusion diagnostics are not in the results files (lines 551-558).** The claims that every one of the 39 excluded ACOs has hidden ESRD counts (15 also aged/dual), and the size medians 6,702 / 8,578 / 10,757 / 15,649, do not appear in any results JSON. BUILD-NOTES says they came from "a diagnostic run (outside the repository)". *Fix:* say so in the text, or commit the diagnostic.

**S10. Overview counts do not match the Design section (lines 30-31 vs 98).** "29 of the 306 ACOs in agreements that began in 2019 or 2020" conflicts with the Design's base of 334. The 306 excludes the 28 leavers, and "2019" excludes the January 1, 2019 starters (425.200(b)(4)(i)). *Fix:* "29 of the 334 ACOs whose agreements began July 1, 2019 or January 1, 2020 (306 of them still in the program in 2022)".

## Consider

- **Rule vocabulary.** "Supported" (H2b) and "contradicted" (H2a) are rule 4's H3 labels. Rules 1 and 2 use descriptive wording. The quoted H2a sentence (line 376) is an adaptation of rule 1's wording, not registered text, so mark it as such.
- **Further design threats.**
  - Survivorship: the base population needs a PY2021 record, so ACOs that left during 2020 are excluded.
  - Anticipation: the decision was made during 2021, which is also the last pre-period year and BY3.
  - Participant-list changes at renewal could move H4 spending through composition rather than behavior; the risk-adjusted variant addresses this only partly.
  - Leavers are an alternative choice, and comparing early renewers only with stayers sets that choice aside.
- **Magnitude sensitivity for H2b.** The robust-regression estimates (+2.1, +2.2) are below the MDE of 2.5 and well below the +3.4 difference in means, which suggests a few large values among early renewers. "Holds in every check" (line 486) is true of the direction only.
- **Student-t fit.** Its own-spending coefficient is -0.56 (-9.98 to 7.36). Report it next to the pull and BASIC-level values (line 413).
- **Citation precision.** Line 131 cites 425.601(a)(6) for the four enrollment types. (a)(6) is the restatement to BY3 proportions; the types are listed in (a)(2), and the shares that combine them are in (d)(3).
- **Leavers.** The pull for leavers covers 20 of 28 (`exploratory.json` `leavers.leaver.pull.n`). Say so at line 512.
- **Jargon.** "PY" is never defined. Also define BASIC levels A-E, one- and two-sided risk, and "glide path" at first use. A five-row glossary would help.
- **Length and voice.** About 7,400 words, and the first result appears after roughly 3,000. The OSF summary-field paragraph (lines 316-319), the Playwright pin (line 573) and much of "What review caught" read as build log rather than reader content; move them to an appendix or to BUILD-NOTES. Framing the methods as "following Jake VanderPlas's 'Statistics for Hackers'" is informal for a health-policy audience; the Rubin and Phipson-Smyth citations already carry the method. Nothing reads as promotional, and the AI-use note is neutral.
- **Before publishing.** Remove the draft HTML comment (lines 11-20), as its own checklist says.

## Sources spot-checked

All of these support the sentences that cite them.

- **eCFR rule text**, read through the versioner API at 2022-01-01:
  - 425.20 "Renewing ACO" (2)
  - 425.200(b)(3)(ii)(B), (b)(4)(ii), (b)(5)
  - 425.220(a)
  - 425.226(a)(2)(i)
  - 425.600(a)(4)(i)(B)(1)(i), (2), (2)(iii), (2)(iv)
  - 425.601(a)(3), (a)(5), (a)(8), (a)(8)(i)(C), (a)(8)(ii)(C), (d)(1), (e)(1), (e)(2)(i), (f)
  - 425.610(d)(2) (75% of savings) and (f)(2) (loss rate 40-75%)
  - 425.600(a)(4)(i)(B)(2)(vi), read at 2023-01-01 (stay in Level A or B)
- **Federal Register:** 83 FR 67859 says CMS will "restrict ACOs from moving from the BASIC track to the ENHANCED track within the ACO's current agreement period" and points to early renewal. 85 FR 27574 has the optional fourth year for 2018 starters.
- **CMS specifications v10**, section 4.1.2 step 3: the BY3/BYx risk ratio.
- **Archived CMS cell suppression policy:** values of 1 to 10 are not reported.
- **DOIs:** all 16 resolve on Crossref with the authors, year, volume and pages given.

Not checked: the `#p-...` paragraph anchors were not rendered in a browser, and the OSF pages and file hashes were not fetched.

## What the post does well

- Every reported estimate, interval, p-value and sample size matches the results files. The H1 fraction/percent units issue is found and disclosed.
- The code at every run commit is verified identical to the registered commit. The outcome lock in the code and the OSF timestamp make the confirmatory claim checkable rather than asserted.
- Verdicts follow the registered rules, including the unwelcome ones: H2a runs against the predicted sign, H4 is not read as an effect, and the >10% exclusion limitation is reported.
- The H3 discussion is careful. It flags the type-M risk at 14-17% power, explains that the own-spending coefficient is just the prior, and reports the Firth model, the Student-t fit and the no-measurement-error fit.
- The plan's background error (ENHANCED losses "up to" 75%; the bar on BASIC-to-ENHANCED is in the preamble, not the regulation) is disclosed even though nothing depends on it.
- Multiple comparisons are not a concern here. There is a single declared primary test, and both supported H3 predictors (p = 0.002 and 0.003) would survive a Bonferroni correction across the three core predictors.
