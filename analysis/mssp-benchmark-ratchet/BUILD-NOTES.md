# Build notes: how this study was built (for the #73 blog post)

A running log of the process, kept for the write-up: what was tried, what was dropped and why, which checks caught
which problems, and how the plan was registered. `DESIGN-NOTES.md` holds the technical detail of the design decisions;
this file is the story. Commit hashes refer to branch `src_feature_mssp_prereg`. Newest entries at the bottom.

## Ground rules (2026-10-22)

- Pre-register before looking at outcomes. Only CMS enrollment files, data dictionaries and regulation text
  (42 CFR 425, via the eCFR API) were used for design. Outcome files (performance-year results, county spending,
  county assignment) were downloaded once to record sha256 hashes (`data-snapshot.tsv`) and left unopened.
- The registration needs an independent timestamp (OSF Registries), because git commit dates can be set by hand.
- The author reviews every rule before registering; the registration is permanent and public.

## Three questions dropped at the design stage (2026-10-22)

1. **Downside risk (the BASIC glide path).** Idea: the glide path forces ACOs into two-sided risk on a schedule, a
   natural experiment. The regulation text (425.600(a)(4)(i)(B)) showed the glide path is a default with opt-outs,
   and enrollment data showed only 10-28% take-up. Dropped (7c82955-1d7fa32).
2. **Benchmark ratchet (spending in benchmark years).** Idea: ACOs spend less once their years start counting toward
   the next benchmark. Enrollment data showed benchmark-year status is collinear with agreement tenure, so the effect
   is not identifiable. Dropped, kept as a descriptive table (3d011d6-e02ac9a).
3. A correction along the way: an unverified inference that "all 139 stay-outs were early renewers" was wrong; agreement
   extensions explained most of them, and only 29 ACOs renewed early into 2022 (e6fb9c3).

## The question that survived: why did 29 ACOs renew early? (2026-10-22)

- v0.2 tested one thing: did early renewers have lower savings? (e0ac5a9)
- The author asked whether the scope was too narrow to explain anything ("are we purposefully limiting the scope...").
  v0.3 became an explanatory plan with two opposing motives: the reset motive (a new benchmark would be higher) and
  the sharing-rate motive (renewal is the only way into the ENHANCED track's 75% sharing) (d3113b5).
- Review caught that the savings rate cannot separate the motives, and that the planned "regional component" contains
  the own-spending term with a negative sign (regional = w x pull - w x own). The primary test became **regional pull**,
  which has no own-spending term (83ff0c2, 2aa2be5).

## Methods chosen by the author (2026-10-22)

- Bayesian estimation throughout, significance by resampling, following VanderPlas, "Statistics for Hackers"
  (PyCon 2016) and the author's 2015 work (`ARCHIVED_2015_Harrold_SDSSJ1600`: shuffled time series for significance,
  emcee MCMC for parameters) (357db23-d354451).
- A side agent pointed out 29 early renewers support only ~3 predictors at 10 events per predictor; the decision model
  was kept small with priors doing the stabilizing.
- Review caught that shuffling labels in a multi-predictor model tests "nothing matters", not "this factor matters
  given the others"; per-factor significance became direct simulation under the reduced model (a parametric
  bootstrap), with the label shuffle kept as an overall test (120053a).

## Writing the code before registering (2026-10-25)

Writing the pipeline before registration exposed gaps in the plan while it could still change.

- **Stack:** DuckDB SQL for the constructed variables (one file per step of section 4.3), PyMC for models, numpy for
  resampling. The author asked whether DuckDB could pre-compute the MCMC runs; it cannot (NUTS is iterative), but it
  made the construction readable and testable.
- **Outcome lock:** every file is hashed before reading; a real outcome file cannot be read until `REGISTRATION.md`
  exists. Synthetic data directories carry a marker. There is no bypass flag.
- **Two implementations:** the synthetic-data generator computes section 4.3 independently in numpy; tests require the
  SQL to match it.
- **Header-only reads** (column names, no values) of outcome files, disclosed in plan section 2.2, found naming drift:
  `ACO_Num` in PY2016-2017, `Sav_Rate` in PY2021, `AGED_Dual` vs `AGDU`.
- Gaps found and pinned by coding: how calibration splits between components, how "below its region" is compared,
  power-simulation sizes, per-refit seeds, the census-region rule, date formats in unseen files.
- **Measured cost:** ~40,000 MCMC refits for the confirmatory stage, ~1.7 s each with 5 workers on synthetic data,
  about 19 hours. (An early estimate of 6 hours missed the overall test.)

## What reviewers and side agents caught (2026-10-25)

- **Suppressed values.** The results files are CMS's suppressed versions; the draft rule dropped any ACO with one
  hidden value, which could cost early renewers. Added a fallback chain (exact recovery of person-years from totals,
  shown years, region x own-to-region ratio) with a complete-case robustness check (b6a190b).
- **Risk adjustment.** The main test compared raw regional spending with each ACO's benchmark. 42 CFR 425.601(c)(4),
  (a)(8)(i)(C) and (a)(3) show CMS risk-adjusts regional spending to the ACO's case mix and restates benchmark years
  to BY3 risk. Implemented, with unadjusted pull kept as a robustness item (3391940).
- **A second validation.** CMS's own benchmark-year spending (PY2022 file, regular renewers only) validates the
  own-spending part separately and sets the measurement-error SD (f062e01).
- **Leak guard.** The PY2022 file would reveal early renewers' actual reset; it is filtered at load to the validation
  sample, and the descriptive stage that needs it runs only after the confirmatory results exist.
- **Fork deadlock risk.** Parallel chains forked a multi-threaded process; switched to `forkserver` (a6a92f1).

## Registration (2026-10-25, in progress)

- All analyses in sections 4-6 coded and tested (72 tests, synthetic data only). Plan v0.5, commit a6a92f1.
- Code zip made with `git archive` at a6a92f1, including `pyproject.toml` and `uv.lock` so package versions are
  frozen; sha256 checked before upload.
- OSF account created via ORCID; email confirmed; draft created (Open-Ended Registration). Title and description
  entered; license CC-By 4.0 (matching the blog); subjects Health Services Research, Health Economics, Health Policy.
- The author asked why register at all; answer recorded: proof the plan predates the results, a credible
  confirmatory/exploratory line, and it unlocks the pipeline. Alternatives considered: AsPredicted, OpenTimestamps.
- Before submitting, the author asked whether conventional methods should be reported side by side for credibility.

## Before registering: conventional methods and an effect question (2026-10-25)

- The author asked whether conventional methods should sit beside the Bayesian and resampling results for
  credibility. Decision: a reported-only comparison section (Welch t, OLS with HC2 errors, maximum-likelihood
  logistic regression) and a table of where the two approaches agree. Adds `statsmodels`.
- The author then asked whether the study should also use difference-in-differences. The plan so far asked only who
  chose to reset and why, not what renewing did. Decision: add H4, the effect of early renewal on per-capita spending
  (PY2022-2024 vs PY2019-2021, early renewers vs stayers from the same cohorts), pre-registered in the same plan before
  any post-period spending is seen. Threats stated up front: selection on recent spending (mean reversion), few
  COVID-era pre-periods, and a bundled treatment (reset + ENHANCED + a change in which years count as benchmark years).
- Registration paused with a private OSF draft until H4 is specified, coded and tested.
- Scope review against what the post should demonstrate: methods and tools are added only where they are the right
  tool for the question. For #73: difference-in-differences with propensity weighting (H4), dbt for the SQL pipeline
  (before registering, since the code is registered), and an interactive dashboard in the write-up (after results).
  Fine-tuning and A/B testing of configurations went to #74 instead, where they fit; synthetic DiD was left out
  (no maintained Python implementation, only two pre-periods).
- Enrollment check for the DiD control group (enrollment data only): of 277 stayers, 42 renewed into 2023 or 2024
  agreements and 72 left by 2024; of 29 early renewers, 3 renewed again in 2024 and 1 left. Design choice:
  "not-yet-renewed" comparison ACOs, censored at any later renewal (Callaway and Sant'Anna's not-yet-treated idea).
- H4 implemented: SQL builds a PY2020-PY2024 panel with each ACO-year's status (included, later renewal, absent);
  the confirmatory estimate collapses it to one change per ACO and reuses the 5.1 estimator, so the DiD test is the
  same stratified permutation as the other group comparisons. Conventional two-way fixed effects and an event study
  sit beside it. On synthetic data with a planted -4% effect the estimate was -3.1% (95% interval -3.9 to -2.3) and
  the TWFE estimate -3.7%. A first TWFE version was rank-deficient (cohort-by-year dummies collinear with ACO
  effects); fixed by dropping PY2020 within each cohort.
- Pre-trend rule changed before registration after a side agent cited Roth (2022), "Pretest with Caution": with one
  COVID-era pre-period change and ~29 treated ACOs, "pre-trend not significant" proves little. H4 is now called an
  effect only if the pre-trend interval, scaled to the gap between period midpoints, rules out a trend difference big
  enough to produce the estimate (an equivalence condition), and a trend-adjusted estimate (pre-period slope carried
  forward, in the spirit of Rambachan and Roth 2023) is reported beside it.
- dbt: the SQL pipeline became a dbt-duckdb project, one model per derived table (28 models in three tagged stages),
  Jinja macros for parsing, a `by_first` variable for the BY2-BY3 variant, and schema plus singular data tests (unique
  keys, accepted values, components adding to the gain, shares summing to one, no early renewer in the PY2022 load).
  Python still loads every raw table after its hash check and lock, so dbt never reads a file. dbt runs twice per
  build so the PY2022 file is filtered by the dbt-built validation sample. Before deleting the old SQL, every one of
  the 28 tables was compared between the old and new pipelines on the same synthetic data, for both variants:
  identical. Two dbt gotchas: `log-path` in dbt_project.yml is not templated (it created a directory literally named
  with the Jinja expression), and dbt sends anonymous usage events by default (disabled in the project).

## Registration draft completed (2026-10-26)

- Code zip remade at the final pre-registration commit 4358df5 with `git archive` (83 files; `pyproject.toml` and
  `uv.lock` included, no data files). Because `git archive` stamps files with the commit time, the zip is
  reproducible from the commit: sha256 f4ef63bf...4727. Plan v0.6 sha256 675de568...ecf7.
- OSF draft updated: description rewritten to cover H4 and the conventional comparison and to cite the new zip, hash
  and commit; three subjects; seven tags. Summary step: a two-sentence lead-in with both hashes, then the full plan
  text, with the plan file and the zip attached as supplemental files. OSF's stored sha256 for both attachments was
  checked against the local files through the OSF API: both match.
- Two form gotchas: a password manager's inline menu attached to the page and the draft's title and description were
  found blank on the server after a reload (tags, subjects and license were intact); and the metadata page saves
  title and description only when Next is clicked, not on blur. Checking the saved draft through the API, not the
  page, caught both.
- The Summary box does not render Markdown, so the pasted plan showed raw `**` and `#`. It was replaced with a
  plain-text copy made by a short script: headings kept, inline marks stripped, line wraps joined, the one table
  turned into list items (a proportional font breaks aligned columns), and a word-for-word check against the
  Markdown (6,636 words outside the table, identical). The attached `.md` stays the authoritative version.
- A second OSF gotcha: the form deletes anything that looks like an HTML tag, so column-name placeholders such as
  `CMS_HCC_RiskScore_<e>_PY` were saved as `CMS_HCC_RiskScore__PY` (16 placeholders), while `p < 0.05` is stored
  escaped and displays correctly. Placeholders are written `{e}` and `{year}` in the summary, said in its lead-in.
  Found by hashing the saved text in 2,000-character chunks against the local file; after the fix the saved text,
  unescaped, matches the local copy byte for byte.
- Two side-agent catches before Register: the plan's status line still said "DRAFT ... Not yet registered", which
  would have been frozen into the public record; the first fix dated it ("submitted ... on 2026-10-26"), which would
  be wrong if Register were clicked another day. Final wording names no date and points to the OSF timestamp in
  `REGISTRATION.md`. Code unchanged; final commit a4064f5, plan sha256 d0e374c8...e8f2, zip sha256 4c98d76a...9cd4.
- OSF gotchas in the swap: an upload whose name matches a file already in the draft's storage is silently dropped,
  so the old `PREREGISTRATION.md` had to be deleted first (the author deleted the stale files; detaching a file
  from the question leaves it in storage, which becomes part of the registration's project); uploading a file
  resets an unsaved Summary box to its last autosave; and after a reload the Metadata step showed a "!" (invalid)
  although the server copy was complete, cleared by saving the step with Next.
- Stopped at Review; the author clicks Register (public, permanent).
- Registered 2026-10-26 13:22:16 UTC: https://osf.io/c53w9/ (DOI 10.17605/OSF.IO/C53W9). OSF holds a new
  registration as "pending approval" (not public) until every admin approves by email, or for 48 hours; the author
  approved it, and it was confirmed visible to a signed-out request before `REGISTRATION.md` was written, since
  that file unlocks the outcome data. The archived copies' sha256 match the plan and the zip. The page the author
  landed on, osf.io/z4an5, is the editable project OSF creates for the draft's files, not the registration.

## Running the registered pipeline (2026-10-26)

- `DEVIATIONS.md` started before the first real-data stage, on a side agent's reminder: after registration even a
  crash fix to the code is a deviation, logged before its results are used. Each results file records its commit;
  the registered code trees (git tree hashes of `ratchet/`, `dbt/`, `tests/`, the manifest, the plan) were checked
  identical to a4064f5.
- validate (11 s): the reconstruction of 2022 benchmarks passed (Spearman 0.94, median absolute percentage error
  1.6%, 101 ACOs), so the own-spending term enters H3 with measurement error sigma_v = 4.38 (4.375).
- power (about 40 min), committed before any confirmatory estimate as the plan requires: MDE for H1 2.7 percentage
  points of savings rate (simulated power 80.4%), H2b 2.5 and H2a 1.8 points (0.55 SD), H4 3.8% (log 0.038). H3
  is underpowered at a log-odds of 0.5 per 2 SD: the 95% interval excludes zero in 17% (pull), 0% (own) and 14%
  (BASIC level) of 500 simulated datasets, so an "undetermined" H3 verdict is the expected outcome, and the
  write-up says so.
- confirm started 2026-10-26 10:08 EDT under `caffeinate -i` (about 19 hours expected). robustness ran alongside it
  once confirm had finished its dbt build (the two share the dbt target directory), in 8 minutes; 4 of about 30,000
  Firth refits in its simulated null distributions stopped at the iteration limit (kept as fitted, as the registered
  code does). Robustness results are read only together with the confirmatory ones, primary first.
- confirm finished 2026-10-27 03:11 EDT (exit 0) after 17 h 3 min, at commit 3e5cb9b (registered code unchanged). The
  H3 model and its t-prior fit both converged, so the direct simulation tests ran and the Firth fallback did not.
  `results/confirm.json` was committed before anything in it was read beyond these checks.
- did (27 s, commit 992d13f): numpy warned "Mean of empty slice" for ACOs with no post-period year; those rows
  get a missing midpoint distance and are then dropped by the `n_post > 0` filter, so no estimate uses them (`did.json`
  has no NaN). `np.errstate` does not silence this warning because numpy raises it through `warnings`, not as a
  floating-point error.
- conventional (8 s, commit acc8b0e): no warnings.
- exploratory (83 s, commit ff6e64b): no warnings. All seven stages have now run with the registered code and no
  deviations; every results file was committed before its estimates were read.
- H1 units, checked as the draft's checklist asks: the PY2020 file stores savings rates as fractions (`0.0382`, SD
  0.046, like the PY2016-PY2018 files behind the power analysis), the PY2021 file as percents with a sign (`3.14%`, all
  475 rows). So H1 PY2020 is 0.0188 = 1.9 percentage points and H1 PY2021 is 1.57 points, both against an MDE of
  0.0265 = 2.7 points. Nothing in the registered analysis mixes the two years (H1 is descriptive and its sign and
  p-value do not depend on the unit), so this is a reporting matter, not a deviation. The dashboard had scaled every H1
  value by 100; `report/dashboard_data.py` now leaves the PY2021 comparison as it is.
- Dashboard data rebuilt from the real results; checked at desktop and phone width (no overflow, no synthetic banner).
- Exclusions: the expected-gain variables are missing for 3 of 29 early renewers (10.3%) and 36 of 277 stayers
  (13.0%), over the plan's 10% reporting line (section 3), so the post lists it as a limitation. A diagnostic run
  (outside the repository, reading the same dbt tables) traced every one to the 2021 county assignment file: each of
  the 39 has its assigned ESRD person-years hidden in every county, so `region_std` has no county weights for ESRD
  (15 also lack aged/dual weights). The registered fill rules cover hidden results-file cells, not county weights, so
  the registered rule (exclude and count) applied. Excluded ACOs are smaller (median 6,702 and 8,578 assigned
  beneficiaries vs 10,757 and 15,649 included). The draft had said 27 events in H3; the fitted model has 24.
- Results written into the post 2026-10-27 in the plan's order, with each verdict in the section 7 wording. Two points
  the numbers forced into the text: the total expected gain does not differ (its two parts offset), and H3's
  supported coefficients come from a test with 14-17% power, so their size is probably exaggerated (type M error).
  The H3 own-spending coefficient's interval equals the prior's because sigma_v (4.38) exceeds the variable's SD.
- Five-column result tables overflowed phones by 97 px; the theme now scrolls post tables inside their box below
  576 px (CSS only, so the frozen posts' Markdown is untouched; their pages were checked too).

## Write-up started while confirm runs (2026-10-26)

- Post drafted as `content/20261026-preregistered-mssp-early-renewal.md` (`Status: draft`): question, why
  pre-register, how the question was chosen, design, methods, pipeline, what review caught, registration and power,
  with the results, robustness, exploratory and deviations sections marked pending. Deviations get their own section,
  as the plan (section 8) and issue #73 require.
- Dashboard frame: `content/static/<slug>/dashboard.js` and `.css`, plain JavaScript and inline SVG (no library,
  font or third-party request, so the privacy page needs no change). It reads `data.json`, which
  `report/dashboard_data.py` (standard library only, outside the registered paths) builds from `results/`. Stages not
  yet run show as pending, and the synthetic-data banner comes from the results files' own `synthetic` field. Built
  and checked on a full quick-mode synthetic run at the registered code.
- Gotcha: Pelican copies any file a post links with `{static}` into the output even when `STATIC_EXCLUDES` lists its
  folder, so a draft's `{static}` links leak its files into the published site. `test_drafts_are_not_published`
  caught it; the draft links the dashboard root-relative until it is published.
- Units: the CMS files store savings rates as fractions (the power analysis's PY2016-PY2018 SD is 0.049), while the
  synthetic generator writes percents. The decision rules do not depend on the unit; the dashboard shows H1 in
  percentage points, and the H1 write-up checks the confirm output's scale against the power file's before comparing
  the estimate with the MDE.
- Robustness and exploratory views added to the dashboard (2026-10-26). Robustness repeats each confirmatory
  estimate with the section 5.5 items that rerun it, on one axis per estimate, with no verdicts (5.5: they do not
  change the decisions). The Firth fit shares the Bayesian H3 axis because both use `make_design`'s scaling
  (continuous predictors per 2 SD, binary centered). Robustness item 4 is the same estimate as the confirm stage's
  PY2021 savings-rate row, so it is not repeated. Exploratory shows the other pull measures, census region, leavers,
  the ENHANCED early renewers, who renewed, balance, and per-capita spending by agreement year (one panel per start
  year, scheduled benchmark years shaded, with the plan's caveat that benchmark-year status and tenure cannot be
  separated).
- Phone-width check found the page scrolling sideways by 282px, from the 64-character hashes in the post's
  registration table, not the dashboard. Fixed in the theme (`overflow-wrap: anywhere` for code in table cells; no
  other post has code in a table). Charts are now sized to the card's content width, which also fixed a clipped
  third panel.
- A marimo static HTML export is a 33 KB page that loads marimo's front end from `cdn.jsdelivr.net` (checked with
  marimo 0.25.2), so hosting one on the site would add a third-party request.
- Results notebook hosting, decided 2026-10-26: a marimo notebook that only reads `results/*.json`, exported as static
  HTML for the site (readers) and uploaded to OSF with a PDF export and an `.ipynb` with outputs. The PDF and `.ipynb`
  are the copies that survive if jsDelivr stops serving marimo's front end; the site and OSF HTML both depend on it.
  Built after the real results, run with `uv run --with marimo==0.25.2 --with nbformat` so `uv.lock` does not change.
- Results write-up approved by the author 2026-10-27, with the site-wide phone-table CSS change reviewed in a local
  preview.
- Results notebook (2026-10-27): `report/results_notebook.py`, a marimo notebook that imports `dashboard_data.build()`
  so the notebook, the dashboard and the post share one set of unit conversions, and checks that the committed
  `data.json` matches. Tables are Markdown and figures matplotlib PNGs, so the `.ipynb` (outputs are only
  `text/markdown` and `image/png`) and the PDF need no JavaScript or CDN. Exported once, after the last edit, with
  `uv run --no-sync --with marimo==0.25.2 --with matplotlib==3.11.2 --with nbformat==5.11.1 --with
  'nbconvert[webpdf]==7.17.2' --with playwright==1.61.0 marimo export {html | ipynb --include-outputs | pdf}`; none
  of these are in `uv.lock`. Playwright is pinned to 1.61.0 because its Chromium revision (1228) was already cached;
  the newest Playwright wanted a browser download. HTML in `content/static/<slug>/`, `.ipynb` and PDF in
  `report/exports/` (about 850 KB, committed so the hashes in the post can be checked against the repository).
  Re-exporting changes every hash (the PDF embeds a creation date), so the files on OSF must be these committed ones.
- Gotchas: in `mo.md(f"""...""")`, an interpolated multi-line table is not indented like the rest of the string, so
  marimo's dedent fails and the cell renders as raw text; build such cells from unindented parts. Every run writes a
  session cache to `report/__marimo__/` (now in `.gitignore`). Ruff formats `.ipynb` files, so
  `report/exports/ruff.toml` excludes them (a nested config, because `pyproject.toml` is a registered file) and
  `.pre-commit-config.yaml` excludes the folder; `ruff format --check .` and `--force-exclude` both skip it.
- The HTML export's only third-party host is cdn.jsdelivr.net (about 300 requests for marimo's scripts, styles and
  fonts; checked with Playwright). Its web-vitals module only logs to the console; no analytics. The embedded mount
  config records the file name without a path and the editor's default settings. The privacy page's notebook bullet
  now covers marimo exports. Where the page's "Run or Edit" button leads was not checked; it acts only when a reader
  clicks it, so it is not a request the page makes on load.
- Notebook exports uploaded by the author to OSF z4an5, folder `results-notebook`, 2026-10-27: results.html
  (osf.io/m5qkx), results.ipynb (osf.io/aczts), results.pdf (osf.io/247qu). OSF's sha256 for each, checked by the
  author in the OSF interface and again through the public API, matches the post and the committed files.
- Sources linked in the post (2026-10-27, at the author's request: every claim about methods, data sources and
  definitions links to a source). About 150 distinct links, written as Markdown reference links defined at the end of
  the post. Regulation links are eCFR point-in-time (2022-01-01) with paragraph anchors, percent-encoded
  (`#p-425.601%28a%29%288%29`); eCFR resolves the encoded anchor. Federal Register links use `/citation/83-FR-NNNNN`
  or `#page-N`. Repository links are pinned: plan, code and data snapshot to `a4064f5`, results, registration record
  and notebook to `3da8cd2`; only `DEVIATIONS.md` links the main branch, as a running log. Papers by DOI (checked
  against Crossref), general concepts by Wikipedia (section anchors checked with the MediaWiki API), software by its
  docs. Every URL was requested: publishers and hhs.gov answer scripts with 403 (the weekly link check accepts 403),
  and GitHub's 429s were rechecked through the API.
- Checking the sources corrected four statements in the post (the registered plan is unchanged): the glide path is
  not something ACOs simply opt out of (they choose the starting level, may advance faster, and could pause for 2021
  and 2022; 425.600(a)(4)(i)(B)); ENHANCED shares 75% of savings but up to 75% of losses (425.610(f)(2));
  "renewing is the only way into ENHANCED" rests on the 2018 rule's preamble (83 FR 67859: no move from BASIC to
  ENHANCED within an agreement period), not the CFR text; and restating benchmark years to BY3 risk is in CMS's
  methodology specifications (version 10, section 4.1.2, step 3), while 425.601(a)(3) only says HCC risk scores
  adjust for changes in case mix.
- References as footnotes (2026-10-27), the site's convention from the 2015-2016 posts: Python-Markdown footnotes
  (`[^id]`) placed by `///Footnotes Go Here///` under References, numbered by first citation, with one back-link per
  citation (repeated references to one footnote work: 113 citations of 52 sources). Each paragraph, list item or
  table row cites a source once, after its first link to it; inline links still go straight to the paragraph or
  page. Footnoted: regulation sections, Federal Register rules, the CMS specification and cell-suppression policy,
  CMS program pages and datasets, the registration, plan, code and results, papers, and the pinned software. General
  terms keep their Wikipedia links inline only. The post also notes that the registered plan's section 1.1
  overstates the rule ("75% of savings and losses"; the only way into ENHANCED), with what the rule says.
- Glide path, rechecked against later versions (2026-10-27). The design-stage note on #73 cited 425.600
  (a)(4)(i)(B)(2)(iii)-(vii), from the current eCFR; as in force on 2022-01-01 only (iii) and (iv) exist (pauses for
  2021 and 2022). (vi), in force from 2023-01-01, let an ACO in Level A or B stay there for the rest of its agreement
  ((vii) does the same for 2024 for agreements starting in 2023). The post now cites both dates, so the correction
  no longer understates the options. Lesson: when citing a regulation for a period, read it as in force in that
  period (`/on/<date>/` URLs, or the versioner API with `--compressed`).
- Documentation updated: the study README lists `results/`, the notebook and its exports, and the status;
  `CLAUDE.md` gained the footnote convention, stable-link rules, marimo and Playwright gotchas, the eCFR API command,
  and the zsh `path` gotcha.
- Analytics before publishing (2026-10-27). Checked: the GA4 tag G-K4PX9089RZ is on every published page (only in
  `publishconf.py`); stream 5708903862 receives traffic; the BigQuery daily export to
  `stharrold-github-io.analytics_393124094` runs. Changed, at the author's request: enhanced measurement now sends
  scrolls (90%) and outbound clicks (it had page views only); event data retention 2 to 14 months; a custom
  dimension `percent_scrolled` (event scope). The theme's GA include (`includes/ga.html`, publish builds only) now
  sends `scroll` at 25, 50 and 75% and a `notebook_open` event for clicks on `/static/*.html` exports, which are
  standalone pages without the tag (adding it would change the OSF-hashed notebook). Tested on a local publish build
  with GA requests blocked, by reading `dataLayer`; the privacy page lists what is measured.
- Independent critical assessment before publishing (2026-10-27), by a fresh agent given only the files:
  `ARCHIVED/20261027T145203Z_critical-assessment_20261026-preregistered-mssp-early-renewal.md`. Verdict: publishable
  after minor fixes; every reported number matched the results files. All findings were applied to the post:
  the summary no longer uses effect language for H4 and uses rule 1's wording; it states that by the approximation a
  reset would on average have lowered both groups' benchmarks (unweighted -1.6 and -1.0 points); the registered H4
  attrition table (plan 4.5) and a limitation on uneven attrition; the agreement table shows the registered OLS-HC2
  counterpart for H2a and H2b (Welch in a note); the own-spending component's low reliability; what the regional
  pull still contains (the ACO's benchmark and risk scores); that the equivalence condition could not hold near zero;
  the remaining registered outputs (validation slope and intercept, by phase-in step, the step-1 check, the 10
  excluded, refit convergence failures, the prior predictive share); MDE in log points; the H3 power caveat; the
  BASIC-level interpretation; the concurrent robustness run and the 17-hour runtime; the exclusion diagnostics'
  source; the overview counts; a short glossary; further design threats; and two citation fixes (425.601(a)(2) for
  the enrollment types, (d)(3) for their shares). "What review caught before registration" moved after Reproduce,
  and the OSF summary-field and Playwright details were trimmed (both remain in these notes).
- Notebook re-exported (2026-10-27) so the archived copies follow the review's wording: H4 heading "spending after
  renewal" and the H4 chart axis "Early renewers minus comparison: change in per-capita spending growth (%)" (it
  said "Effect of renewing early"). The dashboard's H4 title changed the same way. New sha256 values are in the
  post; the three files go to OSF z4an5/results-notebook as new versions of the earlier uploads, which stay in each
  file's OSF history.
- Re-exported notebook uploaded to OSF 2026-10-27 15:12 UTC as new versions (same GUIDs m5qkx, aczts, 247qu); OSF's sha256 for all three matches the post and the committed files (public API).
- Reproducibility (2026-10-27): `fetch_snapshot.py` (download and sha256-check the snapshot, falling back to the OSF
  archive osf.io/53aqd, sha256 16f54615...), `compare_results.py` (rerun vs committed results), `CITATION.cff`, and a
  "Reproduce and adapt" README section. Fresh-clone test with an empty home directory (uv cache reused): sparse
  clone, fetch (40/40 from data.cms.gov in 9 s), tests (81 passed, 8 min), validate (8 s, identical to the
  committed file), power (40 min). Power reproduced every deterministic value but not the simulated ones (H1
  simulated power 0.776 vs 0.804; H3 detection shares 0.148/0.150 vs 0.168/0.138). Cause, confirmed by building the
  database three times: `select * from analysis` in `ratchet/run.py` has no ORDER BY, and DuckDB returns the 334
  rows in a different order each build, so the seeded draws fall on different ACOs. Every resampling and simulation
  result therefore varies within simulation error between runs; no verdict is near a threshold. Not a deviation (no
  code changed); disclosed in the post's Reproduce and Pipeline sections and the README, which suggests
  `order by aco_id` for bit-for-bit reruns of a variant.
- Post additions after the review (2026-10-27): "What was simulated, and when"; "In plain English" (with the median
  PY2021 benchmark of $11,312 across the 334 ACOs, so 1 point of benchmark is about $113 per patient per year);
  "Background for newcomers" (four collapsible primers: MSSP worked example, association and causation, Bayesian
  and frequentist, pre-registering a study); an "At a glance" table; "Do these results apply today?" (42 CFR
  425.652, 425.656 and 425.658 as in force on 2024-01-01: prior savings adjustment, offset to negative regional
  adjustments, ACPT); "Implications and open questions"; a numbered Reproduce section; the dashboard's stage list
  shown only while a stage is pending, and its footer pointing to the pinned results instead of a build time; and a
  README recipe for one ACO's reset components. In the worked example, two dollar amounts in one paragraph were
  rendered as inline math by arithmatex; dollar signs there are written `&#36;`.
- Visual abstract (2026-10-27): `report/visual_abstract.py` draws a 1200 x 630 PNG and an SVG from the dashboard's
  `data.json` with matplotlib (pinned on the command line, like the notebook), in the reference palette's blue
  with one series per panel. First draft had labels colliding with values; values now sit in their own column on
  the interval's line, and labels carry a surface-colored background over the grid. Shown below "At a glance" with
  full alt text, linked to the full-size PNG for phones. The theme gained optional per-post preview images
  (`Image:` and `Image_alt:` metadata become og:image, og:image:alt and a large Twitter card); posts without them
  are unchanged, and a test checks that a published post's image exists and is the og:image.
- Visual abstract uploaded to OSF z4an5/results-notebook (2026-10-27): visual-abstract.png (sha256 82beb2d7...) and visual-abstract.svg (sha256 1a4c54e0...), matching the committed files. If the image is redrawn, replace both on OSF.
- medRxiv preprint (2026-10-27): drafted in a separate public repository,
  [stharrold/mssp-paper-2026](https://github.com/stharrold/mssp-paper-2026) (created as mssp-preprint-2026 and renamed the same day), with the yuimedi-paper build
  (pandoc, Eisvogel 3.3.0, tectonic). Tables and figures are generated from copies of `results/*.json` (hashes
  recorded), and `scripts/check_numbers.py` checks the prose: single numbers match some results value by chance about
  90% of the time at 1 decimal, so the real check is that each interval's bounds (and its estimate, where adjacent)
  come from one results record. A PubMed pass added the core MSSP savings and selection papers (McWilliams 2016,
  2018 and 2020; Markovitz 2019; Bond 2025; Srivastava 2026). A fresh-agent review traced about 250 numbers and found
  no wrong value, but found "log points" used on two scales, Crossref subtitles that were Health Affairs teasers, a
  PDF text layer with every hyphen as U+2011 (Source Sans Pro; fixed with Latin Modern by file name), plan-required
  reporting left out (Pr(>0), P/CrI disagreements, two exploratory tables) and caveats lost in condensing the post.
  All applied except the title (kept as registered) and the affiliation's location (the author's call); see the
  repository's `reviews/`.
- Second assessment and post hoc checks (2026-10-27): a second review (supplied by the author) found the study
  sound but the H2b reading too strong. Its sources check out: Milliman's April 2024 report already tabulates the
  29 ACOs that rebased early in 2022 (higher prior gross savings; the 11 earlier incumbents moved to ENHANCED), and
  42 CFR 425.600(d) limits ACOs experienced with risk to Level E or ENHANCED. The preprint now cites both, reads the
  pull as relative efficiency, and says the BASIC-level prediction was not blind to the enrollment data. At the
  author's choice, `posthoc/validation_change.py` (not registered, bf91e5c) checks the gain on the change scale
  (Spearman 0.61, median error 1.7 points, regular renewers) and against early renewers' published 2022 benchmarks
  (mean -1.3%, 66% below PY2021; rebuilt -1.6 vs realized -1.4). The post has not yet been updated to match.
- Visual abstract redrawn (2026-10-27, deployed f6805db): takeaway now "low-cost relative to their regions, and
  almost all moved to the 75% sharing rate, but the reset did not raise their benchmarks on average", matching the
  revised post and preprint. Replaced on OSF z4an5/results-notebook as version 2 (same file ids): visual-abstract.png
  sha256 bcfb1e5f6b45a285..., visual-abstract.svg sha256 93c82894c20525ea..., verified through the OSF API.
- medRxiv submission (2026-10-27): version 1 submitted as MEDRXIV/2026/366643 (Health Policy, CC BY 4.0), main
  PDF and Supplement 1 byte-identical to mssp-paper-2026 at the README's recorded commit (hashes checked on medRxiv's
  proof page). The form's scope path: "Clinical research article with new results"; human data = yes, only openly
  available public data = yes (data.cms.gov download pages given), not a prospective interventional study;
  preregistration DOI as the protocol link. The form silently converts non-ASCII characters to HTML entities, so its
  text fields were entered as plain ASCII. Awaiting screening; a v2 is planned after an outside reviewer.
- i-JMR package (2026-10-28): the same manuscript reformatted as a JMIR Original Paper for the *Interactive Journal
  of Medical Research*, using the JMIR tooling from the yuimedi-paper repository (its validator, adapted, and its
  JMIR guidance). medRxiv v1 is frozen as the tag `medrxiv-v1`; the JMIR version is on the unpushed branch
  `ijmr-submission` of mssp-paper-2026. What JMIR's rules changed:
  - the title, to "Early Renewal of Accountable Care Organization Agreements to Reset Benchmarks in the Medicare
    Shared Savings Program: Preregistered Retrospective Cohort Study" (JMIR wants a descriptive title naming the
    design, with no abbreviations; the first review had asked for the design in the title too);
  - the abstract headings, an Ethical Considerations section citing 45 CFR 46.102(e)(1), and JMIR's end sections;
  - italics instead of bold, P values without spaces, and URLs moved into the references;
  - the STROBE checklist, now Multimedia Appendix 2.

  No number changed. Two JMIR rules were new: since October 2026, generative AI use is declared in a submission-form
  question rather than in the Acknowledgments, and JMIR asks for the AI transcripts as an appendix. The author chose
  to give a summary instead, because the sessions also cover unrelated work. Other facts gathered:
  - i-JMR's Original Paper fee is US $1985 on acceptance; JMIRx Med's is $1000, and it is named as the transfer
    choice.
  - Submitting directly was chosen over medRxiv's transfer to JMIR.
  - JMIR requires suggested reviewers. The shortlist (first authors of cited MSSP studies, from PubMed records) is
    kept out of the public repository, as are the copies of JMIR's help pages.
- i-JMR framing (2026-10-28): two cold reads by fresh agents scored the contribution 2 of 5 for a general reader and
  3 for a specialist. The root cause was that the headline rests on secondary and post hoc results, not on the
  registered primary measure, while the abstract framed only the reset motive. The manuscript now:
  - states both motives up front, and says why the pull was primary and the total gain secondary;
  - flags the registered H2b wording ("beyond past savings") as overstated once the decomposition is known;
  - quotes CMS's 2018 reason for barring moves from BASIC to ENHANCED (83 FR 67859): CMS named early renewal, with
    its reset, as the way to make the move;
  - reads the data, as interpretation only, as fitting the sharing-rate motive better;
  - adds Weitzman 1980, Einav et al. 2022, a Cappello 2026 dissertation (found in a Scholar Labs novelty check) and
    the program's size from CMS's 2026 fact sheet.

  A new post hoc check (`posthoc/pull_savings.py`, not registered) finds a rank correlation of 0.45 between the pull
  and the PY2020 savings rate, so the pull is related to past savings without restating them. AI cold reads stopped
  there, with the outside human reviewer planned for medRxiv version 2 as the real test.
- Zenodo archive (2026-10-28): mssp-paper-2026 is connected to Zenodo. Zenodo's repository list was 9 months old,
  and "Sync now" made the renamed repository appear. The i-JMR branch was merged into `main`, so the public
  repository matches the submission, and the tag `medrxiv-v1` keeps version 1. `CITATION.cff`, `.zenodo.json` and
  byte-identical copies of the 2 post hoc scripts were added. Releases v1.0.0 and v1.1.0 were archived; the concept
  DOI is 10.5281/zenodo.23737045 (v1.1.0: 10.5281/zenodo.23737104), and the manuscript's Data Availability cites it,
  so the uploaded Word file points to its own archive. A DOI exists only after the first release, which is why there
  were two releases.
- i-JMR submission (2026-10-28): submitted as manuscript 115640, an Original Paper in the Health Services Research
  section, with open participation review and JMIR Preprints, from the files archived as Zenodo v1.2.0
  (doi:10.5281/zenodo.23740845). The steps that needed judgment:
  - 4 suggested reviewers: first authors of cited MSSP studies, with current emails from PubMed records and faculty
    pages.
  - The AI declaration: the session logs showed Claude proposed the topic (in the job-search planning session) and
    drafted the plan's question, hypotheses, decision rules and methods, so every purpose except translation was
    declared, plus a summary for the editor.
  - A Word-table fix: pandoc sizes Word tables to a 5.5 in text width, which broke values across lines; found by
    exporting the files through Pages.
  - Table 4 moved to the appendix.
  - No homepage image: JMIR's homepage images allow no text or diagrams, so the visual abstract can't be one.
  - JMIR renames uploads itself, so pre-renamed appendix files are unnecessary.
  - The stored abstract was checked after submission: plain ASCII and complete.
- medRxiv declined (2026-10-28): medRxiv declined the preprint the day after submission. It requires authors to have
  an organizational affiliation that provides oversight of research, and the author is an independent researcher, so
  it was never posted. The i-JMR submission's JMIR Preprints posting is the preprint instead. The paper repository's
  README and its release notes were corrected; the Zenodo copies of the notes keep the earlier "in screening". The
  cover letter to i-JMR had described the preprint as in screening, so the author is sending the editor a
  correction. Lesson: check a preprint server's affiliation requirements before choosing it as an independent
  researcher (OSF Preprints is the noted fallback; its own requirements were not checked).
- Post synced with the submitted manuscript (2026-10-28, deployed c514575):
  - no mention of a preprint;
  - an AI disclosure matching the i-JMR declaration;
  - the third post hoc check and the sharing-rate reading;
  - links to the manuscript repository and its Zenodo archive, without naming the journal;
  - the new literature.

  Footnotes are numbered in the order of their definitions, so the References list was re-sorted by first citation.
  The lessons from the session went into `CLAUDE.md` here and a new `CLAUDE.md` in mssp-paper-2026.
- Distribution (2026-10-29): two days after publishing, the post had no outside readers. Its only engaged visit was the
  author's phone, once the author's browsers were excluded from the analytics (`analysis/site-analytics/BUILD-NOTES.md`).
  Almost all traffic arrived direct, and search had not yet indexed the post, so it was shared on
  [LinkedIn](https://www.linkedin.com/posts/samuelharrold_healtheconomics-valuebasedcare-causalinference-share-7521508274597441536-PqS7/).
  The share leads with the answer: early renewers were already beating their benchmarks, and most moved to the 75%
  track. It adds why the result matters as a baseline for the 2024 rules, and links the post (tagged
  `utm_source=linkedin` so the visits can be measured), the OSF registration and the manuscript repository. A first
  draft gave findings without the "so what"; it was revised before posting. Medium and Substack were left for later:
  Medium only as an import with the site marked as the original, and Substack only once there is a regular schedule.
- Measuring the share (2026-10-29): #78 tracks a `/analytics` check about a week after the LinkedIn share. The
  tagged link is now a CLAUDE.md rule for sharing posts elsewhere.
- Video slides (2026-10-29): a 26-slide deck for a narrated video ("Resetting the Target Early"), with the narration
  script in the speaker notes, is stored as
  `content/static/20261027-preregistered-mssp-early-renewal/video-slides.pptx`. Its figures were checked against the
  post and the results files before storing (the "two-thirds got a lower target" opening is the post hoc result:
  19 of 29). It explains the study for a general audience, with a made-up $11,000 example of how a reset works, and
  ends with the AI disclosure and the links.
