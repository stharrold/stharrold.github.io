# Literature search for the write-up (related work)

Searches run after the analysis, to place the post in the existing literature. They inform the write-up only; they
change nothing in the registered plan or code. Searches use Google Scholar Labs (an AI-overview search over scholarly
papers, about 3 queries a day), run through the `scholar-labs-search` skill in a signed-in Chrome. Each query's raw
output is saved here as JSON (title, URL, and the page text with Scholar Labs' summaries); publisher session tokens
were removed from URLs. `parse_scholar_labs.py` turns each raw file into one record per paper (`*_papers.json`: title,
link, byline, Scholar Labs' summary sentence and labeled bullets, cited-by count), copied verbatim. "More results"
was clicked once per query; it did not use a query. Every paper cited in the post is checked against Crossref by DOI first.

## Question

What prior research exists on (a) MSSP benchmark rebasing, the regional adjustment and the incentives they create
(including early renewal), and (b) which ACOs select into two-sided risk or leave the program?

## Queries

| UTC | Query | Status | Raw output |
|---|---|---|---|
| 2026-10-27 16:22:14 | `benchmark rebasing incentives in the Medicare Shared Savings Program` | ok, 10 results, then 20 after one "More results" | `20261027T162214Z_scholar-labs_q1_raw.json`, `..._q1_more1_raw.json` (20 papers); parsed: `..._q1_papers.json`, `..._q1_more1_papers.json` |
| 2026-10-27 16:22:33 | `accountable care organization exit and risk track selection in the Medicare Shared Savings Program` | bounced ("not designed for queries like this"; a free re-read confirmed it) | `20261027T162233Z_scholar-labs_q2_raw.json`, `..._q2_reread.json` |
| 2026-10-27 16:32:33 | `early renewal of accountable care organization agreements in the Medicare Shared Savings Program` | ok, 10 results, then 12 after one "More results" (the page reports 12 relevant) | `20261027T163233Z_scholar-labs_q3_raw.json`, `..._q3_more1_raw.json`; parsed: `..._q3_papers.json`, `..._q3_more1_papers.json` |

Query 2 asked two things at once and was bounced; it still used a query. Exit and participation are covered by
query 1's results, so a narrower follow-up is about selection into two-sided risk.

## Results of query 1, with relevance

Crossref-verified entries give the DOI; the others are listed as returned.

| Paper | Verified | Relevance to this study |
|---|---|---|
| Lyu, P. F., Chernew, M. E. and McWilliams, J. M. (2023). Benchmarking changes and selective participation in the Medicare Shared Savings Program. *Health Affairs* 42(5), 622-631. | doi:10.1377/hlthaff.2022.01061 | High. Adding regional spending to benchmarks from 2017 drew in ACOs and practices with lower baseline spending (selective participation); discusses ratchet effects of rebasing. The closest prior work: selection on benchmark position. |
| Chen, A. J. and McWilliams, J. M. (2025). How benchmark changes affect participation in accountable care organizations: prospects for voluntary payment models. *American Journal of Health Economics* 11(1), 38-62. | doi:10.1086/726748 | High. Participation responds to benchmark changes; the same mechanism behind choosing when to reset. |
| Rose, S., Zaslavsky, A. M. and McWilliams, J. M. (2016). Variation in accountable care organization spending and sensitivity to risk adjustment: implications for benchmarking. *Health Affairs* 35(3), 440-448. | doi:10.1377/hlthaff.2015.1026 | High. ACO spending varies widely relative to local spending after case-mix adjustment, so regional benchmarks shift unevenly. (Scholar Labs' summary also credits it with the ratchet point; its abstract does not say that.) |
| Chernew, M. E., McWilliams, J. M. and Shah, S. (2023). The case for administrative benchmarks (and some challenges). *NEJM Catalyst* 4(10). | doi:10.1056/CAT.23.0194 | Medium. Administratively set benchmarks to break the ratchet; context for the 2024 rules (ACPT). |
| Srivastava, A., et al. (2026). Accountable care organization efficiency on entry and shared savings bonuses. *JAMA Network Open*. | doi:10.1001/jamanetworkopen.2026.0166 (title and journal matched; authors not yet checked) | Medium. Entry efficiency and bonuses; selection on spending at entry. |
| Jacobs, D., Rawal, P., Fowler, L. and Seshamani, M. (2022). Expanding accountable care's reach among Medicare beneficiaries. *New England Journal of Medicine* 387(2), 99-102. | doi:10.1056/NEJMp2202991 | Low to medium. CMS's stated direction for accountable care; policy context. |
| McWilliams, J. M., Chen, A. and Chernew, M. E. (2021). From vision to design in advancing Medicare payment reform: a blueprint for population-based payments. USC-Brookings Schaeffer Initiative (report). | report, no DOI | Medium. Benchmark design proposals, including the ratchet. |
| CMS (2016). Revised benchmark rebasing methodology. Final rule (Federal Register). | PubMed 27295736 | Background: the rule that introduced regional spending in rebasing (agreements from 2017). |
| Harvey, H. B., et al. (2014). The ephemeral accountable care organization. *Journal of the American College of Radiology*. | not checked | Low. Early commentary on ACO churn. |
| "Part V" (aapc.com PDF of a 2016 Federal Register document) | not a paper | Not used. |

## Used in the post

Each was checked against Crossref by DOI, and each claim in the post against the paper's abstract (Europe PMC or
Crossref), not only against Scholar Labs' summary. Scholar Labs summarized Rose et al. (2016) as finding that
rebasing weakens savings incentives; the abstract does not say that, so the post cites it for what the abstract
does say (wide variation in ACO spending relative to local spending after case-mix adjustment), and the ratchet to
Douven et al. (2015), whose abstract does. Ying et al. (2023) and Moloci et al. (2021) are research letters without
abstracts; their claims were checked against the full texts (PDFs supplied by the author, kept in the separate
`library` repository, not here).

| Paper | DOI | Found by | Cited for |
|---|---|---|---|
| Douven, McGuire and McWilliams (2015), *Health Affairs* 34(1) | 10.1377/hlthaff.2014.0444 | q1 (more), q3 | Renewal benchmark rules weaken savings incentives; weights rewarded spending before a new agreement |
| Rose, Zaslavsky and McWilliams (2016), *Health Affairs* 35(3) | 10.1377/hlthaff.2015.1026 | q1 | ACO spending varies widely relative to local spending after case-mix adjustment |
| Lyu, Chernew and McWilliams (2023), *Health Affairs* 42(5) | 10.1377/hlthaff.2022.01061 | q1 | Selection toward providers with low spending relative to their region after 2017 |
| Chen and McWilliams (2025), *American Journal of Health Economics* 11(1) | 10.1086/726748 | q1 | ACOs with effective benchmark decreases 7 points more likely to drop out |
| Ying et al. (2024), *Health Affairs Scholar* 2(1) | 10.1093/haschl/qxad093 | q1 (more), q3 | Under Pathways, more ACOs exited than entered; leaders reassessed savings vs losses given benchmark changes |
| Ying et al. (2023), *Journal of General Internal Medicine* 38(7) | 10.1007/s11606-022-07947-x | q3 | 2019 was the first year more ACOs exited (73) than entered (65); ACOs achieving savings, and those with higher spending, were more likely to stay (the authors link the latter to the benchmark changes) |
| Moloci et al. (2021), *Journal of General Internal Medicine* 36(8) | 10.1007/s11606-020-06424-7 | q3 | 40% of Track 1 ACOs facing renewal in 2019 exited; projected lost savings up to $396.8 million by 2022 if that rate continued |

## Gap: early renewal itself

Query 3 was a clean, focused search for early renewal; its 12 results (all the page reports as relevant) include
renewal decisions, exits and benchmark rules at renewal, but no study of ACOs ending an agreement early to reset. The
post therefore says that, as far as this search found, no prior study examines early renewal itself. This is a
limited search (one engine, one query), not a systematic review.
