Title: Predicting household income from census data
Status: draft
Date: 2016-02-21T12:00:00Z
Modified: 2016-02-08T19:20:00Z
Tags: machine-learning, predictive-analytics, how-to, python, regression
Category: Machine Learning
Slug: 20160221-predict-household-income-from-census
Related_posts: 20160110-etl-census-with-python
Authors: Samuel Harrold
Summary: Predicting a household's income using data from the Census Bureau's American Community Survey.

[TOC]

## Overview

## Motivations

**Why am I using the ACS household-level data?**

Companies collect information on their consumers[^cr-dbs] and consumers often spend on behalf of their household.[^bea-pce] Connecting ACS household-level data with the personal-level data is a future step for this project.


## Predicting household income

* TODO:
    * The Public Use Microdata Sample (PUMS)[^pums] has more features than the summary data sets but low geographic resolution to protect respondents' privacy &mdash; the Public Use Microdata Areas (PUMAs) each have at least 100K people.
    * Join personal and housing files.
    * imputation (knn?)
    * Purpose: Predict total annual household income.
    * Feature extraction: map PUMA to lat-lon, map cat cols to heir cols, incremental PCA, clustering, informative priors, create cross-term features?
    * Data mining: feature corrs, household corrs, pairplots, dim-red vis
    * Predictive analytics: random forest with grid search, 5-fold cross-validation, get confidence intervals, partial dependence plots with decomposed eigenvectors
    * dask vs spark: http://dask.readthedocs.org/en/latest/spark.html
        * dask tutorial: http://nbviewer.ipython.org/github/jcrist/Dask_PyData_NYC/blob/master/Dask_DataFrame_Airline.ipynb
        * dask with scikit-learn requires partial_fit (out-of-core; different from n_jobs): http://blaze.pydata.org/blog/2015/10/19/dask-learn/, http://scikit-learn.org/stable/modules/scaling_strategies.html
        * Data size (including memoized operations on data) fit in RAM (1 machine); fit on disk (1 machine); fit in RAM (2+ machines); fit on disk (2+machines) // Job duration short enough for single CPU (1 core, 1 machine); for multiple CPUs (2+ cores, 1 machine); for multiple CPUs (2+ cores, 2+ machines)
        * use dask to select random subset (100MB) for pandas: http://dask.pydata.org/en/latest/dataframe-api.html (also use python to get file size)

## Helpful links

Some links I found helpful for this blog post: TODO

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
[^cr-dbs]:
    See [examples of consumer databases](http://www.consumerreports.org/cro/money/consumer-protection/big-brother-is-watching/overview/index.htm) from Consumer Reports and how they're used.
[^bea-pce]:
    The Bureau of Economic Analysis measures [personal consumption expenditures](http://www.bea.gov/newsreleases/regional/pce/pce_newsrelease.htm) on a per-household basis.
<!--## Predicting household income-->
[^pums]:
    See the ACS guidebook ["What Public Use Microdata Sample Users Need to Know" (2009)](https://www.census.gov/library/publications/2009/acs/pums.html).
<!-- ## Helpful links -->
