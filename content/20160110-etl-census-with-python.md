Title: Extract transform load census data with Python
Status: draft
Date: 2016-01-10T12:00:00Z
Modified: 2016-01-10T12:00:00Z
Tags: etl, how-to, python, pandas
Category: ETL
Slug: 20160110-etl-census-with-python
Related_posts: 20151208-ipynb-on-gce-from-chrome
Authors: Samuel Harrold
Summary: I parse, load, and validate data from the Census Bureau's American Community Survey using Python.

[TOC]

## Overview

The [Census Bureau](https://www.census.gov/about/what.html) collects data from people in the United States throughout the year. Federal, state, and local governments use the data to assess how constituents are represented and to allocate spending. The data is also made freely available to the public and has a wide range of use cases.[^use-cases] In this post I parse, load, and validate data from the Census Bureau's [American Community Survey (ACS)](http://www.census.gov/programs-surveys/acs/about.html) [2013 5-year Public Use Microdata Sample (PUMS)](https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.2013.html) for Washington&nbsp;DC.

Brief process:

* Start with a running Google Cloud VM instance and Jupyter Notebook server following ["Running an Ipython Notebook on Google Compute Engine from Chrome"](/20151208-ipynb-on-gce-from-chrome.html).
    * For additional storage, [create and mount a disk](https://cloud.google.com/compute/docs/disks/persistent-disks) to the instance.
* Download (and decompress):[^ftp] [^no-api]
    * 2013 5-year PUMS data dictionary: [PUMS_Data_Dictionary_2009-2013.txt](http://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2009-2013.txt) (<1&nbsp;MB)
    * 2013 5-year PUMS person and housing records for Washington DC:
        * Person records: [csv_pdc.zip](http://www2.census.gov/programs-surveys/acs/data/pums/2013/5-Year/csv_pdc.zip) (5&nbsp;MB compressed, 30&nbsp;MB decompressed)
        * Housing records: [csv_hdc.zip](http://www2.census.gov/programs-surveys/acs/data/pums/2013/5-Year/csv_hdc.zip) (2&nbsp;MB compressed, 13&nbsp;MB decompressed)
    * 2015 5-year PUMS estimates for user verification: [pums_estimates_9_13.csv](http://www2.census.gov/programs-surveys/acs/tech_docs/pums/estimates/pums_estimates_9_13.csv) (<1&nbsp;MB)
* Load the files:
    * Data dictionary TXT: `dsdemos.census.parse_pumsdatadict` (see `dsdemos` package <a href="/20160110-etl-census-with-python.md#src">below</a>)  
    This is a customized parser I wrote for `PUMS_Data_Dictionary_2009-2013.txt`. The data dictionary is inconsistently formatted, which complicates parsing.
    * Person/housing and verification CSVs: `pandas.read_csv` [^pd-csv] [^pd-py35]
* Verify calculations of estimates (example <a href="/20160110-etl-census-with-python.html#verify">below</a>):[^pums-acc]
    * To select columns by condition in `pandas`, I prefer creating a pandas series with booleans as true-false mask (e.g. `tfmask = np.logical_and(25 <= df['AGEP'], dfp['AGEP'] <= 34)`) then filtering using the true-false mask as an index (e.g. `df_new = df.loc[tfmask, ['AGEP', 'WGTP']]`).[^pd-loc]
    * To calculate an estimate $X$ (also called a "characteristic"), sum the column `'[P]WGTP'` of the filtered data.
    * To calculate the estimate's "direct standard error", use the ACS's modified root-mean-square deviation:  
    $ \mathrm{SE}(X) = \sqrt{ \frac{4}{80} \sum_{r=1}^{80}(X_r-X)^2 } $  
    where each $X_r$ is the sum of the column `'[P]WGTPr'` of the filtered data.
    * To calculate the estimate's "margin of error" (defined by ACS at the 90% confidence level):  
    $ \mathrm{MOE}(X) = 1.645\,\mathrm{SE}(X) $

<span id="source">Source code:</span>

* For step-by-step, see the Jupyter Notebook (click the HTML export to render in-browser):  
[20160110-etl-census-with-python.ipynb]({filename}/static/20160110-etl-census-with-python/20160110-etl-census-with-python.ipynb)  
[20160110-etl-census-with-python-full.html]({filename}/static/20160110-etl-census-with-python/20160110-etl-census-with-python-full.html)
* For the `dsdemos` package, see TODO: versioned links.

## Motivations

**Why am I using the American Community Survey (ACS)?**

* The ACS is a relevant data set. A future step is to predict an individual's household income, which is among the [subjects that the ACS survey addresses](http://www.census.gov/programs-surveys/acs/guidance/subjects.html).
* The ACS is a cultivated, thorough data set.[^acs-method] The ACS has many quality controls to ensure that it is representative. The survey samples about 3&nbsp;million addresses per year with a response rate often over 95%.
* The ACS is a timeseries data set. The survey sends questionnaires throughout the year and releases data once per year. As a timeseries, the data can be used for forecasting analytics, which is future step.
* <span id="problematic">I recognize that using ACS data can be problematic.</span> Data from the Census Bureau has been used for harm,[^data-harm] and current ACS terminology asks respondents to identify by terms such as "race".[^prob-race] For this project, I take data from the Census Bureau at face value and I infer from it at face value. It's important to respect that these aren't simply data points; these are people.

**Why am I using the ACS 5-year estimate?**

As of Dec 2015, the ACS offers two windowing options for their data releases, 1-year estimates and 5-year estimates.[^acs-ests] Because the ACS 5-year estimates include data over a 5-year window, they have the largest sample size and thus the highest precision for modeling small populations. However, the sample size comes at the expense of currency. Forecasting the predictions from a 5-year window to be relevant to a specific year is a future step.

**Why am I using Python?**

This project can be done using Python, R, and/or other languages.[^rvpy] I'm using Python since a future step is to make an extensible, optimized pipeline, which is a popular application for [scikit-learn](http://scikit-learn.org/).

**What about "big data"?**

I'm staring with a data set small enough to be processed in memory (i.e. operated on in RAM), since the focus of many Python packages is in-memory operations on single machines.[^pydata] Within these packages, operations are often parallelized across the processor cores within the machine. For operations that exceed the available RAM on the machine (i.e. out-of-core computations), there's [Dask](http://dask.pydata.org/en/latest/) for Python, and for operations that require a cluster of machines, there's [Spark](http://spark.apache.org/) for Java, Scala, Python, and R. Scaling a pipeline to large enough data that requres a cluster is a future step.

## <span id="verify">Example verification</span>

This is an example of how to replicate the calculations from a PUMS user verification file, `pums_estimates_9_13.csv`. The Jupyter Notebook <a href="/20160110-etl-census-with-python.md#src">above</a> has my full procedure.

A row from `pums_estimates_9_13.csv`:

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>&nbsp;</th>
      <th>st&nbsp;</th>
      <th>state&nbsp;</th>
      <th>characteristic&nbsp;</th>
      <th>pums_est_09_to_13&nbsp;</th>
      <th>pums_se_09_to_13&nbsp;</th>
      <th>pums_moe_09_to_13&nbsp;</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>300&nbsp;</th>
      <td>11&nbsp;</td>
      <td>District of Columbia&nbsp;</td>
      <td>Age 25-34&nbsp;</td>
      <td>134,025&nbsp;</td>
      <td>526&nbsp;</td>
      <td>865&nbsp;</td>
    </tr>
  </tbody>
</table>

With `pums_estimates_9_13.csv` loaded as `dfe`, `ss13pdc.csv` person records file loaded as `dfp` (extracted from `csv_pdc.zip`), and `import numpy as np`:  

```python
# Imports
import numpy as np
import pandas as pd
# Load
# Select the verification estimates for Washington DC
# then for the "characteristic" 'Age 25-34'.
tfmask_dc = dfe['state'] == 'District of Columbia'
dfe_dc = dfe.loc[tfmask_dc]
char = 'Age 25-34'
tfmask_ref = dfe_dc['characteristic'] == char
# Select the person records for the characteristic.
tfmask_test = np.logical_and(25 <= dfp['AGEP'], dfp['AGEP'] <= 34)
# Calculate the estimate ('est') for the characteristic,
# which is a weighted sum, using sample weights 'PWGTP'.
pwt = 'PWGTP'
ref_est = int(dfe_dc.loc[tfmask_ref, 'pums_est_09_to_13'].values[0].replace(',', ''))
test_est = dfp.loc[tfmask_test, pwt].sum()
assert np.isclose(ref_est, test_est, rtol=0, atol=1)
# Calculate the direct standard error ('se') of the estimate
# using replicate weights 'PWGTP[1-80]'.
pwts = pwts = [pwt+str(inum) for inum in range(1, 81)]
ref_se = dfe_dc.loc[tfmask_ref, 'pums_se_09_to_13'].values[0]
test_se = ((4/80)*((dfp.loc[tfmask_test, wts].sum() - test_est)**2).sum())**0.5
assert np.isclose(ref_se, test_se, rtol=0, atol=1)
# Calculate the margin of error ('moe') at the 90% confidence level (+/- 1.645 standard errors)
ref_moe = dfe_dc.loc[tfmask_ref, 'pums_moe_09_to_13'].values[0]
test_moe = 1.645*test_se
assert np.isclose(ref_moe, test_moe, rtol=0, atol=1)
```

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
[^use-cases]:
    Some use cases for the Census Bureau's American Community Survey with data access recommendations: [ACS Which Data Tool](https://www.census.gov/acs/www/guidance/which-data-tool/)
[^ftp]:
    For how to download [ACS data via FTP](https://www.census.gov/programs-surveys/acs/data/data-via-ftp.html):  
    `$ sudo curl --remote-name <url>`  
    Decompress the `.zip` files with `unzip`.
[^no-api]:
    I'm downloading the data files rather than using the [Census Bureau's API](http://www.census.gov/developers/) because this project requires one-time access to all data rather than dynamic access to a subset of the data.
[^pd-csv]:
    [Docs for `pandas.read_csv`](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html)
[^pd-py35]:
    Pandas 0.17.1 has a compatibility issue with Python 3.5. See [GitHub pandas issue 11915](https://github.com/pydata/pandas/issues/11915) for a temporary fix. The issue should be resolved for pandas 0.18+.
[^pums-acc]:
    For the formulas to caluclate the estimates, the direct standard error, and the margin of error, see [2013 5-year PUMS Accuracy](http://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2009_2013AccuracyPUMS.pdf), section 7, "Measuring Sampling Error".
[^pd-loc]:
    [Docs for `pandas.DataFrame.loc`](http://pandas.pydata.org/pandas-docs/version/0.17.1/generated/pandas.DataFrame.loc.html)
<!-- ## Motivations -->
[^rvpy]:
    See the popular discussion ["R vs Python for data analysis"](http://programmers.stackexchange.com/questions/181342/r-vs-python-for-data-analysis) on StackExchange Programmers.
[^acs-method]:
    The [ACS methodology](http://www.census.gov/programs-surveys/acs/methodology.html) includes design factors, sample sizes, coverage estimates, and past questionnaires.
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
[^acs-ests]:
    The ACS 3-year estimates are discontinued; 2013 is the last year included in the 3-year estimates. For guidance in choosing, accessing, and using a data set, see [Guidance for Data Users](https://www.census.gov/programs-surveys/acs/guidance.html).
[^pydata]:
    See the [PyData stack](http://pydata.org/downloads/) for a collection of performant Python packages.
<!-- ## ETL process -->
[^services]:
    This project mounts a single disk for storage to a single instance and keeps the data in RAM for queries. A scaled version of this pipeline on the Google Cloud Platform may include integrated services such as [Cloud Storage](https://cloud.google.com/storage/) and [Big Query](https://cloud.google.com/bigquery/).
