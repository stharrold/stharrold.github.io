Title: Extract, transform, and load census data with Python
Status: draft
Date: 2016-01-10T12:00:00Z
Modified: 2016-01-07T00:00:00Z
Tags: etl, how-to, python, pandas, census
Category: ETL
Slug: 20160110-etl-census-with-python
Related_posts: 20151208-ipynb-on-gce-from-chrome
Authors: Samuel Harrold
Summary: I parse, load, and verify data from the Census Bureau's American Community Survey using Python.

[TOC]

## Overview

The [Census Bureau](https://www.census.gov/about/what.html) collects data from people in the United States through multiple survey programs. Federal, state, and local governments use the data to assess how constituents are represented and to allocate spending. The data is also made freely available to the public and has a wide range of use cases.[^use-cases] In this post I parse, load, and verify data from the Census Bureau's [American Community Survey (ACS)](http://www.census.gov/programs-surveys/acs/about.html) [2013 5-year Public Use Microdata Sample (PUMS)](https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.2013.html) for Washington&nbsp;DC.

**Brief process:**

* Start with ["Running an IPython Notebook on Google Compute Engine from Chrome"](/20151208-ipynb-on-gce-from-chrome.html).
    * For additional storage, [create and mount a disk](https://cloud.google.com/compute/docs/disks/persistent-disks) to the instance.[^services]
* Download (and decompress):[^ftp] [^no-api]
    * 2013 5-year PUMS data dictionary: [PUMS_Data_Dictionary_2009-2013.txt](http://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2009-2013.txt) (<1&nbsp;MB)
    * 2013 5-year PUMS person and housing records for Washington DC:
        * Person records: [csv_pdc.zip](http://www2.census.gov/programs-surveys/acs/data/pums/2013/5-Year/csv_pdc.zip) (5&nbsp;MB compressed, 30&nbsp;MB decompressed)
        * Housing records: [csv_hdc.zip](http://www2.census.gov/programs-surveys/acs/data/pums/2013/5-Year/csv_hdc.zip) (2&nbsp;MB compressed, 13&nbsp;MB decompressed)
    * 2013 5-year PUMS estimates for user verification: [pums_estimates_9_13.csv](http://www2.census.gov/programs-surveys/acs/tech_docs/pums/estimates/pums_estimates_9_13.csv) (<1&nbsp;MB)
* Load the files:
    * Data dictionary TXT: `dsdemos.census.parse_pumsdatadict` (see `dsdemos` package <a href="#source">below</a>)  
    This is a customized parser I wrote for `PUMS_Data_Dictionary_2009-2013.txt`. The data dictionary is inconsistently formatted, which complicates parsing.[^so-post] [^json]
    * Person/housing records and user verification CSVs: `pandas.read_csv` [^pd-csv] [^pd-py35]
* Confirm the user verification estimates (see example <a href="#example">below</a>):[^pums-acc]
    * To calculate an estimate $X$ for a specific "characteristic" (e.g. "Age 25-34"), sum the column `'[P]WGTP'` of the filtered data (`'PWGTP'` for person records, `'WGTP'` for housing records).[^filter] `'[P]WGTP'` are the sample weights.
    * To calculate the estimate's "direct standard error", use the ACS's modified root-mean-square deviation:  
    $$\mathrm{SE}(X) = \sqrt{\frac{4}{80}\sum_{r=1}^{80}(X_r-X)^2}$$  
    where each $X_r$ is the sum of the column `'[P]WGTPr'` of the filtered data. `'[P]WGTP[1-80]'` are the "replicate weights".
    * To calculate the estimate's margin of error (defined by ACS at the 90% confidence level):  
    $$\mathrm{MOE}(X) = 1.645\,\mathrm{SE}(X)$$

<span id="source">**Source code:**</span>

* For step-by-step, see the Jupyter Notebook (click the HTML export to render in-browser):  
[20160110-etl-census-with-python.ipynb]({filename}/static/20160110-etl-census-with-python/20160110-etl-census-with-python.ipynb)  
[20160110-etl-census-with-python-full.html]({filename}/static/20160110-etl-census-with-python/20160110-etl-census-with-python-full.html)
* This post uses `dsdemos` [v0.0.3](https://github.com/stharrold/dsdemos/releases/tag/v0.0.3).[^version]

## Motivations

**Why am I using the American Community Survey (ACS)?**

* The ACS is a relevant data set. A future step is to predict an individual's household income, which is among the [subjects that the ACS survey addresses](http://www.census.gov/programs-surveys/acs/guidance/subjects.html).
* The ACS is a reliable data set.[^acs-method] The ACS has quality controls to ensure that it is representative. The survey samples about [3&nbsp;million addresses per year](https://www.census.gov/acs/www/methodology/sample-size-and-data-quality/sample-size/) with a [response rate of about 97%](https://www.census.gov/acs/www/methodology/sample-size-and-data-quality/response-rates/).
* The ACS is a time-series data set. The survey sends questionnaires throughout the year and [releases data once per year](https://www.census.gov/programs-surveys/acs/news/data-releases.html). A future step is to use the time series to forecast an individual's household income.
* I recognize that using ACS data can be <span id="problematic">problematic</span>. Data from the Census Bureau has been used for harm,[^data-harm] and current ACS terminology asks respondents to identify by terms such as "race".[^prob-race] For this project, I take data from the Census Bureau at face value, and I infer from it at face value. It's important to respect that these aren't simply data points; these are people.

**Why am I using the ACS 5-year estimate?**

As of Dec 2015, the ACS offers two windowing options for their data releases, 1-year estimates and 5-year estimates.[^acs-ests] Because the ACS 5-year estimates include data over a 5-year window, they have the largest sample size and thus the highest precision for modeling small populations. However, the sample size comes at the expense of currency. Forecasting the predictions from a 5-year window to be relevant to a specific year is a future step.

**Why am I using Python?**

This project can be done using Python, R, SQL, and/or other languages.[^rvpy] I'm using Python since a future step is to make a machine learning pipeline, which is a popular application of [scikit-learn](http://scikit-learn.org/).

**What about "big data"?**

I'm starting with a data set small enough to be processed in memory (i.e. operated on in RAM), since the focus of many Python packages is in-memory operations on single machines.[^pydata] These packages often parallelize operations across the machine's processor cores. For operations that exceed the machine's available RAM (i.e. out-of-core computations), there's [Dask](http://dask.pydata.org/en/latest/) for Python, and for operations that require a cluster of machines, there's [Spark](http://spark.apache.org/) for Java, Scala, Python, and R. Scaling a pipeline to a large enough data set that requires a cluster is a future step.

<!--
Note: The "Example" header will be rendered with `id="example"`.
  Creating an additional `id="example"` will break the reference.
  `href="#example"` will automatically link to this header.
-->
## Example

This is an abbreviated example of my ETL procedure in the Jupyter Notebook (see links to source code <a href="#source">above</a>).

<!-- 
Copy-pasted from
    /static/20160110-etl-census-with-python/example-basic.html
TODO: Add exported notebook by embedding HTML rather than copy-paste.
    https://github.com/stharrold/stharrold.github.io/issues/5
-->

<!--
BEGIN IPYNB
-->


<div class="cell border-box-sizing code_cell rendered">
<div class="input">
<div class="prompt input_prompt">In&nbsp;[1]:</div>
<div class="inner_cell">
    <div class="input_area">
<div class=" highlight hl-ipython3"><pre><span class="n">cd</span> <span class="o">~</span>
</pre></div>

</div>
</div>
</div>

<div class="output_wrapper">
<div class="output">


<div class="output_area"><div class="prompt"></div>
<div class="output_subarea output_stream output_stdout output_text">
<pre>/home/samuel_harrold
</pre>
</div>
</div>

</div>
</div>

</div>
<div class="cell border-box-sizing code_cell rendered">
<div class="input">
<div class="prompt input_prompt">In&nbsp;[2]:</div>
<div class="inner_cell">
    <div class="input_area">
<div class=" highlight hl-ipython3"><pre><span class="c"># Import standard packages.</span>
<span class="kn">import</span> <span class="nn">os</span>
<span class="kn">import</span> <span class="nn">subprocess</span>
<span class="kn">import</span> <span class="nn">sys</span>
<span class="c"># Import installed packages.</span>
<span class="kn">import</span> <span class="nn">numpy</span> <span class="k">as</span> <span class="nn">np</span>
<span class="kn">import</span> <span class="nn">pandas</span> <span class="k">as</span> <span class="nn">pd</span>
<span class="c"># Import local packages.</span>
<span class="c"># Insert current directory into module search path.</span>
<span class="c"># `dsdemos` version: https://github.com/stharrold/dsdemos/releases/tag/v0.0.3</span>
<span class="n">sys</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">curdir</span><span class="p">,</span> <span class="s">r&#39;dsdemos&#39;</span><span class="p">))</span>
<span class="kn">import</span> <span class="nn">dsdemos</span> <span class="k">as</span> <span class="nn">dsd</span>
</pre></div>

</div>
</div>
</div>

</div>
<div class="cell border-box-sizing code_cell rendered">
<div class="input">
<div class="prompt input_prompt">In&nbsp;[3]:</div>
<div class="inner_cell">
    <div class="input_area">
<div class=" highlight hl-ipython3"><pre><span class="c"># File paths</span>
<span class="n">path_static</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">expanduser</span><span class="p">(</span><span class="s">r&#39;~&#39;</span><span class="p">),</span> <span class="s">r&#39;stharrold.github.io/content/static&#39;</span><span class="p">)</span>
<span class="n">basename</span> <span class="o">=</span> <span class="s">r&#39;20160110-etl-census-with-python&#39;</span>
<span class="n">filename</span> <span class="o">=</span> <span class="s">r&#39;example&#39;</span>
<span class="n">path_ipynb</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">path_static</span><span class="p">,</span> <span class="n">basename</span><span class="p">,</span> <span class="n">filename</span><span class="o">+</span><span class="s">&#39;.ipynb&#39;</span><span class="p">)</span>
<span class="n">path_acs</span> <span class="o">=</span> <span class="s">r&#39;/mnt/disk-20151227t211000z/www2-census-gov/programs-surveys/acs/&#39;</span>
<span class="c"># 2013 5-year PUMS data dictionary</span>
<span class="c"># http://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2009-2013.txt</span>
<span class="n">path_dtxt</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">path_acs</span><span class="p">,</span> <span class="s">r&#39;tech_docs/pums/data_dict/PUMS_Data_Dictionary_2009-2013.txt&#39;</span><span class="p">)</span>
<span class="c"># 2013 5-year PUMS housing records for Washington DC (extracted from csv_pdc.zip)</span>
<span class="c"># http://www2.census.gov/programs-surveys/acs/data/pums/2013/5-Year/csv_pdc.zip</span>
<span class="n">path_hcsv</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">path_acs</span><span class="p">,</span> <span class="s">r&#39;data/pums/2013/5-Year/ss13hdc.csv&#39;</span><span class="p">)</span>
<span class="c"># 2013 5-year PUMS user verification estimates</span>
<span class="c"># http://www2.census.gov/programs-surveys/acs/tech_docs/pums/estimates/pums_estimates_9_13.csv</span>
<span class="n">path_ecsv</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">path_acs</span><span class="p">,</span> <span class="s">r&#39;tech_docs/pums/estimates/pums_estimates_9_13.csv&#39;</span><span class="p">)</span>
</pre></div>

</div>
</div>
</div>

</div>
<div class="cell border-box-sizing code_cell rendered">
<div class="input">
<div class="prompt input_prompt">In&nbsp;[4]:</div>
<div class="inner_cell">
    <div class="input_area">
<div class=" highlight hl-ipython3"><pre><span class="c"># Load and display the data dictionary.</span>
<span class="n">ddict</span> <span class="o">=</span> <span class="n">dsd</span><span class="o">.</span><span class="n">census</span><span class="o">.</span><span class="n">parse_pumsdatadict</span><span class="p">(</span><span class="n">path</span><span class="o">=</span><span class="n">path_dtxt</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;`ddict`, `dfd`: Convert the nested `dict` into a hierarchical data frame.&quot;</span><span class="p">)</span>
<span class="n">tmp</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span> <span class="c"># `tmp` is a throwaway variable</span>
<span class="k">for</span> <span class="n">record_type</span> <span class="ow">in</span> <span class="n">ddict</span><span class="p">[</span><span class="s">&#39;record_types&#39;</span><span class="p">]:</span>
    <span class="n">tmp</span><span class="p">[</span><span class="n">record_type</span><span class="p">]</span> <span class="o">=</span> <span class="n">pd</span><span class="o">.</span><span class="n">DataFrame</span><span class="o">.</span><span class="n">from_dict</span><span class="p">(</span><span class="n">ddict</span><span class="p">[</span><span class="s">&#39;record_types&#39;</span><span class="p">][</span><span class="n">record_type</span><span class="p">],</span> <span class="n">orient</span><span class="o">=</span><span class="s">&#39;index&#39;</span><span class="p">)</span>
<span class="n">dfd</span> <span class="o">=</span> <span class="n">pd</span><span class="o">.</span><span class="n">concat</span><span class="p">(</span><span class="n">tmp</span><span class="p">,</span> <span class="n">names</span><span class="o">=</span><span class="p">[</span><span class="s">&#39;record_type&#39;</span><span class="p">,</span> <span class="s">&#39;var_name&#39;</span><span class="p">])</span>
<span class="n">dfd</span><span class="o">.</span><span class="n">head</span><span class="p">()</span>
</pre></div>

</div>
</div>
</div>

<div class="output_wrapper">
<div class="output">


<div class="output_area"><div class="prompt"></div>
<div class="output_subarea output_stream output_stdout output_text">
<pre>&#96;ddict&#96;, &#96;dfd&#96;: Convert the nested &#96;dict&#96; into a hierarchical data frame.
</pre>
</div>
</div>

<div class="output_area"><div class="prompt output_prompt">Out[4]:</div>

<div class="output_html rendered_html output_subarea output_execute_result">
<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>length</th>
      <th>description</th>
      <th>var_codes</th>
      <th>notes</th>
    </tr>
    <tr>
      <th>record_type</th>
      <th>var_name</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">HOUSING RECORD</th>
      <th>ACR</th>
      <td>1</td>
      <td>Lot size</td>
      <td>{'b': 'N/A (GQ/not a one-family house or mobil...</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>ADJHSG</th>
      <td>7</td>
      <td>Adjustment factor for housing dollar amounts (...</td>
      <td>{'1086032': '2009 factor', '1068395': '2010 fa...</td>
      <td>[Note: The values of ADJHSG inflation-adjusts ...</td>
    </tr>
    <tr>
      <th>ADJINC</th>
      <td>7</td>
      <td>Adjustment factor for income and earnings doll...</td>
      <td>{'1085467': '2009 factor (0.999480 * 1.0860317...</td>
      <td>[Note: The values of ADJINC inflation-adjusts ...</td>
    </tr>
    <tr>
      <th>AGS</th>
      <td>1</td>
      <td>Sales of Agriculture Products (Yearly sales)</td>
      <td>{'b': 'N/A (GQ/vacant/not a one-family house o...</td>
      <td>[Note: No adjustment factor is applied to AGS.]</td>
    </tr>
    <tr>
      <th>BATH</th>
      <td>1</td>
      <td>Bathtub or shower</td>
      <td>{'b': 'N/A (GQ)', '1': 'Yes', '2': 'No'}</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>
</div>

</div>

</div>
</div>

</div>
<div class="cell border-box-sizing code_cell rendered">
<div class="input">
<div class="prompt input_prompt">In&nbsp;[5]:</div>
<div class="inner_cell">
    <div class="input_area">
<div class=" highlight hl-ipython3"><pre><span class="c"># Load and display the housing records.</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;`dfh`: First 5 housing records and first 10 columns.&quot;</span><span class="p">)</span>
<span class="n">dfh</span> <span class="o">=</span> <span class="n">pd</span><span class="o">.</span><span class="n">read_csv</span><span class="p">(</span><span class="n">path_hcsv</span><span class="p">)</span>
<span class="n">dfh</span><span class="o">.</span><span class="n">iloc</span><span class="p">[:,</span> <span class="p">:</span><span class="mi">10</span><span class="p">]</span><span class="o">.</span><span class="n">head</span><span class="p">()</span>
</pre></div>

</div>
</div>
</div>

<div class="output_wrapper">
<div class="output">


<div class="output_area"><div class="prompt"></div>
<div class="output_subarea output_stream output_stdout output_text">
<pre>&#96;dfh&#96;: First 5 housing records and first 10 columns.
</pre>
</div>
</div>

<div class="output_area"><div class="prompt output_prompt">Out[5]:</div>

<div class="output_html rendered_html output_subarea output_execute_result">
<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>insp</th>
      <th>RT</th>
      <th>SERIALNO</th>
      <th>DIVISION</th>
      <th>PUMA00</th>
      <th>PUMA10</th>
      <th>REGION</th>
      <th>ST</th>
      <th>ADJHSG</th>
      <th>ADJINC</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>600</td>
      <td>H</td>
      <td>2009000000403</td>
      <td>5</td>
      <td>102</td>
      <td>-9</td>
      <td>3</td>
      <td>11</td>
      <td>1086032</td>
      <td>1085467</td>
    </tr>
    <tr>
      <th>1</th>
      <td>NaN</td>
      <td>H</td>
      <td>2009000001113</td>
      <td>5</td>
      <td>103</td>
      <td>-9</td>
      <td>3</td>
      <td>11</td>
      <td>1086032</td>
      <td>1085467</td>
    </tr>
    <tr>
      <th>2</th>
      <td>480</td>
      <td>H</td>
      <td>2009000001978</td>
      <td>5</td>
      <td>103</td>
      <td>-9</td>
      <td>3</td>
      <td>11</td>
      <td>1086032</td>
      <td>1085467</td>
    </tr>
    <tr>
      <th>3</th>
      <td>NaN</td>
      <td>H</td>
      <td>2009000002250</td>
      <td>5</td>
      <td>105</td>
      <td>-9</td>
      <td>3</td>
      <td>11</td>
      <td>1086032</td>
      <td>1085467</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2500</td>
      <td>H</td>
      <td>2009000002985</td>
      <td>5</td>
      <td>101</td>
      <td>-9</td>
      <td>3</td>
      <td>11</td>
      <td>1086032</td>
      <td>1085467</td>
    </tr>
  </tbody>
</table>
</div>
</div>

</div>

</div>
</div>

</div>
<div class="cell border-box-sizing code_cell rendered">
<div class="input">
<div class="prompt input_prompt">In&nbsp;[6]:</div>
<div class="inner_cell">
    <div class="input_area">
<div class=" highlight hl-ipython3"><pre><span class="c"># Load and display the verification estimates.</span>
<span class="c"># Select the estimates for Washington DC then for the</span>
<span class="c"># characteristic &#39;Owner occupied units (TEN in 1,2)&#39;.</span>
<span class="n">dfe</span> <span class="o">=</span> <span class="n">pd</span><span class="o">.</span><span class="n">read_csv</span><span class="p">(</span><span class="n">path_ecsv</span><span class="p">)</span>
<span class="n">tfmask_dc</span> <span class="o">=</span> <span class="n">dfe</span><span class="p">[</span><span class="s">&#39;state&#39;</span><span class="p">]</span> <span class="o">==</span> <span class="s">&#39;District of Columbia&#39;</span>
<span class="n">dfe_dc</span> <span class="o">=</span> <span class="n">dfe</span><span class="o">.</span><span class="n">loc</span><span class="p">[</span><span class="n">tfmask_dc</span><span class="p">]</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;`dfe_dc`: This example verifies these quantities.&quot;</span><span class="p">)</span>
<span class="n">dfe_dc</span><span class="o">.</span><span class="n">loc</span><span class="p">[[</span><span class="mi">310</span><span class="p">]]</span>
</pre></div>

</div>
</div>
</div>

<div class="output_wrapper">
<div class="output">


<div class="output_area"><div class="prompt"></div>
<div class="output_subarea output_stream output_stdout output_text">
<pre>&#96;dfe_dc&#96;: This example verifies these quantities.
</pre>
</div>
</div>

<div class="output_area"><div class="prompt output_prompt">Out[6]:</div>

<div class="output_html rendered_html output_subarea output_execute_result">
<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>st</th>
      <th>state</th>
      <th>characteristic</th>
      <th>pums_est_09_to_13</th>
      <th>pums_se_09_to_13</th>
      <th>pums_moe_09_to_13</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>310</th>
      <td>11</td>
      <td>District of Columbia</td>
      <td>Owner occupied units (TEN in 1,2)</td>
      <td>110,362</td>
      <td>1363</td>
      <td>2242</td>
    </tr>
  </tbody>
</table>
</div>
</div>

</div>

</div>
</div>

</div>
<div class="cell border-box-sizing code_cell rendered">
<div class="input">
<div class="prompt input_prompt">In&nbsp;[7]:</div>
<div class="inner_cell">
    <div class="input_area">
<div class=" highlight hl-ipython3"><pre><span class="c"># Verify the estimates following</span>
<span class="c"># https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.2013.html</span>
<span class="c"># http://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2009_2013AccuracyPUMS.pdf</span>
<span class="c"># Define the column names for the housing weights.</span>
<span class="n">hwt</span> <span class="o">=</span> <span class="s">&#39;WGTP&#39;</span>
<span class="n">hwts</span> <span class="o">=</span> <span class="p">[</span><span class="n">hwt</span><span class="o">+</span><span class="nb">str</span><span class="p">(</span><span class="n">inum</span><span class="p">)</span> <span class="k">for</span> <span class="n">inum</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="mi">1</span><span class="p">,</span> <span class="mi">81</span><span class="p">)]</span> <span class="c"># [&#39;WGTP1&#39;, ..., &#39;WGTP80&#39;]</span>
<span class="c"># Select the reference verification data for the characteristic.</span>
<span class="n">char</span> <span class="o">=</span> <span class="s">&#39;Owner occupied units (TEN in 1,2)&#39;</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;&#39;{char}&#39;&quot;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">char</span><span class="o">=</span><span class="n">char</span><span class="p">))</span>
<span class="n">tfmask_ref</span> <span class="o">=</span> <span class="n">dfe_dc</span><span class="p">[</span><span class="s">&#39;characteristic&#39;</span><span class="p">]</span> <span class="o">==</span> <span class="n">char</span>
<span class="c"># Select the records for the characteristic.</span>
<span class="n">tfmask_test</span> <span class="o">=</span> <span class="n">np</span><span class="o">.</span><span class="n">logical_or</span><span class="p">(</span><span class="n">dfh</span><span class="p">[</span><span class="s">&#39;TEN&#39;</span><span class="p">]</span> <span class="o">==</span> <span class="mi">1</span><span class="p">,</span> <span class="n">dfh</span><span class="p">[</span><span class="s">&#39;TEN&#39;</span><span class="p">]</span> <span class="o">==</span> <span class="mi">2</span><span class="p">)</span>
<span class="c"># Calculate the estimate (&#39;est&#39;) for the characteristic.</span>
<span class="c"># The estimate is the sum of the sample weights &#39;WGTP&#39;.</span>
<span class="n">col</span> <span class="o">=</span> <span class="s">&#39;pums_est_09_to_13&#39;</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;    &#39;{col}&#39;:&quot;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">col</span><span class="o">=</span><span class="n">col</span><span class="p">),</span> <span class="n">end</span><span class="o">=</span><span class="s">&#39; &#39;</span><span class="p">)</span>
<span class="n">ref_est</span> <span class="o">=</span> <span class="nb">int</span><span class="p">(</span><span class="n">dfe_dc</span><span class="o">.</span><span class="n">loc</span><span class="p">[</span><span class="n">tfmask_ref</span><span class="p">,</span> <span class="n">col</span><span class="p">]</span><span class="o">.</span><span class="n">values</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span><span class="o">.</span><span class="n">replace</span><span class="p">(</span><span class="s">&#39;,&#39;</span><span class="p">,</span> <span class="s">&#39;&#39;</span><span class="p">))</span>
<span class="n">test_est</span> <span class="o">=</span> <span class="n">dfh</span><span class="o">.</span><span class="n">loc</span><span class="p">[</span><span class="n">tfmask_test</span><span class="p">,</span> <span class="n">hwt</span><span class="p">]</span><span class="o">.</span><span class="n">sum</span><span class="p">()</span>
<span class="k">assert</span> <span class="n">np</span><span class="o">.</span><span class="n">isclose</span><span class="p">(</span><span class="n">ref_est</span><span class="p">,</span> <span class="n">test_est</span><span class="p">,</span> <span class="n">rtol</span><span class="o">=</span><span class="mi">0</span><span class="p">,</span> <span class="n">atol</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;(ref, test) = {tup}&quot;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">tup</span><span class="o">=</span><span class="p">(</span><span class="n">ref_est</span><span class="p">,</span> <span class="n">test_est</span><span class="p">)))</span>
<span class="c"># Calculate the &quot;direct standard error&quot; (&#39;se&#39;) of the estimate.</span>
<span class="c"># The direct standard error is a modified root-mean-square deviation</span>
<span class="c"># using the &quot;replicate weights&quot; &#39;WGTP[1-80]&#39;.</span>
<span class="n">col</span> <span class="o">=</span> <span class="s">&#39;pums_se_09_to_13&#39;</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;    &#39;{col}&#39; :&quot;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">col</span><span class="o">=</span><span class="n">col</span><span class="p">),</span> <span class="n">end</span><span class="o">=</span><span class="s">&#39; &#39;</span><span class="p">)</span>
<span class="n">ref_se</span> <span class="o">=</span> <span class="n">dfe_dc</span><span class="o">.</span><span class="n">loc</span><span class="p">[</span><span class="n">tfmask_ref</span><span class="p">,</span> <span class="n">col</span><span class="p">]</span><span class="o">.</span><span class="n">values</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span>
<span class="n">test_se</span> <span class="o">=</span> <span class="p">((</span><span class="mi">4</span><span class="o">/</span><span class="mi">80</span><span class="p">)</span><span class="o">*</span><span class="p">((</span><span class="n">dfh</span><span class="o">.</span><span class="n">loc</span><span class="p">[</span><span class="n">tfmask_test</span><span class="p">,</span> <span class="n">hwts</span><span class="p">]</span><span class="o">.</span><span class="n">sum</span><span class="p">()</span> <span class="o">-</span> <span class="n">test_est</span><span class="p">)</span><span class="o">**</span><span class="mi">2</span><span class="p">)</span><span class="o">.</span><span class="n">sum</span><span class="p">())</span><span class="o">**</span><span class="mf">0.5</span>
<span class="k">assert</span> <span class="n">np</span><span class="o">.</span><span class="n">isclose</span><span class="p">(</span><span class="n">ref_se</span><span class="p">,</span> <span class="n">test_se</span><span class="p">,</span> <span class="n">rtol</span><span class="o">=</span><span class="mi">0</span><span class="p">,</span> <span class="n">atol</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;(ref, test) = {tup}&quot;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">tup</span><span class="o">=</span><span class="p">(</span><span class="n">ref_se</span><span class="p">,</span> <span class="n">test_se</span><span class="p">)))</span>
<span class="c"># Calculate the margin of error (&#39;moe&#39;) at the 90% confidence level</span>
<span class="c"># (+/- 1.645 standard errors).</span>
<span class="n">col</span> <span class="o">=</span> <span class="s">&#39;pums_moe_09_to_13&#39;</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;    &#39;{col}&#39;:&quot;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">col</span><span class="o">=</span><span class="n">col</span><span class="p">),</span> <span class="n">end</span><span class="o">=</span><span class="s">&#39; &#39;</span><span class="p">)</span>
<span class="n">ref_moe</span> <span class="o">=</span> <span class="n">dfe_dc</span><span class="o">.</span><span class="n">loc</span><span class="p">[</span><span class="n">tfmask_ref</span><span class="p">,</span> <span class="n">col</span><span class="p">]</span><span class="o">.</span><span class="n">values</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span>
<span class="n">test_moe</span> <span class="o">=</span> <span class="mf">1.645</span><span class="o">*</span><span class="n">test_se</span>
<span class="k">assert</span> <span class="n">np</span><span class="o">.</span><span class="n">isclose</span><span class="p">(</span><span class="n">ref_moe</span><span class="p">,</span> <span class="n">test_moe</span><span class="p">,</span> <span class="n">rtol</span><span class="o">=</span><span class="mi">0</span><span class="p">,</span> <span class="n">atol</span><span class="o">=</span><span class="mi">1</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="s">&quot;(ref, test) = {tup}&quot;</span><span class="o">.</span><span class="n">format</span><span class="p">(</span><span class="n">tup</span><span class="o">=</span><span class="p">(</span><span class="n">ref_moe</span><span class="p">,</span> <span class="n">test_moe</span><span class="p">)))</span>
</pre></div>

</div>
</div>
</div>

<div class="output_wrapper">
<div class="output">


<div class="output_area"><div class="prompt"></div>
<div class="output_subarea output_stream output_stdout output_text">
<pre>&apos;Owner occupied units (TEN in 1,2)&apos;
    &apos;pums_est_09_to_13&apos;: (ref, test) = (110362, 110362)
    &apos;pums_se_09_to_13&apos; : (ref, test) = (1363, 1363.1910174293257)
    &apos;pums_moe_09_to_13&apos;: (ref, test) = (2242, 2242.449223671241)
</pre>
</div>
</div>

</div>
</div>

</div>

<!--
END IPYNB
-->

## Helpful links

Some links I found helpful for this blog post:

* American Community Survey (ACS):
    * [ACS About](https://www.census.gov/programs-surveys/acs/about.html).
    * [ACS Guidance for Data Users](https://www.census.gov/programs-surveys/acs/guidance.html) describes how to get started with ACS data.
    * [ACS Technical Documentation](https://www.census.gov/programs-surveys/acs/technical-documentation.html) links to resources for learning how to work with ACS data.
    * [ACS Methodology](http://www.census.gov/programs-surveys/acs/methodology.html) includes design details, sample sizes, coverage estimates, and past questionnaires.
    * [ACS Library](https://www.census.gov/programs-surveys/acs/library.All.html) has a collection of reports and infographics using ACS data.
* Python:
    * [*Learning Python* (5th ed, 2013, O'Reilly)](http://shop.oreilly.com/product/0636920028154.do) was my formal introduction to Python.
    * [*Python for Data Analysis* (2012, O'Reilly)](http://shop.oreilly.com/product/0636920023784.do) introduced me to `pandas`.
    * [*Python Cookbook* (3rd ed, 2013, O'Reilly)](http://shop.oreilly.com/product/0636920027072.do) has a collection of optimized recipes.
    * From the well-documented [Python 3.5](https://docs.python.org/3/index.html) standard library, I used [collections](https://docs.python.org/3/library/collections.html), [functools](https://docs.python.org/3/library/functools.html), [os](https://docs.python.org/3/library/os.html), [pdb](https://docs.python.org/3/library/pdb.html), [subprocess](https://docs.python.org/3/library/subprocess.html), [sys](https://docs.python.org/3/library/sys.html), and [time](https://docs.python.org/3/library/time.html) for this post.
    * Likewise, the documentation for [numpy](http://docs.scipy.org/doc/numpy-1.10.0/reference/) and [pandas](http://pandas.pydata.org/pandas-docs/version/0.17.1/) is thorough and invaluable.
    * Of IPython's convenient ["magic" commands](http://ipython.readthedocs.org/en/stable/interactive/magics.html), within this post's Jupyter Notebooks, I used [%pdb](http://ipython.readthedocs.org/en/stable/interactive/magics.html#magic-pdb), [%reload_ext](http://ipython.readthedocs.org/en/stable/interactive/magics.html#magic-reload_ext), and the extension [%autoreload](http://ipython.readthedocs.org/en/stable/config/extensions/autoreload.html?highlight=autoreload#module-IPython.extensions.autoreload).
    * StackOverflow ["How to get line count cheaply in Python"](http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python) (compare to `wc -l`).
* `dsdemos` [v0.0.3](https://github.com/stharrold/dsdemos/tree/59705867b61b1bbc054c9ff2a5f8c6b2305ca60e):
    * To design the package file structure, I used [*Learning Python* (O'Reilly)](http://shop.oreilly.com/product/0636920028154.do) Section V, "Modules and Packages".
    * I use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html) adapted from the [example](http://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_google.html) by the [Napoleon](https://sphinxcontrib-napoleon.readthedocs.org/en/latest/) extension to [Sphinx](http://sphinx-doc.org/) (a Python documentation generator, not yet used by `dsdemos`).
    * [Pytest](http://pytest.org/latest/) for testing.
    * [Semantic Versioning](http://semver.org/) for version numbers.
* Git:
    * [GitHub Guides](https://guides.github.com/) are where I started with `git`.
    * [Git documentation](https://git-scm.com/) answers a lot of questions.
    * [Git-flow](https://github.com/nvie/gitflow) streamlines my repository management with this [branching model](http://nvie.com/posts/a-successful-git-branching-model/).
    * StackOverflow ["Download a specific tag with git"](http://stackoverflow.com/questions/791959/download-a-specific-tag-with-git).

## Footnotes
<!-- From https://pythonhosted.org/Markdown/extensions/footnotes.html -->
///Footnotes Go Here///

<!-- ## Overview -->
[^use-cases]:
    Some use cases for the Census Bureau's American Community Survey with data access recommendations: [ACS Which Data Tool](https://www.census.gov/acs/www/guidance/which-data-tool/)
[^services]:
    This project mounts a single disk for storage to a single instance and loads the data in RAM. A scaled version of this pipeline on the Google Cloud Platform may include integrated services such as [Cloud Storage](https://cloud.google.com/storage/) and [Big Query](https://cloud.google.com/bigquery/).
[^ftp]:
    For how to download [ACS data via FTP](https://www.census.gov/programs-surveys/acs/data/data-via-ftp.html):  
    `$ sudo curl --remote-name <url>`  
    Decompress the `.zip` files with `unzip`.
[^no-api]:
    I'm downloading the data files rather than using the [Census Bureau's API](http://www.census.gov/developers/) because this project requires one-time access to all data rather than dynamic access to a subset of the data.
[^so-post]:
    StackOverflow ["regex to parse well-formated multi-line data dictionary"](http://stackoverflow.com/questions/26564775/regex-to-parse-well-formated-multi-line-data-dictionary/34564141#34564141).
[^json]:
    With `dsdemos` v0.0.3 <a href="#source">above</a>, you can export the data dictionary to [JSON format](http://json.org/) with the [`json` Python library](https://docs.python.org/3.5/library/json.html). See [example from `dsdemos` tests](https://github.com/stharrold/dsdemos/blob/59705867b61b1bbc054c9ff2a5f8c6b2305ca60e/tests/test_census.py#L34-L43).
[^pd-csv]:
    [Docs for `pandas.read_csv`](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html)
[^pd-py35]:
    Pandas 0.17.1 has a compatibility issue with Python 3.5. See [GitHub pandas issue 11915](https://github.com/pydata/pandas/issues/11915) for a temporary fix. The issue should be resolved in pandas 0.18.
[^pums-acc]:
    For the formulas to calculate the estimates, the direct standard error, and the margin of error, as well as for example calculations, see [2013 5-year PUMS Accuracy](http://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2009_2013AccuracyPUMS.pdf), section 7, "Measuring Sampling Error". The sample weights `'[P]WGTP'` mitigate over/under-representation and control agreement with published ACS estimates. The accuracy PDF describes two methods of calculating the error (uncertainty) associated with an estimate of a characteristic:  
    <ol>
    <li>Calculate the "generalized standard error" of the estimate using "design factors" from the survey. This method does not use columns `'[P]WGTP[1-80]'` and requires looking up a design factor for the specific characteristic (e.g "Population by Tenure"). See the accuracy PDF for the design factors.</li>
    <li>Calculate the "direct standard error" of the estimate using the "replicate weights", which are the columns `'[P]WGTP[1-80]'`. This method is extensible to many kinds of characteristics (e.g. population by tenure by age).
    </ol>  
    Note: Controlled estimates of characteristics like "total population" have 0 direct standard error from replicate weights. Use the generalized standard error for these estimates.
[^filter]:
    There are [several ways](http://pandas.pydata.org/pandas-docs/stable/indexing.html) to select rows by filtering on conditions within `pandas`. I prefer creating a `pandas.Series` with boolean values as true-false mask then using the true-false mask as an index to filter the rows. See the [docs for `pandas.DataFrame.loc`](http://pandas.pydata.org/pandas-docs/version/0.17.1/generated/pandas.DataFrame.loc.html).  
    Example query: Select `'AGEP'` and `'WGTP'` where `'AGEP'` is between 25 and 34.  
    `tfmask = np.logical_and(25 <= df['AGEP'], df['AGEP'] <= 34)`  
    `df_subset = df.loc[tfmask, ['AGEP', 'WGTP']]`
[^version]:
    To download `dsdemos` and checkout `v0.0.3` for following the example <a href="#example">above</a>:  
    `$ cd ~`  
    `$ git clone https://github.com/stharrold/dsdemos.git`  
    `$ cd dsdemos`  
    `$ git checkout tags/v0.0.3`  
    If you already have a clone of `dsdemos`, update your local repository then checkout the new tag:  
    `$ cd dsdemos`  
    `$ git pull`  
    `$ git checkout tags/v0.0.3`
<!-- ## Motivations -->
[^acs-method]:
    [ACS Methodology](http://www.census.gov/programs-surveys/acs/methodology.html) includes design details, sample sizes, coverage estimates, and past questionnaires.
[^data-harm]:
    Data from the Census Bureau was used to identify Japanese communities as part of the internment of US citizens and residents with Japanese ancestry during World&nbsp;War&nbsp;II. See the [ACLU's FAQ section about census data](https://www.aclu.org/frequently-asked-questions-national-census) and the [Wikipedia article "Internment of Japanese Americans"](https://en.wikipedia.org/wiki/Internment_of_Japanese_Americans).
[^prob-race]:
    "Race" is a problematic term with historical connotations and conflicts between self-identification and labeling by others. The [2015 ACS questionnaire](http://www2.census.gov/programs-surveys/acs/methodology/questionnaires/2015/quest15.pdf) refers to "race" and "ethnicity" separately. The American Anthropological Association [recommended in 1997](http://s3.amazonaws.com/rdcms-aaa/files/production/public/FileDownloads/pdfs/cmtes/minority/upload/AAA_Response_OMB1997.pdf) that questions about "race" and "ethnicity" are ambiguous given the historical context and would be better phrased as about "race/ethnicity". For this project, I refer to "race" and "ethnicity" as "race/ethnicity". The following links are also helpful:  
    <ul>
    <li>[Census Bureau's statement about "race" (2013)](http://www.census.gov/topics/population/race/about.html)</li>
    <li>[Office of Management and Budget, "Standards for the Classification of Federal Data on Race and Ethnicity" (1994), Appendix Directive No.&nbsp;15 (1977)](https://www.whitehouse.gov/omb/fedreg_notice_15/)</li>
    <li>[Office of Management and Budget, "Review of the Racial and Ethnic Standards to the OMB Concerning Changes" (Jul&nbsp;1997)](https://www.whitehouse.gov/omb/fedreg_directive_15)</li>
    <li>[Office of Management and Budget, "Revisions to the Standards for the Classification of Federal Data on Race and Ethnicity" (Oct&nbsp;1997)](https://www.whitehouse.gov/omb/fedreg_1997standards)</li>
    <li>[American Anthropological Association, "Statement on Race" (1998)](http://www.americananthro.org/ConnectWithAAA/Content.aspx?ItemNumber=2583)</li>
    <li>[Wikipedia article "Race and ethnicity in the United States Census"](https://en.wikipedia.org/wiki/Race_and_ethnicity_in_the_United_States_Census)</li>
    </ul>
[^acs-ests]:
    The ACS 3-year estimates are discontinued; 2013 is the last year included in the 3-year estimates. For guidance in choosing, accessing, and using a data set, see [ACS Guidance for Data Users](https://www.census.gov/programs-surveys/acs/guidance.html).
[^rvpy]:
    StackExchange Programmers ["R vs Python for data analysis"](http://programmers.stackexchange.com/questions/181342/r-vs-python-for-data-analysis).
[^pydata]:
    See the [PyData stack](http://pydata.org/downloads/) for a collection of performant Python packages.
