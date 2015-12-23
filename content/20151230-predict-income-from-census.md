Title: Predicting household income from census data
Status: draft
Date: 2015-12-30T12:00:00Z
Modified: 2014-12-30T12:00:00Z
Tags: predictive-analytics, how-to, python, regression, random-forest
Category: Predictive Analytics
Slug: 20151230-predict-income-from-census
Authors: Samuel Harrold
Summary: I use Census Bureau data to predict a household's income.

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
    * Data source
    * 

## Footnotes
<!-- From https://pythonhosted.org/Markdown/extensions/footnotes.html -->
///Footnotes Go Here///

[^cr-dbs]:
    [Examples of consumer databases](http://www.consumerreports.org/cro/money/consumer-protection/big-brother-is-watching/overview/index.htm) from Consumer Reports and how they're used.
[^bea-pce]:
    [Personal consumption expenditures](http://www.bea.gov/newsreleases/regional/pce/pce_newsrelease.htm) from the Bureau of Econonic Analysis are measured on a per-household basis.
