Title: Predicting household income from census data
Status: draft
Date: 2015-12-30T12:00:00Z
Modified: 2014-12-30T12:00:00Z
Tags: machine-learning, predictive-analytics, how-to, python, regression
Category: Machine Learning
Slug: 20151230-predict-income-from-census
Related_posts: 20151208-ipynb-on-gce-from-chrome
Authors: Samuel Harrold
Summary: I predict a household's income using data from the Census Bureau.

[TOC]

## Overview

The [Census Bureau](https://www.census.gov/about/what.html) collects data from people in the United States throughout the year. Federal, state, and local governments use the data to assess how constituents are represented and to allocate spending. The data is also made freely available to the public. In this post I predict a household's total annual income using the Census Bureau's [American Community Survey (ACS)](http://www.census.gov/programs-surveys/acs/about.html).

## Motivations

**Why am I using Python instead of R?**

This project can be done using R, Python, and/or other languages.[^rvpy] I'm using Python, especially [scikit-learn](http://scikit-learn.org/), to optimize computational performance and to make an extensible, maintainable pipeline.

**Why am I using the American Community Survey (ACS)?**

* The ACS is a relevant dataset. The goal of this project is to predict the income for a household given characteristics of that household, which is among the [subjects that the ACS survey addresses](http://www.census.gov/programs-surveys/acs/guidance/subjects.html).
* The ACS is a cultivated, thorough dataset.[^acs-method] The ACS has many quality controls to ensure that it is representative, and it samples about 3&nbsp;million addresses per year with a response rate often over 95%.
* The ACS is a timeseries dataset. The ACS samples continuously and releases data once per year. As a timeseries, the data can be used to predict current and future quantities, which is future step for this project.
* <span id="problematic">However, I recognize that using ACS data can be problematic.</span> Data from the Census Bureau has been used for harm,[^data-harm] and current ACS terminology asks respondents to identify by terms such as "race".[^prob-race] For this project, I take data from the Census Bureau at face value and I infer from it at face value. It's important to respect that these aren't simply data points; these are people.

**Why am I using the ACS household-level data?**

Companies collect information on their consumers[^cr-dbs] and consumers often spend on behalf of their household.[^bea-pce] Connecting ACS household-level data with the personal-level data is a future step for this project.

**Why am I using the ACS 5-year estimate?**

As of Dec 2015, the ACS offers two windowing options for their data releases, 1-year estimates and 5-year estimates.[^acs-ests] Because the ACS 5-year estimates aggregate data over a 5-year window, they have the largest sample and thus the highest precision for modeling small populations. However, the sample size comes at the expense of currency. Forecasting the predictions from a 5-year window to a specific year is a future step for this project.

## Predicting household income

* TODO:
    * Purpose: Predict total annual household income.
    * ETL: docs, data dict, zip file, check user verification files, format data dictionary file, imputation (knn?)
        * I start with a running Google Cloud VM instance and Jupyter Notebook server following a previous post, ["Running an Ipython Notebook on Google Compute Engine from Chrome"](/20151208-ipynb-on-gce-from-chrome.html).
        * [Create and mount a disk](https://cloud.google.com/compute/docs/disks/persistent-disks) to the instance for storage.[^services]
        * Download the [ACS data via FTP](https://www.census.gov/programs-surveys/acs/data/data-via-ftp.html):[^no-api]  
        `$ sudo curl --remote-name <url>` where the downloaded URLs were  
        `http://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict13.txt`  
        `http://www2.census.gov/programs-surveys/acs/data/pums/2013/5-Year/csv_hus.zip`
        * The Public Use Microdata Sample (PUMS)[^pums] has more features than the summary data sets but low geographic resolution to protect respondents' privacy &mdash; the Public Use Microdata Areas (PUMAs) each have at least 100K people.
    * Feature extraction: map PUMA to lat-lon, map cat cols to heir cols, incremental PCA, clustering, informative priors, create cross-term features?
    * Data mining: feature corrs, household corrs, pairplots, dim-red vis
    * Predictive analytics: random forest with grid search, 5-fold cross-validation, get confidence intervals, partial dependence plots with decomposed eigenvectors

## Helpful links

Some links I found helpful for this blog post:

* ACS and census data:
    * [ACS Guidance for Data Users](https://www.census.gov/programs-surveys/acs/guidance.html) describes how to get started with ACS data.
    * [ACS Library](https://www.census.gov/programs-surveys/acs/library.All.html) includes example reports and infographics using ACS data.
    * [ACS methodology](http://www.census.gov/programs-surveys/acs/methodology.html) includes design details, sample sizes, coverage estimates, and past questionnaires.
    * Kaggle competition, [2013 American Community Survey](https://www.kaggle.com/census/2013-american-community-survey).
    * <a href="https://archive.ics.uci.edu/ml/datasets/Census-Income+(KDD)" type="text/html">UCI Census-Income (KDD) Data Set</a>, see "Papers That Cite This Data Set".
    * <a href="https://archive.ics.uci.edu/ml/datasets/US+Census+Data+(1990)" type="text/html">UCI US Census Data (1990) Data Set</a>, see "Papers That Cite This Data Set".
    * [Predicting Income Level, An Analytics Casestudy in R](http://www.knowbigdata.com/blog/predicting-income-level-analytics-casestudy-r).
    * RPubs, [Predict Income Range](https://rpubs.com/Jovin/census_data_income).
    * Mathematica for prediction algorithms, [Classification and association rules for census income data](https://mathematicaforprediction.wordpress.com/2014/03/30/classification-and-association-rules-for-census-income-data/).
    * [Using PUMS Census data](http://www-rohan.sdsu.edu/~gawron/python_for_ss/course_core/book_draft/data/PUMS_data.html) from a social science perspective.
* Analysis:
    * ["Statistics for Hackers", Jake VanderPlas](https://speakerdeck.com/jakevdp/statistics-for-hackers): Evaluating statistical significance by sampling, cross-validation, etc.
    * [Scikit-learn user guide](http://scikit-learn.org/stable/user_guide.html): Copious examples of machine learning tasks.

## Footnotes
<!-- From https://pythonhosted.org/Markdown/extensions/footnotes.html -->
///Footnotes Go Here///

<!-- ## Overview -->
<!-- ## Motivations -->
[^rvpy]:
    See the popular discussion ["R vs Python for data analysis"](http://programmers.stackexchange.com/questions/181342/r-vs-python-for-data-analysis) on StackExchange Programmers.
[^acs-method]:
    [ACS methodology](http://www.census.gov/programs-surveys/acs/methodology.html) includes design details, sample sizes, coverage estimates, and past questionnaires.
[^data-harm]:
    Data from the Census Bureau was used to identify Japanese communities as part of the internment of US citizens and residents with Japanese ancestry during World&nbsp;War&nbsp;II. See the [ACLU's FAQ section about census data](https://www.aclu.org/frequently-asked-questions-national-census) and the [Wikipedia article "Internment of Japanese Americans"](https://en.wikipedia.org/wiki/Internment_of_Japanese_Americans).
[^prob-race]:
    "Race" is a problematic term with historical connotations and conflicts between self-identification and labeling by others. As of Dec 2015, the [ACS refers to "race" and "ethnicity" separately](http://www2.census.gov/programs-surveys/acs/methodology/questionnaires/2015/quest15.pdf). The American Anthropological Association [recommended in 1997](http://s3.amazonaws.com/rdcms-aaa/files/production/public/FileDownloads/pdfs/cmtes/minority/upload/AAA_Response_OMB1997.pdf) that questions about "race" and "ethnicity" are ambiguous given the historical context and would be better phrased as about "race/ethnicity". For this project, I refer to "race" and "ethnicity" as "race/ethnicity". The following links are also helpful:  
    <ul>
    <li>[Census Bureau's statement about "race" (2013)](http://www.census.gov/topics/population/race/about.html)</li>
    <li>[Office of Management and Budget, "Standards for the Classification of Federal Data on Race and Ethnicity" (1994), Appendix Directive No.&nbsp;15 (1977)](https://www.whitehouse.gov/omb/fedreg_notice_15/)</li>
    <li>[Office of Management and Budget, "Review of the Racial and Ethnic Standards to the OMB Concerning Changes" (Jul&nbsp;1997)](https://www.whitehouse.gov/omb/fedreg_directive_15)</li>
    <li>[Office of Management and Budget, "Revisions to the Standards for the Classification of Federal Data on Race and Ethnicity" (Oct&nbsp;1997)](https://www.whitehouse.gov/omb/fedreg_1997standards)</li>
    <li>[American Anthropological Association, "Statement on Race" (1998)](http://www.americananthro.org/ConnectWithAAA/Content.aspx?ItemNumber=2583)</li>
    <li>[Wikipedia article "Race and ethnicity in the United States Census"](https://en.wikipedia.org/wiki/Race_and_ethnicity_in_the_United_States_Census)</li>
    </ul>
[^cr-dbs]:
    See [examples of consumer databases](http://www.consumerreports.org/cro/money/consumer-protection/big-brother-is-watching/overview/index.htm) from Consumer Reports and how they're used.
[^bea-pce]:
    The Bureau of Economic Analysis measures [personal consumption expenditures](http://www.bea.gov/newsreleases/regional/pce/pce_newsrelease.htm) on a per-household basis.
[^acs-ests]:
    The ACS 3-year estimates are discontinued; 2013 is the last year included in the 3-year estimates. For guidance in choosing, accessing, and using a dataset, see [Guidance for Data Users](https://www.census.gov/programs-surveys/acs/guidance.html).
<!-- ## Predicting household income -->
[^services]:
    This project mounts a single disk for storage to a single instance and keeps the data in RAM for queries. A scaled version of this pipeline on the Google Cloud Platform may include integrated services such as [Cloud Storage](https://cloud.google.com/storage/) and [Big Query](https://cloud.google.com/bigquery/).
[^no-api]:
    I'm downloading the data files rather than using the [Census Bureau's API](http://www.census.gov/developers/) because this project requires one-time access to all data rather than dynamic access to a subset of the data.
[^pums]:
    See the ACS guidebook ["What Public Use Microdata Sample Users Need to Know" (2009)](https://www.census.gov/library/publications/2009/acs/pums.html).
