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

**Why am I using the American Community Survey?**

* TODO: notes from google keep.

**Why am I using the ACS household-level data?**

* Companies collect information on their consumers[^cr-dbs] and consumers often spend on behalf of their household[^bea-pce].
* Connecting ACS household-level data with the personal-level data is a future step for this project.

**Why am I using the ACS 5-year estimate?**

* TODO:
    * Highest granularity
    * Forecasting the 5-year estimate to be windowed on the current and next years is a future step for this project.

## Predicting household income

* TODO:
    * Purpose
    * ETL: docs, data dict, zip file, check validation files, imputation (knn?)
    * Feature extraction: map cat cols to heir cols, incremental PCA, clustering, informative priors, create cross-term features?
    * Data mining: feature corrs, household corrs, pairplots, dim-red vis
    * Predictive analytics: random forest with grid search, 5-fold cross-validation, get confidence intervals, partial dependence plots with decomposed eigenvectors


## Footnotes
<!-- From https://pythonhosted.org/Markdown/extensions/footnotes.html -->
///Footnotes Go Here///

[^cr-dbs]:
    [Examples of consumer databases](http://www.consumerreports.org/cro/money/consumer-protection/big-brother-is-watching/overview/index.htm) from Consumer Reports and how they're used.
[^bea-pce]:
    [Personal consumption expenditures](http://www.bea.gov/newsreleases/regional/pce/pce_newsrelease.htm) from the Bureau of Econonic Analysis are measured on a per-household basis.
