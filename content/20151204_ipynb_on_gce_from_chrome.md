Title: Running an IPython Notebook on Google Compute Engine from a Chromebook
Status: draft
Date: 2015-12-04T23:00:00Z
Modified: 2015-12-04T23:00:00Z
Tags: devops, ipynb, gce, chrome, cloud9, ssh
Category: DevOps
Slug: 20151204_ipynb_on_gce_from_chrome
Authors: Samuel Harrold
Summary: As a data scientist, I develop from a Chromebook using IPython Notebooks, Google Compute Engine, Cloud9, and SSH port forwarding.

[TOC]

## Overview

In October 2015, I bought a Chromebook with the intent of moving my data-science development workflow to the cloud. This is the workflow that I've settled on so far:[^1]  
* TODO

<!-- TODO: format footnote -->
[^1]: Some links I found helpful:  
    * IPython Notebooks:  
        * [Running an IPython Notebook from Amazon Web Services](https://gist.github.com/iamatypeofwalrus/5183133)  
        * [Hosting a password-protected IPython Notebook from Google Compute Engine](https://gist.github.com/samklr/07bee2868a6ed72a8ec4)  
    * Chrome:  
        * [Using a Chromebook as a developer](http://jjg.svbtle.com/)  
        * [Export cookies from Chrome for wget](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg)  
        * [SFTP from a Chromebook](https://chrome.google.com/webstore/detail/sftp-file-system/gbheifiifcfekkamhepkeogobihicgmn)
        * [`chrome://system` to inspect system resources](chrome://system)
        * [`chrome://memory-redirect` to inspect RAM usage by Chrome](chrome://memory-redirect)
        * [Caret for editing](https://chrome.google.com/webstore/detail/caret/fljalecfjciodhpcledpamjachpmelml)
    * Linux:  
        * [SSH login without password](http://www.linuxproblem.org/art_9.html)  
        * [SSH port forwarding (tunnels) explained](http://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html)  
        * [wget download from Google Drive](http://unix.stackexchange.com/questions/136371/how-to-download-a-folder-from-google-drive-using-terminal)  
        * [wget download from Kaggle](https://www.kaggle.com/forums/f/15/kaggle-forum/t/6604/downloading-data-via-command-line)  
        * [Choosing between Debian and Ubuntu](http://www.datamation.com/open-source/debian-vs-ubuntu-which-is-best-for-you-1.html)  
        * [`disown PID` to keep a job running after closing the shell](http://www.cyberciti.biz/faq/unix-linux-disown-command-examples-usage-syntax/)
        * `lsof -i:PORT` to find active processes
        

## Step-by-step

Google Compute Engine settings: f1-micro, debian, only port forward - no http, snapshots as backups, fixed external ip

Cloud9 and DigitalOcean hosted VM instances were too small (Cloud9 offers up to 2.5 GB RAM, 1 core; DigitalOcean up to 8GB RAM, 4 core). I now use Cloud9 for its fancy IDE, but only as a SSH workspace. I use Google Compute Engine as my VM instance. I port forward from the VM instance to my Chromebook to run jupyter notebook using the app "Secure Shell" (screenshot attached with options). I used the VM instance to create the id_rsa key pair for my Chromebook.

copy-paste tool for key-pairs

## Why __?

### IPython Notebooks

[IPython (Jupyter) Notebooks](http://ipython.org/notebook.html) enable me to
develop quickly and to share my work in-progress. The notebook serves as a top-level script, the parts of which I eventually modularize as components of installable packages.

### Chromebook

TODO: cheap, replacable, demo from most limiting netbook

I'm using an [ASUS C201 11.6-inch Chromebook with 4GB RAM](http://www.amazon.com/gp/product/B00VUV0MG0). Because I'm using SSH port forwarding, the Chromebook is rendering the IPython Notebook. Rendering a 5MB IPython Notebook consumes
My first Chromebook had 2GB RAM, I returned

low-profile flash drive: http://www.amazon.com/gp/product/B00LLER2CS

large cheap monitor with hdmi input

so far avoided needing chrome os's dev mode. using now for 2 months.

### Cloud

It's useful to have a reproducible environment that can scale with the problem.

### Google Compute Engine

Between Google Cloud and Amazon Web Services, I chose Google Cloud due to its intuitive UI. SSH within the browser is amazing.

I chose [Google Compute Engine](https://cloud.google.com/compute/) over services like [Wakari](https://wakari.io/), [Cloud9](https://c9.io/?redirect=0), [Digital Ocean](https://www.digitalocean.com/), because I wanted to be able to scale the infrastructure to many cores.



### Environment

I use the [Anaconda Python distribution](https://www.continuum.io/downloads) for the `conda` package manager.

### Cloud9

TODO: cloud9, and instructions for connecting, need to provide public key

[Cloud9](https://c9.io/?redirect=0) insta, digitalocean instances too small

I don't use cloud9 for debugging. I use [pdb](https://docs.python.org/3.5/library/pdb.html) for debugging and [pytest](http://pytest.org/latest/) for testing. I use the IDE mostly for code navigation, autocomplete, and managing packages with many files


### SSH port forwarding

TODO
