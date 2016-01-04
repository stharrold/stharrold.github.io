Title: Predicting household income from census data
Status: draft
Date: 2016-02-01T12:00:00Z
Modified: 2016-02-01T12:00:00Z
Tags: machine-learning, predictive-analytics, how-to, python, regression
Category: Machine Learning
Slug: 20160201-predict-household-income-from-census
Related_posts: 20160110-etl-census-with-python
Authors: Samuel Harrold
Summary: I predict a household's income using data from the Census Bureau's American Community Survey.

[TOC]

## Overview

## Motivations

**Why am I using the ACS household-level data?**

Companies collect information on their consumers[^cr-dbs] and consumers often spend on behalf of their household.[^bea-pce] Connecting ACS household-level data with the personal-level data is a future step for this project.


## Predicting household income

* TODO:
    * Purpose: Predict total annual household income.
    * Feature extraction: map PUMA to lat-lon, map cat cols to heir cols, incremental PCA, clustering, informative priors, create cross-term features?
    * Data mining: feature corrs, household corrs, pairplots, dim-red vis
    * Predictive analytics: random forest with grid search, 5-fold cross-validation, get confidence intervals, partial dependence plots with decomposed eigenvectors

    * The Public Use Microdata Sample (PUMS)[^pums] has more features than the summary data sets but low geographic resolution to protect respondents' privacy &mdash; the Public Use Microdata Areas (PUMAs) each have at least 100K people.

## Helpful links

Some links I found helpful for this blog post: TODO

## Footnotes
<!-- From https://pythonhosted.org/Markdown/extensions/footnotes.html -->
///Footnotes Go Here///

<!-- ## Overview -->
<!-- ## Motivations -->
[^cr-dbs]:
    See [examples of consumer databases](http://www.consumerreports.org/cro/money/consumer-protection/big-brother-is-watching/overview/index.htm) from Consumer Reports and how they're used.
[^bea-pce]:
    The Bureau of Economic Analysis measures [personal consumption expenditures](http://www.bea.gov/newsreleases/regional/pce/pce_newsrelease.htm) on a per-household basis.
<!--## Predicting household income-->
[^pums]:
    See the ACS guidebook ["What Public Use Microdata Sample Users Need to Know" (2009)](https://www.census.gov/library/publications/2009/acs/pums.html).
<!-- ## Helpful links -->
