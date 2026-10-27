Title: Why did Medicare ACOs reset their benchmarks early? A pre-registered study
Status: draft
Date: 2026-10-26T12:00:00Z
Modified: 2026-10-26T12:00:00Z
Tags: causal-inference, pre-registration, bayesian, resampling, difference-in-differences, healthcare, medicare, dbt, duckdb, python
Category: Causal Inference
Slug: 20261026-preregistered-mssp-early-renewal
Authors: Samuel Harrold
Summary: A study of Medicare Shared Savings Program ACOs that ended their agreements early to reset their benchmarks, registered on OSF before any outcome data were read: the plan, the methods, the pipeline and the results.

<!-- DRAFT. Results filled from analysis/mssp-benchmark-ratchet/results/ (every stage run, 2026-10-27). Before
     publishing: set Date and the slug's date prefix, rename content/static/<slug>/,
     remove the slug from STATIC_EXCLUDES in publishconf.py, and change the dashboard's root-relative /static/ links
     to {static} (Pelican copies {static}-linked files even when STATIC_EXCLUDES lists them, so a draft must not use
     them; once published, {static} makes the build check that the files exist). Results notebook: built and
     exported (HTML in content/static/<slug>/, .ipynb and PDF in analysis/mssp-benchmark-ratchet/report/exports/,
     hashes in the post); change its root-relative link to {static} too. Re-exported 2026-10-27 after the critical
     assessment (H4 wording), uploaded to OSF z4an5/results-notebook as new versions, and OSF's sha256 checked
     against the post. Never re-export again, since that changes every hash. src_master was merged into the
     study branch 2026-10-27 (uv.lock change logged in DEVIATIONS.md). Finally delete this comment: HTML
     comments are published in the page source. -->

[TOC]

## Overview

| At a glance | |
|---|---|
| Question | Why did 29 of 334 ACOs end their Shared Savings Program agreements early in 2022 to reset their benchmarks, and did renewing change their spending? |
| Data | Public CMS files, 2014-2026: ACO enrollment, performance-year results, county spending and county assignment (40 files, 40 MB) |
| Design | Pre-registered on OSF before any outcome was read; group comparisons, a decision model and a difference-in-differences estimate, with decision rules fixed in advance |
| Methods | Bayesian bootstrap, stratified permutation tests, Bayesian logistic regression with measurement error, direct-simulation tests, difference-in-differences with an equivalence rule, conventional comparisons |
| Tools | Python, dbt on DuckDB, PyMC, statsmodels, uv; an interactive dashboard in plain JavaScript; a marimo notebook |
| Finding | Early renewers' regions spent more relative to their benchmarks, but they were also beating their benchmarks, so on average a reset would not have raised them; no detectable change in spending afterward |
| Reproduce | About 10 minutes to download the data and run the tests; about 18 hours to rerun every stage ([Reproduce](#reproduce)) |

In the [Medicare Shared Savings Program][mssp][^cms-mssp] (MSSP), an [accountable care organization][aco-cms][^cms-aco] (ACO) earns a
share of the savings when its patients' spending comes in below a benchmark. The benchmark is
[reset at the start of each agreement period][cfr-601-reset][^cfr-425-601] from the ACO's own recent spending,
[pulled toward its region's][cfr-601-adj]. An ACO can [end its agreement early and start a new one][cfr-20-renewing][^cfr-425-20],
which resets the benchmark early. Of the 334 ACOs whose agreements began July 1, 2019 or January 1, 2020, 29 ended
them early and started new ones on January 1, 2022; 277 stayed in their agreements and 28 left the program (from the
[enrollment files][data-acos][^data-acos]).

This post asks why they did, and what renewing changed:

* **Who chose to reset, and why (H1-H3).** Did early renewers stand to gain from a reset because their regions spent
  more than their benchmarks (the primary test), because their own spending had run high, or because renewing was
  the only way into the [track that shares 75% of savings][cfr-610-rate][^cfr-425-610]?
* **Spending after renewal (H4).** Did early renewers' spending change afterwards, relative to ACOs that had not
  yet renewed? A [difference-in-differences][did-wiki] estimate.

Terms used throughout:

* **PY:** performance year, the calendar year over which CMS measures an ACO's spending against its benchmark.
* **Benchmark years (BY1-BY3):** the three years before an agreement starts, whose spending sets the new benchmark.
* **BASIC and ENHANCED tracks:** BASIC has five levels, A to E. Levels A and B are **one-sided** (the ACO shares
  savings only), and C to E are **two-sided** (it also repays part of any losses). ENHANCED is two-sided with the
  highest sharing rate.
* **Glide path:** BASIC's schedule for moving an ACO up a level each year, toward two-sided risk.

The analysis plan was registered on [OSF Registries](https://osf.io/c53w9/) (DOI
[10.17605/OSF.IO/C53W9](https://doi.org/10.17605/OSF.IO/C53W9))[^registration] before any outcome value was read, together with the
analysis code, which was written and tested on [synthetic data][synthetic][^code] first. Every result below is reported, whatever it
shows; changes made after registration are listed separately under [Deviations](#deviations).

**In short.** The primary test found what the plan calls "evidence for the reset motive beyond past savings": early
renewers' regions spent 3.4 percentage points of benchmark more than stayers' regions, relative to their current
benchmarks (95% [credible interval][credible] 1.7 to 5.4, p < 0.001). That is not a larger expected gain. Early
renewers were beating their benchmarks by more than stayers, with savings rates about 2 points higher, and by the
approximation a reset would on average have *lowered* both groups' benchmarks (by about 1.6% for early renewers and
1% for stayers): early renewers stood to gain more from the regional adjustment and to lose more on their own
spending. In the decision model, renewing early was more likely with a higher regional pull and a higher BASIC level.
Early renewers' spending growth in PY2022-PY2024 did not differ detectably from that of ACOs not yet renewed (-0.4%,
-4.0% to +2.5%); a continuing pre-period difference in trends cannot be ruled out, so this is not read as an effect
of renewing.

**In plain English.**

* **Early renewers were in regions that spend more.** The ACOs that reset early tended to be in places where Medicare
  spends more per patient, relative to the ACO's own benchmark, than the places stayers were in: about 3.4% of the
  benchmark more, or roughly $385 per patient per year at the median benchmark of $11,312 in PY2021 (the
  [PY2021 results file][file-py2021][^data-results]). A reset pulls the benchmark toward the region's spending, so these
  ACOs had more to gain from that part of it.
* **But they were already beating their benchmarks.** They spent further below their targets than other ACOs did. A
  reset also resets the target to the ACO's own recent spending, so for most of them that part would have cut the
  benchmark. By the study's estimate the two parts roughly cancel, and a reset would not have raised the average
  early renewer's benchmark.
* **ACOs at higher BASIC levels renewed early more often.** ACOs already at BASIC's higher, two-sided levels (C to
  E) were more likely to renew early; 16 of the 27 BASIC-track early renewers were at the top level, E. Renewing was
  their way into ENHANCED, which keeps 75% of savings, so the pattern fits an interest in the higher sharing rate,
  but it cannot be told apart from the regional motive, because both came with the same choice.
* **Spending afterward looked about the same.** Early renewers' spending growth in 2022-2024 was close to that of
  ACOs that had not renewed. The data rule out a drop of more than about 4% or a rise of more than about 2.5%, but a difference in
  trends that began before renewal could still hide a smaller effect, so this is not read as "renewing had no
  effect".
* **What this means.** ACOs that reset early were positioned to gain from the regional adjustment and from a higher
  sharing rate. A reset was not a simple way to get a higher benchmark.
* **These are the 2022 rules.** Benchmarks for agreements starting in 2024 or later give ACOs credit for past savings
  and soften the cut for an ACO that spends more than its region, so the same trade-off may not hold for an ACO renewing today (see
  [Limitations](#limitations)).

## Background for newcomers

Four short primers for readers new to the program or the methods; each opens on a click, and experienced readers can
skip them.

<details markdown="1">
<summary><strong>How the Shared Savings Program works, with a worked example</strong></summary>

An ACO is a group of doctors and hospitals that agrees to be measured on the total Medicare spending of the patients
assigned to it. CMS sets a **benchmark**: the spending it expects per patient per year. If the ACO's patients cost
less, and the ACO meets quality standards and saves more than a minimum rate, it keeps a share of the savings. On the
BASIC track that share is up to 40% (one-sided levels A and B, which never owe money) or 50% (two-sided levels C to
E, which also repay part of any losses). On ENHANCED it is up to 75%, with up to 75% of losses
([42 CFR 425.605][cfr-605-levels], [425.610][cfr-610-rate]).

A made-up example, ignoring risk adjustment, trends and caps:

* The benchmark is &#36;11,000 per patient and the ACO's 15,000 patients cost &#36;10,500 each: &#36;500 saved per patient, &#36;7.5
  million in all. At a 50% sharing rate the ACO receives about &#36;3.75 million; at 75%, about &#36;5.6 million.
* At the next agreement the benchmark is **reset**. The new one starts from the ACO's own recent spending, about
  &#36;10,500, so the **own-spending part** of a reset lowers it by &#36;500: beating the benchmark today makes the next one
  harder.
* It is then **adjusted toward the region**. If comparable patients in the ACO's region cost &#36;12,000, the benchmark
  moves part of the way there: with the [phase-in weight][cfr-601-phase] of 35% that applies the first time (it rises
  to 50% later), by 0.35 x (&#36;12,000 - &#36;10,500) = &#36;525. That is the
  **regional part**, and the regional pull measures how much room there is for it.
* The new benchmark is about &#36;10,500 + &#36;525 = &#36;11,025, almost the same as before. This is the pattern the study found
  for early renewers: the regional gain and the own-spending loss roughly cancel.

Agreements last five years. Early renewal ends one early and starts a new one, which resets the benchmark sooner and,
for a BASIC ACO, is the way into ENHANCED. More: CMS's [program page][mssp][^cms-mssp] and the rule,
[42 CFR 425.601][cfr-601].

</details>

<details markdown="1">
<summary><strong>Association and causation: what the methods can and cannot show</strong></summary>

Statistics cannot prove that one thing caused another. A study design can make a causal claim credible, under
assumptions it states and checks. The **effect** of renewing early on an ACO is the difference between what happened
and what would have happened had the same ACO not renewed, and that second outcome is never observed. A randomized
experiment solves this by making the groups alike on average. Here ACOs chose for themselves, so the ones that renewed
may differ in ways that also affect spending (**selection**).

* **H1-H3 are associations.** They describe which ACOs chose to renew early, and say nothing about what renewing
  caused.
* **H4 uses difference-in-differences.** It compares the change in spending of early renewers with the change for
  ACOs that had not yet renewed. That is an effect only if, without renewal, both groups' spending would have changed
  in parallel (**parallel trends**), ACOs did not change behavior in anticipation, and one group's choice did not
  affect the other's spending. Earlier years can test parallel trends only weakly, and here there is one earlier
  change, so the plan required an **equivalence condition** before reading H4 as an effect. It did not hold.
* **Pre-registration** guards against a different problem: trying many analyses and reporting the one that works.
  Fixing the analyses and decision rules first means a reader can trust that the reported tests were not chosen
  after seeing the results.

More, all free online: Cunningham's [*Causal Inference: The Mixtape*](https://mixtape.scunning.com/),
Huntington-Klein's [*The Effect*](https://theeffectbook.net/), and Hernán and Robins's
[*Causal Inference: What If*](https://miguelhernan.org/whatifbook).

</details>

<details markdown="1">
<summary><strong>Bayesian and frequentist statistics, side by side</strong></summary>

The two schools answer different questions about the same data.

* A **frequentist p-value** asks: if there were no real difference, how often would chance alone produce a difference
  at least as large as the one observed? Here chance is simulated directly: the early-renewer labels are shuffled
  10,000 times, and the p-value is the share of shuffles with a difference at least as large. A **confidence
  interval** is a range built by a procedure that captures the true value in 95% of repeated studies.
* A **Bayesian posterior** describes what is plausible about the true value after seeing the data, given a model and
  a **prior** (what was assumed before). A 95% **credible interval** is a range with 95% probability of holding the
  true value, under that model. In this study the priors are mild: on the log-odds scale, Normal(0, 1) says large
  effects are unlikely, which keeps the estimates stable with only 24 early renewers in the decision model. A second
  fit with wider Student-t priors checks that the results do not depend on that choice.

The study uses both on purpose. Estimates and their uncertainty are Bayesian. The yes-or-no decisions use p-values
against thresholds fixed in the registration, because a rule written in advance is easy to check. The
conventional (frequentist) versions are reported beside them, and every verdict agrees, so the conclusions do not
hinge on the choice of school.

More: VanderPlas's [*Frequentism and Bayesianism: A Python-driven Primer*](https://arxiv.org/abs/1411.5018) (free)
and McElreath's [*Statistical Rethinking*](https://xcelab.net/rm/).

</details>

<details markdown="1">
<summary><strong>How to pre-register your own observational study</strong></summary>

This study's plan ([`PREREGISTRATION.md`][plan-file][^plan]) can serve as a template. Its sections are the ones a registry
expects:

1. **Background and hypotheses:** each with its predicted direction and its role (primary, secondary, descriptive).
2. **Data:** the sources, and what you have and have not already seen.
3. **Sample and groups:** exact inclusion rules, and how missing or hidden values are handled.
4. **Variables:** how each is built, and how any approximation is validated before it is used.
5. **Analysis plan:** every estimate and test, robustness checks, and what is exploratory.
6. **Power:** what effect sizes the data can detect.
7. **Decision rules:** the exact wording for each possible result, written before any result exists.
8. **Deviations:** how later changes will be logged.

Register it with an independent registry that records the time itself (see
[OSF's guide to registrations](https://help.osf.io/article/229-select-a-registration-template)), keep the code that
reads outcome data locked until then (this study's outcome lock is described under [Why pre-register](#why-pre-register)), and log
every later change before using its results.

</details>

## Why pre-register

The CMS [public use files][puf][^cms-puf] used here are public. Anyone analyzing them can try many specifications and
report the one that works, often without meaning to ([Simmons, Nelson and Simonsohn 2011][simmons2011][^simmons2011]). A
pre-registration fixes the question, the variables, the tests and the decision rules before the outcomes are seen, so
a reader can tell confirmatory results from exploration ([Nosek et al. 2018][nosek2018][^nosek2018]).

Two details make that claim checkable here:

* **An independent timestamp.** [Git commit dates can be set by hand][git-dates], so the plan was registered on
  [OSF Registries][osf-registries], which records the time itself. The plan file's [sha256][sha2] and the registered
  code commit are recorded in [`REGISTRATION.md`][registration-md][^results], so the repository copy can be matched to the
  registered one.
* **An outcome lock in the code.** Every data file is [hashed before it is read][snapshot-py][^code]. A file whose hash matches a
  performance-year results file or a county spending file could not be opened until `REGISTRATION.md` existed. There
  was no bypass flag. Before registration only the [enrollment files][data-acos][^data-acos], the CMS data dictionaries (for example the
  [PY2021 results dictionary][dict-results-2021][^data-results]) and the [regulation text][cfr-425][^cfr-425] were used, plus the column names (not the values) of the outcome files, to write the code.

## How the question was chosen

The question in this post was the fourth candidate. The first three were dropped at the design stage, using only the
regulation and the enrollment files:

1. **Downside risk.** The program's "glide path" [moves ACOs into two-sided risk on a schedule][cfr-600-glide][^cfr-425-600],
   which looked like a [natural experiment][natural-exp]. The regulation showed that the timing is partly chosen:
   ACOs [choose the level they start at][cfr-600-entry], [can move up faster][cfr-226][^cfr-425-226], and could pause the advance
   for [2021][cfr-600-pause-2021] and [2022][cfr-600-pause-2022]; from 2023, an ACO still in one-sided Level A or B
   could [stay there for the rest of its agreement][cfr-600-stay-2023]. The [enrollment files][data-acos][^data-acos] showed that only
   about 10-28% of ACOs were in two-sided risk in the years the schedule called for it. Not a usable treatment.
2. **The benchmark ratchet.** Do ACOs spend less once their spending starts counting toward the next benchmark? In
   the enrollment data, benchmark-year status is [collinear][multicol] with how long the ACO has been in its agreement, so the
   effect cannot be separated from tenure. Kept only as a descriptive table.
3. **A correction.** An early tabulation found 139 ACOs leaving their benchmark-year schedule at the 2022
   transition, and an unverified inference treated them all as early renewers. Accounting for the [optional
   one-year extension][cfr-200-ext][^cfr-425-200] of agreements that began in 2018 (from the [2020 interim final rule][fr-covid][^fr-2020])
   showed that only 29 renewed early into a January 1, 2022
   agreement.

Those 29 became the question. A first version asked only whether they had lower savings rates. That was too narrow
to explain anything, so the plan became explanatory, with two motives that predict different things.

## Related work

Four strands of earlier research bear on this study. None of them, as far as a focused literature search found,
studies early renewal itself.

* **Rebasing creates a ratchet.** The rules for setting an ACO's benchmark at renewal weaken its incentive to save,
  and the old weights on the benchmark years even rewarded higher spending just before a new agreement
  ([Douven, McGuire and McWilliams 2015][douven2015][^douven2015]). That is one reason the H4 design guards against
  anticipation and mean reversion.
* **ACOs differ widely from their regions.** Even after case-mix adjustment, ACOs' spending varies widely relative to
  local fee-for-service spending, so moving benchmarks toward regional averages shifts them unevenly
  ([Rose, Zaslavsky and McWilliams 2016][rose2016][^rose2016]). That variation is what the regional pull measures, and
  why its case-mix adjustment matters (see [Limitations](#limitations)).
* **Benchmarks drive who participates.** After regional spending entered benchmarks in 2017, participation shifted
  toward providers whose spending was low relative to their region ([Lyu, Chernew and McWilliams 2023][lyu2023][^lyu2023]),
  and ACOs whose effective benchmark fell were 7 percentage points more likely to leave
  ([Chen and McWilliams 2025][chen2025][^chen2025]). The primary result here is the same kind of selection, in when to
  reset rather than whether to join or leave.
* **The 2019 rules changed participation decisions.** Under Pathways to Success, for the first time more ACOs left the
  program than joined it, and ACO leaders described reassessing potential savings against losses in light of the
  benchmark changes ([Ying et al. 2024][ying2024][^ying2024]). Related work describes the change in participation
  ([Ying et al. 2023][ying2023][^ying2023]) and the cost to the program of departures
  ([Moloci et al. 2021][moloci2021][^moloci2021]).

This study adds the early-renewal choice: which ACOs used the option to reset their benchmark early, measured with
public data under a pre-registered plan. The search used Google Scholar Labs (three queries on 2026-10-27, one
rejected as too broad), and its questions, raw results and per-paper summaries are saved in the study's
[`research/`][research] folder.

## Design

### Groups

The base population is the 334 ACOs in the [enrollment files][data-acos][^data-acos] whose agreements began July 1, 2019 or
January 1, 2020 ([plan section 3][plan-3][^plan]). Both cohorts' agreements run to December 31, 2024
([42 CFR 425.200(b)(4)(ii)][cfr-200-b4][^cfr-425-200] and [(b)(5)][cfr-200-b5]), so a January 1, 2022 agreement start means an
early renewal: an ACO that [terminated its agreement][cfr-220][^cfr-425-220] and immediately entered a new one
([425.20, "renewing ACO"][cfr-20-renewing][^cfr-425-20]).

| Group | 2019-07-01 cohort | 2020-01-01 cohort | All |
|---|---|---|---|
| Early renewers | 11 | 18 | 29 |
| Stayers | 159 | 118 | 277 |
| Left after PY2021 | 19 | 9 | 28 |

### Two motives, and why the savings rate cannot separate them

* **The reset motive.** A new benchmark would be higher than the current one.
* **The sharing-rate motive.** An ACO in the [BASIC track][cfr-605-levels][^cfr-425-605] cannot move to the ENHANCED track during
  an agreement period ([2018 rule][fr-pathways-track][^fr-2018]), so renewing early was the only way in before its agreement
  ended. ENHANCED shares [75% of savings][cfr-610-rate][^cfr-425-610] and [up to 75% of losses][cfr-610-loss]. In the
  [enrollment files][data-acos][^data-acos], 26 of the 27 early renewers that were in BASIC moved to ENHANCED, and no stayer did.

The expected benchmark gain from a reset has two parts: an **own-spending** part (how the ACO's recent spending
compares with its current benchmark) and a **regional** part ([the adjustment toward the region][cfr-601-adj][^cfr-425-601]). The own-spending
part is close to a restatement of the savings rate. Writing out the regional adjustment shows that it contains the
own-spending part too, with a negative sign. With [phase-in weight][cfr-601-phase] $w$, before [capping][cfr-601-cap],

$$\text{regional component} = w \times (\text{pull} - \text{own})$$

where "pull" is the regional pull defined below and "own" the own-spending component, so the regional part is also
tied to past savings. The primary test therefore uses the **regional pull**: how far the region's
spending, adjusted to the ACO's case mix [the way CMS adjusts it][cfr-601-regional-risk][^cfr-425-601], sits above the ACO's current benchmark,

$$\text{regional pull} = 100 \times \frac{\sum_e s_e\, R_e - B}{B}$$

where $R_e$ is the risk-adjusted regional spending for [enrollment type][cfr-601-types][^cfr-425-601] $e$ ([ESRD][esrd], disabled,
[aged/dual][dual], aged/non-dual), $s_e$ the ACO's share of person-years of that type, and $B$ its current per-capita benchmark. It has
no term for the ACO's own benchmark-year spending, though it is not free of the ACO's own data: $B$ was set from the
ACO's earlier spending, and $R_e$ is adjusted with the ACO's own risk scores (see [Limitations](#limitations)). An
ACO can be beating its own benchmark and still stand to gain from a reset because its
region spends more; that is the part of the reset motive a savings rate cannot show.

### Hypotheses

As registered ([plan section 1.3][plan-1.3][^plan]):

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

CMS does not publish what an ACO's benchmark would have been had it reset. The plan rebuilds it from
[42 CFR 425.601][cfr-601][^cfr-425-601] in six steps ([section 4.3][plan-4.3][^plan]), which come down to four parts:

* the [equally weighted mean][cfr-601-equal][^cfr-425-601] of the ACO's per-capita spending in the three benchmark years
  (PY2019-PY2021), [risk-adjusted][cfr-601-risk] and restated to the latest year's risk scores (CMS's
  [methodology specifications, version 10][spec-v10][^spec-v10], section 4.1.2, step 3), and
  [trended to 2021 dollars with the national-regional blend][cfr-601-trend];
* risk-standardized regional spending from the [county files][data-county][^data-county],
  [weighted by where the ACO's beneficiaries live][cfr-601-regional-weight][^cfr-425-601] (from the
  [assigned-beneficiaries-by-county files][data-assigned][^data-assigned]) and [adjusted to the ACO's case mix][cfr-601-regional-risk];
* the regional adjustment with the [phase-in weights][cfr-601-phase][^cfr-425-601] and [caps][cfr-601-cap];
* and the shares that [combine the four enrollment types][cfr-601-shares][^cfr-425-601].

Because several steps can only be approximated from public files, the approximation was **validated before it was
used**: rebuilt for the regular renewers whose 2022 benchmarks CMS does publish (in the
[results files][data-results][^data-results]; 101 of the 111 eligible; 10 lack either the rebuilt or the published benchmark), with a pass rule fixed in the plan ([section 4.4][plan-4.4][^plan]:
[Spearman correlation][spearman] at least 0.80, [median absolute percentage error][mape] at most 5%). Early renewers were kept
out of the validation sample, and the 2022 results file was filtered as it was loaded, so validation could not
reveal their actual reset.

## Methods

### Estimates and significance

Every confirmatory estimate is Bayesian, and significance is measured by resampling: the null distribution is simulated
rather than looked up (an accessible introduction is VanderPlas's "Statistics for Hackers";
[video][vdp-video][^vanderplas2016], [slides][vdp-slides]).

* **Group comparisons (H1, H2a, H2b, H4).** The estimate is the difference in means, early renewers minus stayers,
  within each cohort and averaged with weights proportional to the early renewers in each cohort. Its posterior is a
  [Bayesian bootstrap][bb-wiki] ([Rubin 1981][rubin1981][^rubin1981]): 10,000 draws of [Dirichlet][dirichlet](1, ..., 1) weights over the ACOs in each cohort-by-group
  cell.
* **Significance by stratified permutation.** Early-renewer labels are [shuffled][perm-wiki] within cohort 10,000
  times, and the estimate is recomputed on each shuffle. The two-sided [p-value][pvalue] is

    $$p = \frac{1 + \#\{\,|\hat\theta_\text{shuffled}| \ge |\hat\theta_\text{observed}|\,\}}{1 + 10{,}000}$$

  Adding 1 to both counts treats the observed labels as one of the shuffles, so the p-value is never zero
  ([Phipson and Smyth 2010][phipson2010][^phipson2010]). The resampling p-value decides, by rules written before the results
  (below). When it and the credible interval disagree, both are reported.

### H3: a Bayesian decision model with measurement error

A [logistic regression][logistic] of early renewal on the three core predictors (regional pull, own-spending
component, higher BASIC level) and five adjustment factors (cohort, size, revenue category, assignment method, first
or later agreement), fit with [PyMC][pymc][^sw-pymc] ([NUTS][nuts][^hoffman2014], 4 chains of 2,000 draws; plan [section 5.4][plan-5.4][^plan]).
Continuous predictors are scaled by two standard deviations ([Gelman 2008][gelman2008][^gelman2008]), so each coefficient is a
[log-odds][logit] difference per 2 SD. With 24 events (27 eligible early renewers, 3 missing a predictor) and 9
parameters, the Normal(0, 1) [priors][prior] keep the estimates stable, so a second fit with [Student-t][student-t]
priors ([Gelman et al. 2008][gelman-prior2008][^gelman-prior2008]) is reported for sensitivity. A Firth-penalized logistic regression
([Firth 1993][firth1993][^firth1993], fit with [`firthmodels`][firthmodels][^sw-firthmodels]) with the core predictors and cohort is always run
beside it, and decides H3 only if the Bayesian model fails its [convergence checks][vehtari2021][^vehtari2021].

The own-spending component is an approximation, so it enters as a latent true value [observed with error][eiv],

$$x_\text{observed} = x_\text{true} + \varepsilon, \qquad \varepsilon \sim \mathcal{N}(0, \sigma_v)$$

with $\sigma_v$ set by the validation step before the model is fit (4.38 percentage points, from CMS's own
benchmark-year spending for the validation sample; [`validation.json`][res-validation][^results]).

Shuffling labels in a model with several predictors would test "nothing matters", not "this factor matters given the
others". Each core predictor is instead tested by **direct simulation under the reduced model** ([a parametric
bootstrap][param-boot]): fit the model without that predictor, simulate 10,000 sets of outcomes from its posterior, refit the
full model to each, and compare the observed coefficient with that null distribution. That is about 40,000 [MCMC][mcmc]
refits, which took 17 hours on 5 cores.

### H4: difference-in-differences with an equivalence rule for pre-trends

The outcome is log per-capita spending. For each ACO,

$$\Delta = \overline{y}_\text{PY2022-24} - \overline{y}_\text{PY2020-21}$$

and the H4 estimate is the same cohort-weighted difference in means as above, applied to $\Delta$. Comparison ACOs
are those **not yet renewed**: a stayer's years after it renews into a 2023 or 2024 agreement are dropped, following
the not-yet-treated idea of [Callaway and Sant'Anna (2021)][callaway2021][^callaway2021] (plan [section 5.8][plan-5.8][^plan]).

The main threat is selection on the outcome's own path: if early renewers renewed after unusually high spending,
their spending could fall afterwards by [mean reversion][regmean] alone. There is only one pre-period change (PY2020 to PY2021,
both affected by COVID-19), and with about 29 treated ACOs a non-significant pre-trend test proves little ([Roth
2022][roth2022][^roth2022]). So H4 counts as an effect only if an **equivalence condition** holds (the logic of an
[equivalence test][lakens2017][^lakens2017]): the pre-trend interval, scaled to the
distance between period midpoints, must rule out a trend difference large enough to produce the estimate. A
trend-adjusted estimate (the pre-period slope carried forward, in the spirit of [Rambachan and Roth 2023][rambachan2023][^rambachan2023]) is reported
beside it, along with [propensity-weighted][ipw] ([Rosenbaum and Rubin 1983][rosenbaum1983][^rosenbaum1983]), risk-adjusted, balanced-panel and single-cohort versions.

### Conventional methods, side by side

For comparison, and not used for any decision (plan [section 5.7][plan-5.7][^plan]): [Welch t-tests][welch-wiki]
([Welch 1947][welch1947][^welch1947]) and [OLS][ols] with [HC2 robust errors][hc] ([MacKinnon and White 1985][mackinnon1985][^mackinnon1985]) for
H1, H2a and H2b; maximum-likelihood logistic regression for H3 ([statsmodels][statsmodels-logit][^sw-statsmodels]); and
[two-way fixed effects][fe] with an event study, [errors clustered][cluster] by ACO, for H4. An agreement table puts
each registered verdict next to the conventional one; for H2a and H2b the registered counterpart is OLS with HC2
errors, and the Welch t-test is shown beside it.

### Decision rules

Fixed before the results ([plan section 7][plan-7][^plan]). For H2b: p < 0.05 and positive means "early renewers' regions spent more
relative to their current benchmarks, evidence for the reset motive beyond past savings"; p < 0.05 and negative is
evidence against it; otherwise "no detectable difference", reported with the credible interval and the [minimum
detectable effect][power]. No test here can rule the sharing-rate motive in or out, because in these data it is bundled with
the reset in a single choice.

### What was simulated, and when

Simulated data played no part in forming the hypotheses. Three kinds of data were used, at three stages:

| When | Data | Used for |
|---|---|---|
| Before registration | The regulation, the enrollment files, the data dictionaries, and the outcome files' column names (not their values) | Choosing the question and writing the hypotheses ([How the question was chosen](#how-the-question-was-chosen)) |
| Before registration | Synthetic data, made up by [`ratchet/synthetic.py`][synthetic][^code] | Writing and testing the pipeline before any outcome could be read |
| After registration, before any confirmatory estimate | Simulations calibrated to the real data | The power analysis ([plan section 6][plan-6][^plan]) and the H3 direct-simulation tests |

The synthetic values are invented, not fitted to CMS data: no CMS outcome value was viewed to write the generator.
It builds a small stand-in (270 ACOs in the two cohorts and 80 regular renewers, in 3 states of 15 counties) with
lognormal spending, and it copies the real files' quirks: column names that change between years, `*` suppression
markers, date formats, and early-renewer rows the loader must drop. It also plants known answers. Early renewal is
made more likely with a higher regional pull and own-spending component (logistic coefficients 1.0 and 0.6 per SD),
and spending is 4% lower after renewal. The [tests][tests][^code] check that the SQL matches an independent NumPy
computation of every constructed variable, that the decision model recovers a planted direction on made-up data,
and that H4 recovers the -4% to within 0.015 log points.

The power analysis uses real spreads, read after registration as the plan allows: the PY2016-PY2018 savings-rate SD
for H1, the stayers' SDs of the regional pull and own-spending component for H2, and the SD of the pre-period
spending change for H4 ([`power.json`][res-power][^results]).

## Pipeline

The pipeline is in [`analysis/mssp-benchmark-ratchet/`][code][^code], linked here as registered (commit `a4064f5`):

* **Data snapshot.** Every CMS file used is listed with its size, sha256 and URL in
  [`data-snapshot.tsv`][snapshot][^code], and each hash is [checked before the file is read][snapshot-py]. The files come
  from four CMS datasets: [ACO enrollment][data-acos][^data-acos], [performance-year results][data-results][^data-results],
  [county expenditures and risk scores][data-county][^data-county] and [assigned beneficiaries by county][data-assigned][^data-assigned].
* **dbt for the SQL.** The constructed variables are a [dbt][dbt][^sw-dbt] project on [DuckDB][duckdb][^sw-duckdb]
  ([dbt-duckdb](https://github.com/duckdb/dbt-duckdb), in [`dbt/`][dbt-dir][^code]): 28 models, one per derived table, in
  three tagged stages, with schema and [data tests][dbt-tests] (unique keys, accepted
  values, components adding to the gain, shares summing to one, no early renewer in the validation load). Python
  loads every raw table after its hash check, so dbt never reads a file directly.
* **Two implementations.** A [synthetic-data generator][synthetic][^code] writes made-up files with the real file and column names and
  computes the constructed variables independently in [NumPy](https://numpy.org/). The [tests][tests] require the SQL to match it, and every stage
  runs end to end on synthetic data, including the recovery of a planted -4% effect in H4.
* **[Staged runner][run][^code].** Each stage refuses to start until the outputs it depends on exist: validate, then
  power, then confirm and robustness (both need only validation and power, and ran at the same time), then did,
  conventional and exploratory. So the power analysis was committed before any confirmatory estimate. The
  robustness results were committed first, about 17 hours before the confirmatory ones, and were read only together
  with them, primary test first.
* **Reproducible environment.** [uv][uv][^sw-uv] with a [lockfile][uv-lock]; PyMC, `firthmodels` and
  [`statsmodels`][statsmodels][^sw-statsmodels] are pinned in `uv.lock`, and every refit has its own seed from a fixed
  [seed sequence][numpy-seed][^sw-numpy] ([parallel streams][numpy-parallel]), so results do not depend on the number of
  processes. They do vary slightly between runs, within simulation error, because the analysis table is read
  without a fixed row order (see [Reproduce](#reproduce)).

Writing the code before registering found gaps in the plan while it could still change: column names that drift
between years (`ACO_Num` and `ACO_ID`, `Sav_Rate` and `Sav_rate`), how calibration splits between the gain's two
parts, how "below its region" is compared, and the per-refit seeds.

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

The attached Markdown file is the authoritative copy of the plan; OSF's summary field holds a plain-text version
(checked through the [OSF API][osf-api] before submission).

## Power

Computed after registration and committed before any confirmatory estimate, as the plan requires
([section 6][plan-6][^plan]; [`power.json`][res-power][^results]). [Minimum detectable effects][power] at 80% power, two-sided alpha
0.05, for 29 vs 277 ACOs:

| Test | Minimum detectable effect |
|---|---|
| H1 savings rate | 2.7 percentage points (simulated power 80.4%) |
| H2b regional pull | 2.5 percentage points |
| H2a own-spending component | 1.8 percentage points (0.55 SD) |
| H4 spending change | 3.8 log points (a change of +3.9% or -3.7%) |

**H3 is underpowered.** At a true log-odds difference of 0.5 per 2 SD, the 95% interval excludes zero in only 17%
(regional pull), 0% (own-spending component) and 14% (BASIC level) of simulated datasets. If the true effects were
about that size, an "undetermined" H3 verdict was the expected outcome. Power was simulated only at 0.5.

## Results

In the order the plan fixes: the validation that decides how the own-spending component is used, the primary test,
then H2a, H1, H3 and H4. Each verdict quotes the decision rule written before the results
([plan section 7][plan-7][^plan]). Every number comes from the results files in [`results/`][results-dir][^results], each of which
records the commit it ran at.

### Validation of the benchmark approximation

Passed. For the 101 regular renewers whose 2022 benchmarks CMS publishes (of 111 eligible; 10 lack either the rebuilt
or the published benchmark), the rebuilt benchmark had a Spearman correlation of 0.94 with the actual one and a
median absolute percentage error of 1.6% (the rule: at least 0.80 and at most 5%). The regression of actual on
rebuilt had slope 0.944 and intercept 664, inside the plan's 0.9-1.1 range for the slope, so no calibration was
applied. By phase-in step of the regional adjustment: 62 ACOs at the first step (Spearman 0.93, error 2.0%) and 39
at the second (0.96, 0.9%). The step-1 check of the own-spending part against CMS's own benchmark-year spending gave
Spearman 0.95 and error 1.4% (101 ACOs), and its error SD sets $\sigma_v$ = 4.38 percentage points
([`validation.json`][res-validation][^results]). The own-spending component is therefore used as registered, not as
exploratory.

These checks are on benchmark *levels*, which vary widely across ACOs. The own-spending component is a *difference*,
and its estimated error ($\sigma_v$ = 4.38 points) is larger than its spread among stayers (SD 3.3), so at the level
of one ACO it is mostly noise. H2a, the total expected gain and the offset argument below rest on it; the H1 savings
rates, which CMS reports directly, are the firmer evidence that early renewers were beating their benchmarks.

### Who renewed early (H2b, H2a, H1)

Early renewers minus stayers, within cohort and weighted by early renewers per cohort
([`confirm.json`][res-confirm][^results]). Expected-gain variables are in percentage points of the current benchmark (1 point
is 1% of the benchmark, about $113 per patient per year at the median PY2021 benchmark of $11,312); savings rates are
in percentage points.

| Comparison | Early renewers minus stayers | 95% credible interval | p | Minimum detectable effect |
|---|---|---|---|---|
| **H2b regional pull (primary)** | **+3.4** | **1.7 to 5.4** | **<&nbsp;0.001** | 2.5 |
| H2a own-spending component | -2.1 | -3.8 to -0.5 | 0.003 | 1.8 |
| H1 savings rate, PY2020 | +1.9 | 0.7 to 3.3 | 0.010 | 2.7 |
| H1 savings rate, PY2021 | +1.6 | 0.2 to 3.1 | 0.033 | 2.7 |
| Total expected gain (descriptive) | -0.5 | -2.0 to 0.8 | 0.33 | |
| Regional component (descriptive) | +1.6 | 0.9 to 2.2 | <&nbsp;0.001 | |

26 early renewers and 241 stayers for the expected-gain variables, 29 and 277 for H1 (see
[Limitations](#limitations) for the exclusions).

* **H2b (rule 1): the regional pull**, how far the region's case-mix-adjusted spending sits above the ACO's
  current benchmark. p < 0.05 and positive: "early renewers' regions spent more relative to their current
  benchmarks, evidence for the reset motive beyond past savings". The difference is larger than the minimum
  detectable effect, which was computed for 29 vs 277 ACOs and so is slightly understated for the 26 vs 241
  compared. In unweighted means, the early renewers' regions spent 5.0 points above their benchmarks, the stayers'
  1.8 points.
* **H2a (rule 2, which applies rule 1's wording to the own-spending component):** how the ACO's own recent spending
  compares with its current benchmark (negative when it spends below it). p < 0.05 and negative; in rule 1's
  terms adapted to this component, their own spending was lower relative to their benchmarks, contrary to the reset
  motive. Early renewers were
  beating their benchmarks by more than stayers. H2a is close to H1 restated, so it is not counted as separate
  evidence.
* **H1, descriptive (rule 3).** Early renewers had higher savings rates in both years. No motive is attributed to the
  sign. (The [PY2020 results file][file-py2020][^data-results] stores savings rates as fractions and the [PY2021 file][file-py2021] as
  percents; both are shown here in percentage points.)

The tables and the dashboard label these outcomes "supported" (H2b) and "contradicted" (H2a), shorthand for rule 1's
two directions.

The two parts of the gain point in opposite directions and offset: the regional component is larger for early
renewers, the own-spending component smaller, and the total expected gain does not differ. On average a reset would
have *lowered* both groups' benchmarks, by the approximation: in unweighted means the own-spending and regional parts
sum to -5.3 + 3.7 = -1.6 points for early renewers and -3.2 + 2.2 = -1.0 for stayers ([`exploratory.json`][res-exploratory][^results]).
That follows from the savings: rebasing to an ACO's own spending lowers the benchmark of any ACO that has been
beating it. So the evidence is about where early renewers stood relative to their regions, not about a larger
expected gain from resetting. That is the
configuration the plan described before any outcome was read ([section 1.3][plan-1.3][^plan]): an ACO "can be beating its own
benchmark and still stand to gain from a reset because its region spends more". As the plan also says (rule 8), no
test here can rule the sharing-rate motive in or out.

### H3: the decision model

206 BASIC-track ACOs, 24 of them early renewers (3 early renewers and 27 stayers excluded for a missing predictor;
[`confirm.json`][res-confirm][^results]).
Coefficients are log-odds differences per 2 SD, or for the BASIC level between levels C-E and A-B. A log-odds
difference of 1.34 multiplies the odds of renewing early by about 3.8.

| Predictor | Posterior mean | 95% credible interval | Direct-simulation p | Verdict |
|---|---|---|---|---|
| Regional pull | 1.34 | 0.44 to 2.30 | 0.002 | supported |
| Own-spending component | -0.05 | -2.01 to 1.92 | 0.19 | undetermined |
| Higher BASIC level (C-E) | 1.34 | 0.38 to 2.31 | 0.003 | supported |
| 2020-01-01 cohort | 0.63 | -0.24 to 1.51 | | adjustment |
| Log assigned beneficiaries | 0.45 | -0.49 to 1.36 | | adjustment |
| High revenue | -0.53 | -1.69 to 0.59 | | adjustment |
| Prospective assignment | -0.77 | -1.79 to 0.19 | | adjustment |
| Later agreement | -0.67 | -1.62 to 0.31 | | adjustment |

* **Verdicts (rule 4).** The regional pull and a higher BASIC level are supported; the own-spending component is
  undetermined. The overall test (the largest absolute core coefficient against its simulated null) gives
  p = 0.004. Adjustment factors are estimates only.
* **What the BASIC level means.** The plan's rationale for it is a smaller step to two-sided risk under ENHANCED
  ([section 1.3][plan-1.3][^plan]): 16 of the 27 BASIC-track early renewers were already at Level E in 2021, BASIC's
  highest level, for whom ENHANCED was a short further step ([`exploratory.json`][res-exploratory][^results]). That bears on
  the sharing-rate motive at least as much as on the reset motive, and the two cannot be separated here.
* **Checks.** The model met its convergence checks on the first fit (largest [R-hat][arviz-rhat][^sw-arviz] 1.001, smallest
  bulk [effective sample size][arviz-ess] 6,661, no divergences). The Student-t fit needed its one registered rerun, then converged, and agrees:
  regional pull 1.65 (0.53 to 2.87), BASIC level 1.63 (0.53 to 2.85), own-spending component -0.56 (-9.98 to 7.36).
  In the direct-simulation tests, 0.34-0.43% of the refits did not converge. Before seeing the outcomes, the priors
  implied a median 17% of ACOs renewing early (95% range 1% to 70%). In [posterior predictive][ppc] checks the
  observed 24 early renewers fall inside the replicated 95% range (14 to 37), and in the top predicted decile 57%
  renewed against 45% predicted.
* **The own-spending coefficient is the prior.** Its interval is the prior's 95% range, because the measurement
  error ($\sigma_v$ = 4.38) is larger than the variable's spread among stayers (SD 3.3): the model can learn almost
  nothing about it. Without the measurement-error model (a robustness check) it is -0.64 (-1.51 to 0.23).
* **Read the sizes with care.** The power analysis gave H3 a 17% (pull) and 14% (BASIC level) chance of detecting a
  log-odds difference of 0.5. An estimate that passes a test with power that low is likely to overstate the true
  effect (a "type M" error, [Gelman and Carlin 2014][gelman-carlin2014][^gelman-carlin2014]), so the directions are the result, and
  coefficients near 1.3 ([odds ratios][odds-ratio] near 4) are probably too large.

### H4: spending after renewal

29 early renewers and 276 comparison ACOs not yet renewed (one stayer has no spending value in any post-period
year; [`did.json`][res-did][^results]). The outcome is the change in log per-capita spending from
PY2020-PY2021 to PY2022-PY2024, shown as a percent difference in spending growth.

| Estimate | Early renewers minus comparison | 95% credible interval | p |
|---|---|---|---|
| **H4** | **-0.4%** | **-4.0% to +2.5%** | **0.78** |
| Pre-trend (PY2020 to PY2021) | +0.7% | -2.3% to +4.9% | 0.58 |
| Trend-adjusted | -4.0% | -12.0% to +2.7% | 0.14 |

* **Verdict (rule 5).** "No detectable difference"; the minimum detectable effect is 3.8 log points (about 3.9%).
* **Not read as an effect.** The pre-trend test is not evidence against parallel trends (p = 0.58), but the
  equivalence condition does not hold: the scaled pre-trend bound, 2.41 years times 0.048, is 0.115 log points
  (a log difference; about 12%),
  far above the H4 estimate of 0.004. The condition needed an estimate above 0.115 log points, about 12% and three
  times the minimum detectable effect. With one pre-period, that threshold was a property of the design, fixed at
  registration: for any estimate near zero, the rule could only end in "not read as an effect". A trend difference
  of the size the pre-period allows could hide an effect in either direction. So H4 is reported as a difference in
  spending changes that cannot be told apart from a continuation of a pre-period difference in trends.
* **What the data do bound.** Under parallel trends, the H4 interval (-4.0% to +2.5%) rules out a drop in spending
  growth of more than about 4% or a rise of more than about 2.5%. The trend-adjusted interval (-12.0% to +2.7%) is too wide to be
  informative.
* **Attrition.** The plan requires it by group and year ([section 4.5][plan-4.5][^plan]), and it is uneven:

    | Group and status | PY2022 | PY2023 | PY2024 |
    |---|---|---|---|
    | Early renewers (29): included | 29 | 28 | 25 |
    | Early renewers: left the program | 0 | 1 | 1 |
    | Early renewers: renewed again | 0 | 0 | 3 |
    | Stayers (277): included | 276 | 222 | 162 |
    | Stayers: left the program | 0 | 46 | 72 |
    | Stayers: renewed (no longer "not yet renewed") | 0 | 8 | 42 |
    | Stayers: no spending value | 1 | 1 | 1 |

    By PY2024, 115 of 277 stayers (42%) had dropped out of the comparison, against 4 of 29 early renewers (14%).
    Exits are unlikely to be random: the ACOs that left after PY2021 had the lowest savings rates (see
    [Exploratory](#exploratory)). The balanced panel, ACOs with all five years, is the check on this: -1.6% (-5.6%
    to +1.6%), p = 0.30.

### Registered and conventional methods

Every verdict agrees with its conventional counterpart (reported only; it would not have changed a decision;
[`conventional.json`][res-conventional][^results]):

| Claim | Registered | Conventional |
|---|---|---|
| H2b | supported (p < 0.001) | supported: OLS with HC2 errors +3.3 (1.3 to 5.4), p = 0.001 |
| H2a | contradicted (p = 0.003) | contradicted: OLS with HC2 errors -2.1 (-3.8 to -0.4), p = 0.018 |
| H3 regional pull | supported (p = 0.002) | supported: logistic odds ratio 4.0 (1.2 to 13.4), p = 0.024 |
| H3 own-spending component | undetermined (p = 0.19) | undetermined: odds ratio 0.53 (0.19 to 1.44), p = 0.21 |
| H3 higher BASIC level | supported (p = 0.003) | supported: odds ratio 4.8 (1.5 to 15.6), p = 0.009 |
| H4 | no detectable difference (p = 0.78) | two-way fixed effects -1.5% (-5.4% to +2.4%), p = 0.44 |

The conventional p-values are mostly larger than the resampling ones, but no verdict changes. The Welch t-tests
agree too: H2b +3.2 (1.1 to 5.3), p = 0.004; H2a -2.1 (-3.9 to -0.2), p = 0.028.

### Interactive results

<link rel="stylesheet" href="/static/20261026-preregistered-mssp-early-renewal/dashboard.css">
<div id="mssp-dashboard" class="mssp-dash" aria-live="polite"><p>Loading the interactive results...</p></div>
<script src="/static/20261026-preregistered-mssp-early-renewal/dashboard.js" defer></script>

### Results notebook

The main results tables and figures are also in a [marimo][marimo][^sw-marimo]
[notebook](/static/20261026-preregistered-mssp-early-renewal/results.html)
([`report/results_notebook.py`][notebook-src][^results]). It reads the results files through the dashboard's data
builder and recomputes nothing: provenance (each results file's commit and sha256), validation, the group
comparisons, H3, H4, the agreement table, robustness and exploratory results. This post is the authoritative report;
some details added after the critical review (such as the H4 attrition table) are only here. The notebook page loads
marimo's front end from [jsDelivr][jsdelivr], so the [OSF project](https://osf.io/z4an5/) also holds a PDF and a
Jupyter notebook with its outputs saved, which need no CDN. The files below were exported on 2026-10-27, after the
review changed the H4 wording, and replaced the first upload on OSF, which keeps the earlier versions in each file's
history:

| File (on OSF) | sha256 |
|---|---|
| [`results.html`](https://osf.io/m5qkx/) | `65fe501e57ceae5eba3fc76533f81a1047771c3ef7ff87db20f72559b93c877a` |
| [`results.ipynb`](https://osf.io/aczts/) | `761f0306fa2b4a5a3ab373b72a71da4f510192810e2b198e6687fbc9f6ee228f` |
| [`results.pdf`](https://osf.io/247qu/) | `32bc555e591b253d7b7aa142a4946bc69e2566fd402a88c5cd9686c69f341630` |

## Robustness

The robustness checks of plan sections [5.5][plan-5.5][^plan] and [5.8][plan-5.8] ([`robustness.json`][res-robustness][^results]
and [`did.json`][res-did]). The robustness stage ran alongside the confirmatory one, and its results were read only
together with the confirmatory results. They do not change the verdicts; the dashboard above shows each one next to its confirmatory estimate.

* **H2b keeps its direction in every check.** Difference in [medians][median] +2.8 (p < 0.001); 2020-01-01 cohort
  only +3.7 (p = 0.001); unadjusted county spending +6.9 (p = 0.002); Bayesian regression with cohort only +2.1 (0.5
  to 3.8) and with track, level and size added +2.2 (0.7 to 3.8). The size depends on the estimator: the regression
  estimates are below the minimum detectable effect and well below the +3.4 difference in means, which suggests a
  few large values among early renewers carry part of it, and the unadjusted version is twice as large.
* **H2a is weaker by medians.** -1.4, p = 0.085; the other checks keep it below zero with p < 0.05 (cohort only
  p = 0.043, benchmark years 2-3 only p = 0.012, complete cases p = 0.005), though the adjusted regression's interval
  reaches zero (-2.6 to 0.02).
* **H1 is weaker with adjustment.** By medians +1.4 points (p = 0.061), and in the adjusted regression +1.2 (-0.1
  to 2.6).
* **H3's directions hold, with two intervals at zero.** The Firth regression gives the same verdicts (pull p = 0.004,
  BASIC level p = 0.006, own-spending p = 0.18). The pull coefficient's interval reaches zero with the 2020-01-01
  cohort only (1.15, -0.02 to 2.39) and with unadjusted county spending (0.75, -0.02 to 1.56); the BASIC level's
  stays above zero in every check.
* **H4 shows no detectable difference in any check.** Risk-adjusted outcome +0.3% (p = 0.85), balanced panel -1.6%
  (p = 0.30), propensity-weighted -0.5% (p = 0.67, largest weight 0.83), 2020-01-01 cohort only -2.9% (p = 0.13),
  trend-adjusted -4.0% (p = 0.14).

## Exploratory

Labeled exploratory in the plan ([section 5.6][plan-5.6][^plan]; [`exploratory.json`][res-exploratory][^results]): no predictions and no verdicts, and nothing here was used to choose
what is reported above.

* **Other measures of the regional pull.** Weighted by the phase-in weight $w$, early renewers minus stayers is +1.6
  (0.7 to 2.6); the capped regional component, +1.6 (0.9 to 2.2). Both are positive in H3 too.
* **[Census region][census][^census]** adds nothing to the decision model: Midwest, South and West, each against the Northeast, all
  have intervals that include zero, and the pull and BASIC-level coefficients barely move (1.43 and 1.32).
* **Leavers.** The 28 ACOs that left after PY2021 had the lowest savings rates (mean 2.7 points in PY2020, against
  6.4 for early renewers and 4.6 for stayers), and a regional pull (for 20 of the 28) similar to early renewers' on
  average (4.8 against 5.0) but much lower in the median (2.0 against 3.5).
* **The two early renewers already in ENHANCED,** for whom renewing could not raise the sharing rate, fall between the
  26th and 68th percentile of stayers on every variable (savings rate at the 38th and 65th, regional pull at the 26th
  and 61st).
* **Spending by agreement year** rises for every group; early renewers from 2020 agreements started lower and stayed
  lower. As the design noted, benchmark-year status cannot be separated from tenure here, so this is description only.

## Implications and open questions

For program design, the results suggest that the early-renewal option let ACOs choose when to reset. The ones that
used it were those whose regions spent more relative to their benchmarks and those at higher BASIC levels, for whom
ENHANCED was a short step. That is selection into an option the program created; it is not evidence that renewing
changed spending. Three questions remain open:

* **What did early renewal cost Medicare,** through higher benchmarks or larger shared-savings payments? This study
  does not estimate it.
* **Did the 2024 rules change who renews early?** The prior savings adjustment and the offset to negative regional
  adjustments weaken the own-spending penalty that early renewers faced in 2022.
* **How much of the choice was the sharing rate rather than the benchmark?** In these data the two came with the same
  decision; a period in which ACOs could move to ENHANCED without resetting would separate them.

## Deviations

None affecting any result. All seven stages (validate, power, confirm, robustness, did, conventional, exploratory) ran with code identical
to the registered commit [`a4064f5`][code][^code], and each results file was committed before its estimates were read. Each results
file records the commit it ran at, and
[`DEVIATIONS.md`][deviations] (the current log, on the main branch)
gives the command that checks it against the registered code.

Two things changed after the last stage ran, and no result was produced with either: the dashboard's reporting
script ([fixed in `dd8c279`][dashboard-fix]), which had shown PY2021 savings rates 100 times too large (they were already percents), and the lockfile
`uv.lock`, which took security updates to filelock and virtualenv from the site's main branch. The lockfile is a
registered file, so that change is the one entry in `DEVIATIONS.md`; rerunning the analysis exactly as registered
uses the lockfile at `a4064f5`.

One sentence in the registered plan's background is imprecise, though nothing in the analysis depends on it.
[Section 1.1][plan-1.1][^plan] says renewing is "the only way for a BASIC-track ACO to enter the ENHANCED track, which
shares 75% of savings and losses". ENHANCED shares [75% of savings][cfr-610-rate][^cfr-425-610] but
[up to 75% of losses][cfr-610-loss], and the bar on moving from BASIC to ENHANCED within an agreement period is in
the [2018 rule's preamble][fr-pathways-track][^fr-2018], not the regulation's text ([Design](#two-motives-and-why-the-savings-rate-cannot-separate-them)).

## Limitations

* **Bundled motives.** In these data, renewing early and moving to ENHANCED are one choice, so no test here can
  separate the sharing-rate motive from the reset motive. The regional pull has no term for benchmark-year spending,
  but it is not free of the ACO's own data, and it is not a test that rules the other motive out.
* **What the regional pull also measures.** Its benchmark $B$ was set from the ACO's earlier spending, and its
  regional spending is adjusted with the ACO's own PY2021 risk scores, so it carries a coding-intensity term. A high
  pull therefore partly measures how low-cost the ACO has been relative to its region, which is also a plausible
  reason to want ENHANCED's 75% sharing rate. The case-mix adjustment matters and has no published counterpart to
  validate it: unadjusted, the H2b difference is +6.9 rather than +3.4, and H3's pull interval reaches zero (0.75,
  -0.02 to 1.56).
* **An approximate benchmark.** The expected gain is rebuilt from public files; the validation bounds the error but
  does not remove it, and the regional part has no published counterpart to check against. The own-spending
  component's estimated error is larger than its spread among stayers (see [Validation](#validation-of-the-benchmark-approximation)),
  so H2a and the total expected gain are weak evidence at the level of one ACO.
* **Few early renewers.** 29 ACOs, 24 in the decision model: the power analysis shows what can and cannot be detected,
  and the supported H3 coefficients are probably overestimates (see H3).
* **Exclusions above the plan's 10% line.** The expected-gain variables (H2a, H2b, H3 and the gain itself) could not
  be built for 3 of 29 early renewers (10.3%) and 36 of 277 stayers (13.0%); the plan requires reporting this as a
  limitation when either group passes 10% ([section 3][plan-3][^plan]). In every one of the 39, CMS hides the ACO's count of
  assigned [ESRD][esrd] (kidney failure) beneficiaries in every county of the
  [2021 county assignment file][data-assigned][^data-assigned] ([it suppresses counts of 1 to 10][suppression-archive][^suppression]),
  so the ESRD part of regional spending has no county weights; for 15 the aged/dual counts are hidden too.
  These details and the size medians below come from a diagnostic query run after the results, outside the
  registered pipeline; they are not in the results files. The
  plan's fill rules cover hidden cells in the results files, not fully hidden county weights, so these ACOs are
  excluded and counted, as registered. They are smaller ACOs (median 6,702 and 8,578 assigned beneficiaries for
  excluded early renewers and stayers, against 10,757 and 15,649 for those included), so H2a, H2b and H3 describe
  the larger ACOs. Separately, 1 early renewer and 3 stayers had hidden values filled by the registered rules.
* **One COVID-era pre-period** for H4, which is why the equivalence condition, not a pre-trend test, decides whether
  H4 is read as an effect.
* **Do these results apply today?** They describe the rules for agreements that began in 2022
  ([42 CFR 425.601][cfr-601]). For agreement periods starting January 1, 2024 or later, benchmarks are set under
  [42 CFR 425.652][cfr24-652][^cfr-2024], which changes the trade-off studied here. An ACO that saved in the years
  before its new agreement can receive a [prior savings adjustment][cfr24-658] of up to half its average per-capita
  savings (capped at 5% of national per-capita spending), and its benchmark gets the higher of that and the regional
  adjustment ([425.652(a)(8)][cfr24-652-a8]). [Negative regional adjustments are partly offset][cfr24-656], and the
  annual update blends in a fixed projected trend, the Accountable Care Prospective Trend
  ([425.652(b)][cfr24-652-b]). Under these rules a reset costs an ACO that has been beating its benchmark less, so the
  incentive to renew early, and which ACOs do so, may well differ.
* **Uneven attrition in H4.** By PY2024 the comparison group had lost 42% of its ACOs, to exits and later renewals,
  against 14% of early renewers (see [H4](#h4-spending-after-renewal)), so its later years are increasingly selected.
* **Other design threats.**
    * *Survivorship:* the base population needs a PY2021 enrollment record, so ACOs in these cohorts that left
      before PY2021 are not in it.
    * *Anticipation:* the decision to renew was made during 2021, which is both the last pre-period year for H4 and
      the third benchmark year of the new benchmark.
    * *Composition:* a renewing ACO can change its participant list, so H4's spending can move through who is
      assigned rather than through behavior; the risk-adjusted version addresses this only in part.
    * *Leavers:* leaving the program is a third choice, and comparing early renewers only with stayers sets it
      aside.

## Reproduce

Everything needed to rerun the study, check it, or adapt it is public: the code, the CMS data (with an archived copy),
and the committed results. The steps below were run, exactly as written, from a fresh clone on macOS on 2026-10-27.
The study's [README][readme] has the same steps with more detail on adapting the analysis.

**What you need.** [git](https://git-scm.com/), [uv][uv][^sw-uv] (on macOS or Linux:
`curl -LsSf https://astral.sh/uv/install.sh | sh`; for Windows see its
[installation page](https://docs.astral.sh/uv/getting-started/installation/)), about 1 GB of disk, and an internet
connection. uv installs Python 3.12 and the exact package versions pinned in `uv.lock` the first time it runs.
Linux should behave the same as macOS; Windows is untested. Run every command from the repository folder.

**1. Get the code (seconds).** The repository also holds this website, so clone only the study:

```bash
git clone --filter=blob:none --sparse https://github.com/stharrold/stharrold.github.io.git
cd stharrold.github.io
git sparse-checkout set analysis/mssp-benchmark-ratchet
```

**2. Get the data (under a minute, about 40 MB).** This downloads the 40 CMS files listed in
[`data-snapshot.tsv`][snapshot][^code], keeps each one only if its sha256 matches, and puts them where the pipeline
looks (`~/.cache/stharrold-github-io/mssp-snapshot-2026-10-22/`). It should end with
`All 40 files match data-snapshot.tsv`.

```bash
uv run python analysis/mssp-benchmark-ratchet/fetch_snapshot.py
```

**3. Check the installation (about 8 minutes).** The first run also installs the analysis packages. It should end
with `81 passed`.

```bash
uv run --group analysis pytest analysis/mssp-benchmark-ratchet/tests
```

**4. Rerun the analysis.** Each stage writes one results file into `--out-dir` and refuses to start until the
files it depends on are there, so run them in this order. Times are for 5 worker processes on an Apple M-series
Mac.

| Stage | Writes | Time |
|---|---|---|
| `validate` | `validation.json` | seconds |
| `power` | `power.json` | about 40 minutes |
| `confirm` | `confirm.json` | about 17 hours |
| `robustness` | `robustness.json` | minutes |
| `did` | `did.json` | under a minute |
| `conventional` | `conventional.json` | seconds |
| `exploratory` | `exploratory.json` | about 2 minutes |

```bash
OUT=~/mssp-rerun
for stage in validate power confirm robustness did conventional exploratory; do
  uv run --group analysis python analysis/mssp-benchmark-ratchet/ratchet/run.py $stage --out-dir $OUT || break
done
```

`--workers N` sets the number of processes (default: half the cores). To rerun a later stage without waiting 17
hours for `confirm`, first copy the committed files it needs into `$OUT`, for example
`cp analysis/mssp-benchmark-ratchet/results/{validation,power,confirm}.json $OUT/` before `did`.

**5. Compare with the published results (seconds).** This checks every number in each rerun file against the
committed one and prints `same`, or the values that differ.

```bash
uv run python analysis/mssp-benchmark-ratchet/compare_results.py $OUT
```

**What the test run showed.** Steps 1-3 worked as written, and the `validate` stage reproduced the committed file
exactly. The `power` stage reproduced every deterministic number (the standard deviations and minimum detectable
effects) but not the simulated ones: H1's simulated power came out 0.776 against the committed 0.804, and H3's
detection shares 15% against 17% (pull) and 15% against 14% (BASIC level). The cause is that the analysis table is read
without a fixed row order, so the same seeded random draws fall on the ACOs in a different order in each run. Every
stage that resamples or simulates (the bootstrap intervals, permutation p-values and MCMC fits) therefore varies
slightly between runs. The differences are of the size of the simulation error (about 1.6 points for a detection
share from 500 datasets, about 0.002 for a p-value of 0.03 from 10,000 shuffles), far from changing any verdict.
`compare_results.py` lists each differing value so you can judge.

**If something goes wrong.**

* *The fetch script prints `changed` for a file.* CMS has replaced that file; the script takes it from the archived
  snapshot on OSF instead ([osf.io/53aqd](https://osf.io/53aqd/)). `--archive-only` takes every file from there.
* *A stage stops with a message about a missing file.* An earlier stage has not written its results into `$OUT`
  yet: run the stages in order, or copy the committed files as in step 4.
* *`--quick` is refused.* It uses small test settings and works only on synthetic data, by design.

**Adapt it.** The README's "Adapt it" table points to the file behind each part of the analysis (who is in each
group, each constructed variable, each statistical method, the settings and seeds). It also shows a dry run on
[synthetic data][synthetic] that takes minutes, and explains how to close the outcome lock in a copy, so that a
variant can be pre-registered in turn rather than reported as exploratory.

**Cite it.** The repository's `CITATION.cff` gives the registration (DOI 10.17605/OSF.IO/C53W9) as the preferred
citation.

The results notebook runs outside the locked environment, with its tools pinned on the command line. For the other
two exports, replace `html` with `ipynb --include-outputs` or `pdf`:

```bash
uv run --with marimo==0.25.2 --with matplotlib==3.11.2 --with nbformat==5.11.1 \
    --with 'nbconvert[webpdf]==7.17.2' --with playwright==1.61.0 \
    marimo export html analysis/mssp-benchmark-ratchet/report/results_notebook.py -o results.html
```

## What review caught before registration

Independent reviews of the plan and code, each given only the files, found problems that would have been permanent
once registered:

* **The first primary test was mechanically tied to past savings.** The "regional component" contains the
  own-spending part with a negative sign; the primary test became the regional pull.
* **Raw regional spending is not what CMS compares.** The regulation
  [risk-adjusts regional spending to the ACO's case mix][cfr-601-regional-risk][^cfr-425-601], and CMS restates benchmark years to
  the latest year's risk ([specifications, version 10][spec-v10][^spec-v10], section 4.1.2); both were implemented, with the unadjusted version
  kept as a robustness check.
* **Suppressed values.** The results files [hide small cells][suppression-archive][^suppression], and the first rule dropped any ACO with one hidden
  value. A fallback chain (exact recovery from totals, then shown years, then a regional ratio) replaced it, with a
  complete-case check.
* **A permutation test that tests the wrong null** in a multi-predictor model, replaced by direct simulation (above).
* **Pre-trend testing with one pre-period**, replaced by the equivalence condition (above).
* **A status line** in the plan that still said "DRAFT ... Not yet registered", and would have been frozen into the
  public record.

## Use of AI tools

The author chose the question, hypotheses and decision rules, approved and registered the plan, ran the analysis, and
is responsible for the results. [Claude Code][claude-code] (Claude Opus 5.5; [Anthropic][anthropic]) drafted the analysis code and parts of this
post under the author's direction, and separate instances reviewed the plan and code before registration.

## References

Every source cited above, numbered in order of first citation; each &#8617;&#xFE0E; returns to a place it is cited.
General terms link to Wikipedia in the text instead.

///Footnotes Go Here///

[mssp]: https://www.cms.gov/medicare/payment/shared-savings-program
[aco-cms]: https://www.cms.gov/priorities-innovation-key-concepts-accountable-care-accountable-care-organizations
[puf]: https://www.cms.gov/research-statistics-data-and-systems/files-for-order/nonidentifiabledatafiles
[esrd]: https://www.niddk.nih.gov/health-information/kidney-disease/kidney-failure/what-is-kidney-failure
[dual]: https://www.cms.gov/medicare/medicaid-coordination/about
[census]: https://www2.census.gov/geo/pdfs/maps-data/maps/reference/us_regdiv.pdf
[suppression]: https://www.hhs.gov/guidance/document/cms-cell-suppression-policy
[suppression-archive]: https://web.archive.org/web/20250516214605/https://www.hhs.gov/guidance/document/cms-cell-suppression-policy
[spec-v10]: https://www.cms.gov/files/document/medicare-shared-savings-program-shared-savings-and-losses-and-assignment-methodology-specifications.pdf-1
[spec-v10-archive]: https://web.archive.org/web/20260510084527/https://www.cms.gov/files/document/medicare-shared-savings-program-shared-savings-and-losses-and-assignment-methodology-specifications.pdf-1
[fr-pathways]: https://www.federalregister.gov/documents/2018/12/31/2018-27981/medicare-program-medicare-shared-savings-program-accountable-care-organizations-pathways-to-success
[fr-pathways-track]: https://www.federalregister.gov/citation/83-FR-67859
[fr-covid]: https://www.federalregister.gov/documents/2020/05/08/2020-09608/medicare-and-medicaid-programs-basic-health-program-and-exchanges-additional-policy-and-regulatory#page-27574
[cfr24-652]: https://www.ecfr.gov/on/2024-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.652
[cfr24-652-a8]: https://www.ecfr.gov/on/2024-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.652#p-425.652%28a%29%288%29
[cfr24-652-b]: https://www.ecfr.gov/on/2024-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.652#p-425.652%28b%29
[cfr24-656]: https://www.ecfr.gov/on/2024-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.656#p-425.656%28c%29%284%29
[cfr24-658]: https://www.ecfr.gov/on/2024-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.658#p-425.658%28c%29%281%29
[cfr-425]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425
[cfr-20-renewing]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-A/section-425.20#p-425.20%28Renewing%20ACO%29%282%29
[cfr-200-b4]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-C/section-425.200#p-425.200%28b%29%284%29%28ii%29
[cfr-200-b5]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-C/section-425.200#p-425.200%28b%29%285%29
[cfr-200-ext]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-C/section-425.200#p-425.200%28b%29%283%29%28ii%29%28B%29
[cfr-220]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-C/section-425.220#p-425.220%28a%29
[cfr-226]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-C/section-425.226#p-425.226%28a%29%282%29%28i%29
[cfr-600-stay-2023]: https://www.ecfr.gov/on/2023-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.600#p-425.600%28a%29%284%29%28i%29%28B%29%282%29%28vi%29
[cfr-600-glide]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.600#p-425.600%28a%29%284%29%28i%29%28B%29%282%29
[cfr-600-entry]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.600#p-425.600%28a%29%284%29%28i%29%28B%29%281%29%28i%29
[cfr-600-pause-2021]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.600#p-425.600%28a%29%284%29%28i%29%28B%29%282%29%28iii%29
[cfr-600-pause-2022]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.600#p-425.600%28a%29%284%29%28i%29%28B%29%282%29%28iv%29
[cfr-605-levels]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.605#p-425.605%28d%29%281%29
[cfr-610-rate]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.610#p-425.610%28d%29%282%29
[cfr-610-loss]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.610#p-425.610%28f%29%282%29
[cfr-601]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601
[cfr-601-reset]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28e%29%281%29
[cfr-601-equal]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28e%29%282%29%28i%29
[cfr-601-risk]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28a%29%283%29
[cfr-601-trend]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28a%29%285%29
[cfr-601-regional-weight]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28d%29%281%29
[cfr-601-regional-risk]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28a%29%288%29%28i%29%28C%29
[cfr-601-adj]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28a%29%288%29
[cfr-601-phase]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28f%29
[cfr-601-cap]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28a%29%288%29%28ii%29%28C%29
[cfr-601-types]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28a%29%282%29
[cfr-601-shares]: https://www.ecfr.gov/on/2022-01-01/title-42/chapter-IV/subchapter-B/part-425/subpart-G/section-425.601#p-425.601%28d%29%283%29
[data-acos]: https://data.cms.gov/medicare-shared-savings-program/accountable-care-organizations
[data-results]: https://data.cms.gov/medicare-shared-savings-program/performance-year-financial-and-quality-results
[data-county]: https://data.cms.gov/medicare-shared-savings-program/county-level-aggregate-expenditure-and-risk-score-data-on-assignable-beneficiaries
[data-assigned]: https://data.cms.gov/medicare-shared-savings-program/number-of-accountable-care-organization-assigned-beneficiaries-by-county
[dict-results-2021]: https://data.cms.gov/sites/default/files/2025-03/6715138f-a3d5-4156-9055-9249ab6d2136/Data_Dictionary-Medicare_Shared_Savings_Program-Performance_Year_Financial_and_Quality_Results_2021.pdf
[file-py2020]: https://data.cms.gov/sites/default/files/2023-10/316a5425-951f-4314-84dd-36f59499bae7/Performance_Year_Financial_and_Quality_Results_2020_suppress.csv
[file-py2021]: https://data.cms.gov/sites/default/files/2023-09/e93c0c3b-9402-406f-ab49-61ec820ba0bf/Performance_Year_Financial_and_Quality_Results_2021_suppress.csv
[code]: https://github.com/stharrold/stharrold.github.io/tree/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet
[snapshot]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/data-snapshot.tsv
[snapshot-py]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/ratchet/snapshot.py
[synthetic]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/ratchet/synthetic.py
[run]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/ratchet/run.py
[tests]: https://github.com/stharrold/stharrold.github.io/tree/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/tests
[dbt-dir]: https://github.com/stharrold/stharrold.github.io/tree/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/dbt
[plan-file]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md
[plan-1.1]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#11-background
[plan-1.3]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#13-hypotheses
[plan-3]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#3-sample-and-groups
[plan-4.3]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#43-expected-benchmark-gain-from-resetting-constructed
[plan-4.4]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#44-validation-of-the-approximation-run-before-h2a-h2b-and-h3-are-estimated
[plan-4.5]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#45-spending-panel-for-h4
[plan-5.4]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#54-h3-bayesian-decision-model-basic-track-acos
[plan-5.5]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#55-robustness-all-reported
[plan-5.6]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#56-exploratory-and-descriptive-labeled-as-such-in-the-write-up
[plan-5.7]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#57-comparison-with-conventional-methods-reported-not-used-for-decisions
[plan-5.8]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#58-h4-effect-of-early-renewal-on-spending-difference-in-differences
[plan-6]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#6-power-analysis-run-after-registration-before-any-confirmatory-estimate
[plan-7]: https://github.com/stharrold/stharrold.github.io/blob/a4064f592a492d971ce3c27e95afb3050e6bc01d/analysis/mssp-benchmark-ratchet/PREREGISTRATION.md#7-decision-rules-fixed-before-seeing-results
[registration-md]: https://github.com/stharrold/stharrold.github.io/blob/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/REGISTRATION.md
[results-dir]: https://github.com/stharrold/stharrold.github.io/tree/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/results
[res-validation]: https://github.com/stharrold/stharrold.github.io/blob/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/results/validation.json
[res-power]: https://github.com/stharrold/stharrold.github.io/blob/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/results/power.json
[res-confirm]: https://github.com/stharrold/stharrold.github.io/blob/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/results/confirm.json
[res-robustness]: https://github.com/stharrold/stharrold.github.io/blob/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/results/robustness.json
[res-did]: https://github.com/stharrold/stharrold.github.io/blob/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/results/did.json
[res-conventional]: https://github.com/stharrold/stharrold.github.io/blob/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/results/conventional.json
[res-exploratory]: https://github.com/stharrold/stharrold.github.io/blob/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/results/exploratory.json
[notebook-src]: https://github.com/stharrold/stharrold.github.io/blob/eceda2ab9ab48330fee70d227e1ca7b4ad44369b/analysis/mssp-benchmark-ratchet/report/results_notebook.py
[readme]: https://github.com/stharrold/stharrold.github.io/blob/src_master/analysis/mssp-benchmark-ratchet/README.md#reproduce-and-adapt
[deviations]: https://github.com/stharrold/stharrold.github.io/blob/src_master/analysis/mssp-benchmark-ratchet/DEVIATIONS.md
[dashboard-fix]: https://github.com/stharrold/stharrold.github.io/commit/dd8c27904e3dfa87840d9debffb663bb1cf64906
[git-dates]: https://git-scm.com/docs/git-commit#_date_formats
[osf-registries]: https://osf.io/registries
[osf-api]: https://developer.osf.io/
[sha2]: https://en.wikipedia.org/wiki/SHA-2
[natural-exp]: https://en.wikipedia.org/wiki/Natural_experiment
[multicol]: https://en.wikipedia.org/wiki/Multicollinearity
[did-wiki]: https://en.wikipedia.org/wiki/Difference_in_differences
[credible]: https://en.wikipedia.org/wiki/Credible_interval
[spearman]: https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient
[mape]: https://en.wikipedia.org/wiki/Mean_absolute_percentage_error
[bb-wiki]: https://en.wikipedia.org/wiki/Bootstrapping_(statistics)#Bayesian_bootstrap
[dirichlet]: https://en.wikipedia.org/wiki/Dirichlet_distribution
[perm-wiki]: https://en.wikipedia.org/wiki/Permutation_test
[pvalue]: https://en.wikipedia.org/wiki/P-value
[logistic]: https://en.wikipedia.org/wiki/Logistic_regression
[logit]: https://en.wikipedia.org/wiki/Logit
[prior]: https://en.wikipedia.org/wiki/Prior_probability#Weakly_informative_priors
[student-t]: https://en.wikipedia.org/wiki/Student%27s_t-distribution
[eiv]: https://en.wikipedia.org/wiki/Errors-in-variables_model
[param-boot]: https://en.wikipedia.org/wiki/Bootstrapping_(statistics)#Parametric_bootstrap
[mcmc]: https://en.wikipedia.org/wiki/Markov_chain_Monte_Carlo
[regmean]: https://en.wikipedia.org/wiki/Regression_toward_the_mean
[ipw]: https://en.wikipedia.org/wiki/Inverse_probability_weighting
[welch-wiki]: https://en.wikipedia.org/wiki/Welch%27s_t-test
[ols]: https://en.wikipedia.org/wiki/Ordinary_least_squares
[hc]: https://en.wikipedia.org/wiki/Heteroskedasticity-consistent_standard_errors
[fe]: https://en.wikipedia.org/wiki/Fixed_effects_model
[cluster]: https://en.wikipedia.org/wiki/Clustered_standard_errors
[power]: https://en.wikipedia.org/wiki/Power_(statistics)
[median]: https://en.wikipedia.org/wiki/Median
[odds-ratio]: https://en.wikipedia.org/wiki/Odds_ratio
[ppc]: https://en.wikipedia.org/wiki/Posterior_predictive_distribution
[pymc]: https://www.pymc.io/
[arviz-rhat]: https://python.arviz.org/projects/stats/en/stable/api/generated/arviz_stats.rhat.html
[arviz-ess]: https://python.arviz.org/projects/stats/en/stable/api/generated/arviz_stats.ess.html
[statsmodels]: https://www.statsmodels.org/
[statsmodels-logit]: https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.Logit.html
[firthmodels]: https://github.com/jzluo/firthmodels
[dbt]: https://www.getdbt.com/
[dbt-tests]: https://docs.getdbt.com/docs/build/data-tests
[duckdb]: https://duckdb.org/
[uv]: https://docs.astral.sh/uv/
[uv-lock]: https://docs.astral.sh/uv/concepts/projects/layout/#the-lockfile
[numpy-seed]: https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html
[numpy-parallel]: https://numpy.org/doc/stable/reference/random/parallel.html
[marimo]: https://marimo.io/
[jsdelivr]: https://www.jsdelivr.com/
[claude-code]: https://code.claude.com/docs/en/overview
[anthropic]: https://www.anthropic.com/
[vdp-video]: https://www.youtube.com/watch?v=Iq9DzN6mvYA
[vdp-slides]: https://speakerdeck.com/jakevdp/statistics-for-hackers
[rose2016]: https://doi.org/10.1377/hlthaff.2015.1026
[douven2015]: https://doi.org/10.1377/hlthaff.2014.0444
[lyu2023]: https://doi.org/10.1377/hlthaff.2022.01061
[chen2025]: https://doi.org/10.1086/726748
[ying2024]: https://doi.org/10.1093/haschl/qxad093
[ying2023]: https://doi.org/10.1007/s11606-022-07947-x
[moloci2021]: https://doi.org/10.1007/s11606-020-06424-7
[research]: https://github.com/stharrold/stharrold.github.io/tree/src_master/analysis/mssp-benchmark-ratchet/research
[callaway2021]: https://doi.org/10.1016/j.jeconom.2020.12.001
[firth1993]: https://doi.org/10.1093/biomet/80.1.27
[gelman2008]: https://doi.org/10.1002/sim.3107
[gelman-carlin2014]: https://doi.org/10.1177/1745691614551642
[gelman-prior2008]: https://doi.org/10.1214/08-AOAS191
[nuts]: https://jmlr.org/papers/v15/hoffman14a.html
[lakens2017]: https://doi.org/10.1177/1948550617697177
[mackinnon1985]: https://doi.org/10.1016/0304-4076%2885%2990158-7
[nosek2018]: https://doi.org/10.1073/pnas.1708274114
[phipson2010]: https://doi.org/10.2202/1544-6115.1585
[rambachan2023]: https://doi.org/10.1093/restud/rdad018
[rosenbaum1983]: https://doi.org/10.1093/biomet/70.1.41
[roth2022]: https://doi.org/10.1257/aeri.20210236
[rubin1981]: https://doi.org/10.1214/aos/1176345338
[simmons2011]: https://doi.org/10.1177/0956797611417632
[vehtari2021]: https://doi.org/10.1214/20-BA1221
[welch1947]: https://doi.org/10.1093/biomet/34.1-2.28

[^cms-mssp]: CMS. [Shared Savings Program][mssp]. cms.gov.
[^cms-aco]: CMS. [Accountable Care Organizations (ACOs)][aco-cms]. cms.gov.
[^cfr-425-601]: 42 CFR 425.601, Establishing, adjusting, and updating the benchmark for agreement periods beginning on July 1, 2019, and in subsequent years. eCFR, as in force on 2022-01-01. [Section][cfr-601]; paragraphs cited: [(a)(3)][cfr-601-risk], [(a)(5)][cfr-601-trend], [(a)(2)][cfr-601-types], [(a)(8)][cfr-601-adj], [(a)(8)(i)(C)][cfr-601-regional-risk], [(a)(8)(ii)(C)][cfr-601-cap], [(d)(1)][cfr-601-regional-weight], [(d)(3)][cfr-601-shares], [(e)(1)][cfr-601-reset], [(e)(2)(i)][cfr-601-equal], [(f)][cfr-601-phase].
[^cfr-425-20]: 42 CFR 425.20, Definitions. eCFR, as in force on 2022-01-01. Paragraphs cited: ["Renewing ACO" (2)][cfr-20-renewing].
[^data-acos]: CMS. [Accountable Care Organizations][data-acos]: Shared Savings Program enrollment, one file per year, 2014-2026. data.cms.gov.
[^cfr-425-610]: 42 CFR 425.610, Calculation of shared savings and losses under the ENHANCED track. eCFR, as in force on 2022-01-01. Paragraphs cited: [(d)(2)][cfr-610-rate], [(f)(2)][cfr-610-loss].
[^registration]: Harrold, S. (2026). Why did Medicare ACOs reset their benchmarks early? A pre-registered analysis of early renewal in the Medicare Shared Savings Program. OSF Registries, registered 2026-10-26. [doi:10.17605/OSF.IO/C53W9](https://doi.org/10.17605/OSF.IO/C53W9). Editable project with the notebook exports: [osf.io/z4an5](https://osf.io/z4an5/).
[^code]: Harrold, S. (2026). [`analysis/mssp-benchmark-ratchet/`][code], the registered analysis code at commit `a4064f5`: [`data-snapshot.tsv`][snapshot], [`ratchet/snapshot.py`][snapshot-py], [`ratchet/synthetic.py`][synthetic], [`ratchet/run.py`][run], [`dbt/`][dbt-dir], [`tests/`][tests].
[^data-results]: CMS. [Performance Year Financial and Quality Results][data-results], 2013-2024. data.cms.gov. Files cited: [PY2020][file-py2020], [PY2021][file-py2021]; [PY2021 data dictionary][dict-results-2021].
[^plan]: Harrold, S. (2026). [`PREREGISTRATION.md`][plan-1.3], version 0.6, the registered plan, at commit `a4064f5` (sha256 `d0e374c8…`; identical to the OSF copy). Sections cited: [1.1][plan-1.1], [1.3][plan-1.3], [3][plan-3], [4.3][plan-4.3], [4.4][plan-4.4], [4.5][plan-4.5], [5.4][plan-5.4], [5.5][plan-5.5], [5.6][plan-5.6], [5.7][plan-5.7], [5.8][plan-5.8], [6][plan-6], [7][plan-7].
[^cms-puf]: CMS. [Non-Identifiable Data Files (public use files)][puf]. cms.gov.
[^simmons2011]: Simmons, J. P., Nelson, L. D. and Simonsohn, U. (2011). False-positive psychology: undisclosed flexibility in data collection and analysis allows presenting anything as significant. *Psychological Science* 22(11), 1359-1366. [doi:10.1177/0956797611417632][simmons2011]
[^nosek2018]: Nosek, B. A., Ebersole, C. R., DeHaven, A. C. and Mellor, D. T. (2018). The preregistration revolution. *Proceedings of the National Academy of Sciences* 115(11), 2600-2606. [doi:10.1073/pnas.1708274114][nosek2018]
[^results]: Harrold, S. (2026). [Results files][results-dir] at commit `3da8cd2`, each recording the commit it ran at: [`validation.json`][res-validation], [`power.json`][res-power], [`confirm.json`][res-confirm], [`robustness.json`][res-robustness], [`did.json`][res-did], [`conventional.json`][res-conventional], [`exploratory.json`][res-exploratory]; with [`REGISTRATION.md`][registration-md] and the notebook source [`report/results_notebook.py`][notebook-src] at commit `eceda2a`, the version exported.
[^cfr-425]: [42 CFR Part 425][cfr-425], Medicare Shared Savings Program. eCFR, as in force on 2022-01-01.
[^cfr-425-600]: 42 CFR 425.600, Selection of risk model. eCFR, as in force on 2022-01-01. Paragraphs cited: [(a)(4)(i)(B)(1)(i)][cfr-600-entry], [(a)(4)(i)(B)(2)][cfr-600-glide], [(a)(4)(i)(B)(2)(iii)][cfr-600-pause-2021], [(a)(4)(i)(B)(2)(iv)][cfr-600-pause-2022]; and, as in force on 2023-01-01, [(a)(4)(i)(B)(2)(vi)][cfr-600-stay-2023].
[^cfr-425-226]: 42 CFR 425.226, Annual participation elections. eCFR, as in force on 2022-01-01. Paragraphs cited: [(a)(2)(i)][cfr-226].
[^cfr-425-200]: 42 CFR 425.200, Participation agreement with CMS. eCFR, as in force on 2022-01-01. Paragraphs cited: [(b)(3)(ii)(B)][cfr-200-ext], [(b)(4)(ii)][cfr-200-b4], [(b)(5)][cfr-200-b5].
[^fr-2020]: CMS (2020). Medicare and Medicaid Programs, Basic Health Program, and Exchanges; Additional Policy and Regulatory Revisions in Response to the COVID-19 Public Health Emergency. Interim final rule. [*Federal Register* 85, 27550][fr-covid], May 8, 2020.
[^douven2015]: Douven, R., McGuire, T. G. and McWilliams, J. M. (2015). Avoiding unintended incentives in ACO payment models. *Health Affairs* 34(1), 143-149. [doi:10.1377/hlthaff.2014.0444][douven2015]
[^rose2016]: Rose, S., Zaslavsky, A. M. and McWilliams, J. M. (2016). Variation in accountable care organization spending and sensitivity to risk adjustment: implications for benchmarking. *Health Affairs* 35(3), 440-448. [doi:10.1377/hlthaff.2015.1026][rose2016]
[^lyu2023]: Lyu, P. F., Chernew, M. E. and McWilliams, J. M. (2023). Benchmarking changes and selective participation in the Medicare Shared Savings Program. *Health Affairs* 42(5), 622-631. [doi:10.1377/hlthaff.2022.01061][lyu2023]
[^chen2025]: Chen, A. J. and McWilliams, J. M. (2025). How benchmark changes affect participation in accountable care organizations: prospects for voluntary payment models. *American Journal of Health Economics* 11(1), 38-62. [doi:10.1086/726748][chen2025]
[^ying2024]: Ying, M., Forman, J. H., Murali, S., Gauntlett, L. E., Krein, S. L., Hollenbeck, B. K. and Hollingsworth, J. M. (2024). Factors affecting Accountable Care Organizations' decisions to remain in or exit the Medicare Shared Savings Program following Pathways to Success. *Health Affairs Scholar* 2(1). [doi:10.1093/haschl/qxad093][ying2024]
[^ying2023]: Ying, M., Hirth, R. A., Yan, P., Shay, A., Murali, S., Ryan, A. M. and Hollingsworth, J. M. (2023). Changes in Shared Savings Program participation after launch of Pathways to Success. *Journal of General Internal Medicine* 38(7), 1780-1782. [doi:10.1007/s11606-022-07947-x][ying2023]
[^moloci2021]: Moloci, N. M., Si, Y., Norton, E. C., Ryan, A. M. and Hollingsworth, J. M. (2021). Predicting losses from Medicare Shared Savings Program departures. *Journal of General Internal Medicine* 36(8), 2490-2491. [doi:10.1007/s11606-020-06424-7][moloci2021]
[^cfr-425-220]: 42 CFR 425.220, Termination of the participation agreement by the ACO. eCFR, as in force on 2022-01-01. Paragraphs cited: [(a)][cfr-220].
[^cfr-425-605]: 42 CFR 425.605, Calculation of shared savings and losses under the BASIC track. eCFR, as in force on 2022-01-01. Paragraphs cited: [(d)(1)][cfr-605-levels].
[^fr-2018]: CMS (2018). Medicare Program; Medicare Shared Savings Program; Accountable Care Organizations—Pathways to Success and Extreme and Uncontrollable Circumstances Policies for Performance Year 2017. Final rule. [*Federal Register* 83, 67816-68082][fr-pathways], December 31, 2018. Cited: [83 FR 67859][fr-pathways-track] (no move from BASIC to ENHANCED within an agreement period).
[^spec-v10]: CMS (2022). [Medicare Shared Savings Program: Shared Savings and Losses and Assignment Methodology Specifications, version 10][spec-v10] (performance years starting January 1, 2022). Section 4.1.2. [Archived copy][spec-v10-archive].
[^data-county]: CMS. [County-level Aggregate Expenditure and Risk Score Data on Assignable Beneficiaries][data-county]. data.cms.gov.
[^data-assigned]: CMS. [Number of Accountable Care Organization Assigned Beneficiaries by County][data-assigned]. data.cms.gov.
[^vanderplas2016]: VanderPlas, J. (2016). Statistics for Hackers. PyCon 2016. [Video][vdp-video], [slides][vdp-slides].
[^rubin1981]: Rubin, D. B. (1981). The Bayesian bootstrap. *Annals of Statistics* 9(1), 130-134. [doi:10.1214/aos/1176345338][rubin1981]
[^phipson2010]: Phipson, B. and Smyth, G. K. (2010). Permutation p-values should never be zero: calculating exact p-values when permutations are randomly drawn. *Statistical Applications in Genetics and Molecular Biology* 9(1), article 39. [doi:10.2202/1544-6115.1585][phipson2010]
[^sw-pymc]: PyMC 6.3.2, with PyTensor 3.3.4 ([pymc.io][pymc]); pinned in `uv.lock`.
[^hoffman2014]: Hoffman, M. D. and Gelman, A. (2014). The No-U-Turn Sampler: adaptively setting path lengths in Hamiltonian Monte Carlo. *Journal of Machine Learning Research* 15, 1593-1623. [jmlr.org][nuts]
[^gelman2008]: Gelman, A. (2008). Scaling regression inputs by dividing by two standard deviations. *Statistics in Medicine* 27(15), 2865-2873. [doi:10.1002/sim.3107][gelman2008]
[^gelman-prior2008]: Gelman, A., Jakulin, A., Pittau, M. G. and Su, Y.-S. (2008). A weakly informative default prior distribution for logistic and other regression models. *Annals of Applied Statistics* 2(4), 1360-1383. [doi:10.1214/08-AOAS191][gelman-prior2008]
[^firth1993]: Firth, D. (1993). Bias reduction of maximum likelihood estimates. *Biometrika* 80(1), 27-38. [doi:10.1093/biomet/80.1.27][firth1993]
[^sw-firthmodels]: firthmodels 0.8.2, Firth-penalized models in Python ([source][firthmodels]); pinned in `uv.lock`.
[^vehtari2021]: Vehtari, A., Gelman, A., Simpson, D., Carpenter, B. and Bürkner, P.-C. (2021). Rank-normalization, folding, and localization: an improved R-hat for assessing convergence of MCMC. *Bayesian Analysis* 16(2), 667-718. [doi:10.1214/20-BA1221][vehtari2021]
[^callaway2021]: Callaway, B. and Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics* 225(2), 200-230. [doi:10.1016/j.jeconom.2020.12.001][callaway2021]
[^roth2022]: Roth, J. (2022). Pretest with caution: event-study estimates after testing for parallel trends. *American Economic Review: Insights* 4(3), 305-322. [doi:10.1257/aeri.20210236][roth2022]
[^lakens2017]: Lakens, D. (2017). Equivalence tests: a practical primer for t tests, correlations, and meta-analyses. *Social Psychological and Personality Science* 8(4), 355-362. [doi:10.1177/1948550617697177][lakens2017]
[^rambachan2023]: Rambachan, A. and Roth, J. (2023). A more credible approach to parallel trends. *Review of Economic Studies* 90(5), 2555-2591. [doi:10.1093/restud/rdad018][rambachan2023]
[^rosenbaum1983]: Rosenbaum, P. R. and Rubin, D. B. (1983). The central role of the propensity score in observational studies for causal effects. *Biometrika* 70(1), 41-55. [doi:10.1093/biomet/70.1.41][rosenbaum1983]
[^welch1947]: Welch, B. L. (1947). The generalization of "Student's" problem when several different population variances are involved. *Biometrika* 34(1-2), 28-35. [doi:10.1093/biomet/34.1-2.28][welch1947]
[^mackinnon1985]: MacKinnon, J. G. and White, H. (1985). Some heteroskedasticity-consistent covariance matrix estimators with improved finite sample properties. *Journal of Econometrics* 29(3), 305-325. [doi:10.1016/0304-4076(85)90158-7][mackinnon1985]
[^sw-statsmodels]: statsmodels 0.15.0 ([statsmodels.org][statsmodels]; [`Logit`][statsmodels-logit]); pinned in `uv.lock`.
[^sw-dbt]: dbt-core 1.12.6 with dbt-duckdb 1.11.0 ([getdbt.com][dbt]; [data tests][dbt-tests]); pinned in `uv.lock`.
[^sw-duckdb]: DuckDB 2.0.0 ([duckdb.org][duckdb]); pinned in `uv.lock`.
[^sw-uv]: uv, the Python package and project manager ([docs][uv]; [lockfile][uv-lock]).
[^sw-numpy]: NumPy 2.5.4: [`SeedSequence`][numpy-seed] and [parallel random number generation][numpy-parallel]; pinned in `uv.lock`.
[^sw-arviz]: ArviZ 1.3.0: [R-hat][arviz-rhat] and [effective sample size][arviz-ess]; pinned in `uv.lock`.
[^gelman-carlin2014]: Gelman, A. and Carlin, J. (2014). Beyond power calculations: assessing Type S (sign) and Type M (magnitude) errors. *Perspectives on Psychological Science* 9(6), 641-651. [doi:10.1177/1745691614551642][gelman-carlin2014]
[^sw-marimo]: marimo 0.25.2, reactive Python notebooks ([marimo.io][marimo]); run outside the lockfile, pinned on the command line (see [Reproduce](#reproduce)).
[^census]: U.S. Census Bureau. [Census Regions and Divisions of the United States][census] (map).
[^suppression]: CMS (2020). [CMS Cell Suppression Policy][suppression-archive]: cells with values of 1 to 10 are not reported. Archived copy; the [HHS Guidance Portal page][suppression] refuses some visitors.
[^cfr-2024]: 42 CFR 425.652, Establishing, adjusting, and updating the benchmark for agreement periods beginning on January 1, 2024, and in subsequent years; 425.656, Calculating the regional adjustment to the historical benchmark; and 425.658, Calculating the prior savings adjustment to the historical benchmark. eCFR, as in force on 2024-01-01. Paragraphs cited: [425.652][cfr24-652], [425.652(a)(8)][cfr24-652-a8], [425.652(b)][cfr24-652-b], [425.656(c)(4)][cfr24-656], [425.658(c)(1)][cfr24-658].
