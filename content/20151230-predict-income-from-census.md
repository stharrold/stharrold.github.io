Title: Predicting household income from census data
Status: draft
Date: 2015-12-30T12:00:00Z
Modified: 2014-12-30T12:00:00Z
Tags: machine-learning, predictive-analytics, how-to, python, regression
Category: Machine Learning
Slug: 20151230-predict-income-from-census
Authors: Samuel Harrold
Summary: I predict a household's income using data from the Census Bureau.

[TOC]

## Overview

The [Census Bureau](https://www.census.gov/about/what.html) collects data from people in the United States throughout the year. Federal, state, and local governments use the data to assess how constituents are represented and to allocate spending. The data is also made freely available to the public. In this post I predict a household's total annual income using the Census Bureau's [American Community Survey (ACS)](http://www.census.gov/programs-surveys/acs/about.html).

## Motivations

**Why am I using Python instead of R?**

* TODO

**Why am I using the American Community Survey (ACS)?**

* The ACS is a relevant dataset. The goal of this project is to predict the income for a household given characteristics of that household, which is among the [subjects that the ACS survey addresses](http://www.census.gov/programs-surveys/acs/guidance/subjects.html).
* The ACS is a cultivated, thorough dataset.[^acs-method] The ACS has many quality controls to ensure that it is representative, and it samples about 3 million addresses per year with a response rate often over 95%.
* The ACS is a timeseries dataset. The ACS samples continuously and releases data once per year. As a timeseries, the data can be used to predict current and future quantities, which is future step for this project.
* With the above points in mind, I recognize that using ACS data can be problematic. Data from the Census Bureau has been used for harm,[^data-harm] and current ACS terminology asks respondents to identify by terms such as "race".[^prob-race] For this project, I take data from the Census Bureau at face value and I infer from it at face value. It's important to respect that these aren't simply data points; these are people.

**Why am I using the ACS household-level data?**

Companies collect information on their consumers[^cr-dbs] and consumers often spend on behalf of their household[^bea-pce]. Connecting ACS household-level data with the personal-level data is a future step for this project.

**Why am I using the ACS 5-year estimate?**

* TODO:
    * Highest granularity
    * Forecasting the 5-year estimate to be windowed on the current and next years is a future step for this project.

## Predicting household income

* TODO:
    * Purpose
    * ETL: docs, data dict, zip file, check validation files, imputation (knn?)
    * Feature extraction: map PUMA to lat-lon, map cat cols to heir cols, incremental PCA, clustering, informative priors, create cross-term features?
    * Data mining: feature corrs, household corrs, pairplots, dim-red vis
    * Predictive analytics: random forest with grid search, 5-fold cross-validation, get confidence intervals, partial dependence plots with decomposed eigenvectors

## Helpful links

Some links I found helpful for this blog post:

* ACS:
    * TODO

## Footnotes
<!-- From https://pythonhosted.org/Markdown/extensions/footnotes.html -->
///Footnotes Go Here///

<!-- ## Overview -->
<!-- ## Motivations -->
[^acs-method]:
    [ACS methodology](http://www.census.gov/programs-surveys/acs/methodology.html)) includes design details, sample sizes, coverage estimates, and past questionnaires.
[^data-harm]:
    Data from the Census Bureau was used to identify Japanese communities as part of the internment of US citizens and residents with Japanese ancestry during World&nbsp;War&nbsp;II. See the [ACLU's FAQ section about census data](https://www.aclu.org/frequently-asked-questions-national-census) and the [Wikipedia article "Internment of Japanese Americans"](https://en.wikipedia.org/wiki/Internment_of_Japanese_Americans).
[^prob-race]:
    "Race" is a problematic term with historical connotations and conflicts between self-identification and labeling by others. As of Dec 2015, the [ACS refers to "race" and "ethnicity" separately](http://www2.census.gov/programs-surveys/acs/methodology/questionnaires/2015/quest15.pdf). The [American Anthropological Association recommended in 1997](http://s3.amazonaws.com/rdcms-aaa/files/production/public/FileDownloads/pdfs/cmtes/minority/upload/AAA_Response_OMB1997.pdf) that questions about "race" and "ethnicity" are ambiguous given the historical context and would be better phrased as about "race/ethnicity". For this project, I refer to "race" and "ethnicity" as "race/ethnicity". The following links are also helpful:  
    [Census Bureau's statement about "race"](http://www.census.gov/topics/population/race/about.html)  
    [Office of Management and Budget, Directive 15, "Race and Ethnic Standards for Federal Statistics and Administrative Reporting"](http://wonder.cdc.gov/wonder/help/populations/bridged-race/directive15.html)  
    [American Anthropological Association, "Statement on Race"](http://www.americananthro.org/ConnectWithAAA/Content.aspx?ItemNumber=2583)  
    [Wikipedia article "Race and ethnicity in the United States Census"](https://en.wikipedia.org/wiki/Race_and_ethnicity_in_the_United_States_Census)
[^cr-dbs]:
    See [examples of consumer databases](http://www.consumerreports.org/cro/money/consumer-protection/big-brother-is-watching/overview/index.htm) from Consumer Reports and how they're used.
[^bea-pce]:
    The Bureau of Economic Analysis measures [personal consumption expenditures](http://www.bea.gov/newsreleases/regional/pce/pce_newsrelease.htm) on a per-household basis.
<!-- ## Predicting household income -->
