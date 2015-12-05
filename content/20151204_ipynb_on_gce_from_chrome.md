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

In October 2015, I bought a Chromebook with the intent of moving my data-science development workflow to the cloud. The workflow that I've settled on so far is TODO.   

Some links I found helpful:  
    * IPython Notebooks:  
        * [Running an IPython Notebook from Amazon Web Services](https://gist.github.com/iamatypeofwalrus/5183133)  
        * [Hosting a password-protected IPython Notebook from Google Compute Engine](https://gist.github.com/samklr/07bee2868a6ed72a8ec4)  
    * Chrome:
        * [Chromebook 2GB vs 4GB Demo](https://www.youtube.com/watch?v=y1dAnXkednM)
        * [Using a Chromebook as a developer](http://jjg.svbtle.com/)
        * [Export cookies from Chrome for wget](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg)  
        * [SFTP from a Chromebook](https://chrome.google.com/webstore/detail/sftp-file-system/gbheifiifcfekkamhepkeogobihicgmn)
        * [`chrome://system` to inspect system resources](chrome://system)
        * [`chrome://memory-redirect` to inspect RAM usage by Chrome](chrome://memory-redirect)
        * [Chrome Caret for editing](https://chrome.google.com/webstore/detail/caret/fljalecfjciodhpcledpamjachpmelml)
        * [Chrome Secure Shell](https://chrome.google.com/webstore/detail/secure-shell/pnhechapfaindjhompbnflcldabbghjo)
    * Linux:  
        * [SSH login without password](http://www.linuxproblem.org/art_9.html)  
        * [SSH port forwarding (tunnels) explained](http://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html)  
        * [wget download from Google Drive](http://unix.stackexchange.com/questions/136371/how-to-download-a-folder-from-google-drive-using-terminal)  
        * [wget download from Kaggle](https://www.kaggle.com/forums/f/15/kaggle-forum/t/6604/downloading-data-via-command-line)  
        * [Choosing between Debian and Ubuntu](http://www.datamation.com/open-source/debian-vs-ubuntu-which-is-best-for-you-1.html)  
        * [`disown PID` to keep a job running after closing the shell](http://www.cyberciti.biz/faq/unix-linux-disown-command-examples-usage-syntax/)
        * `lsof -i:PORT` to find active processes
        * `free -m` displays the free memory (RAM) in MB.
        * `df -B MB` displays the free disk space in MB.
        * [What `sudo apt-get update` does](http://askubuntu.com/questions/222348/what-does-sudo-apt-get-update-do)
        

## Motivation

TODO: cheap, replacable, demo from most limiting netbook



Adds a bit of extra setup, but leverages powerful infrastructure.

I had to upgrade from a 2GB RAM Chromebook since I typically use about 2.5GB RAM while working.

I need to test the scalability of my workflows, and for me it's most convenient to use virtual machines directly. If this isn't your use case, hosted services like [Continuum Analytics Wakari](https://wakari.io/), [Cloud9 hosted workspaces](https://c9.io/?redirect=0), and [Digital Ocean](https://www.digitalocean.com/) are worth considering.

## Setup

There are many ways to run an IPython Notebook on a virtual machine. This is just my setup:

* I'm using an [ASUS C201 Chromebook with 4GB RAM](http://www.amazon.com/gp/product/B00VUV0MG0).
* Create the Google Compute Engine virtual machine instance and SSH keys:
    * Make a project in the [Google Developers Console](https://console.developers.google.com).
    * Configure an instance:
        * Machine type: I start with the smallest and move to larger instances as the work load requires. TODO: memory command  
        * Boot disk: I start with the default boot disk (Debian) and increase size as I need storage. TODO: storage command
        * Firewall: Allow HTTP and HTTPS connections to use `curl` and `wget`.
        * Project access: Reserve an external IP address ("Networking > External IP"). Other settings can be left at default for this example. For the rest of this example, I give my intance's static external IP address as `123.123.123.123`.[^1]  
    * Connect to the instance, e.g. with Google's in-browser SSH.
    * [Update the Debian system.](http://askubuntu.com/questions/222348/what-does-sudo-apt-get-update-do)
    * [Generate SSH keys](https://help.github.com/articles/generating-ssh-keys/) and might as well connect to GitHub.[^2]  

[^1]: Reassigning a static external IP address to a new instance when changing machine types is often easier than changing an ephemeral IP address in all connections to the instance, i.e. in Cloud9 and Chrome Secure Shell.

[^2]: For Google's in-browser SSH, use `less` rather than `xclip` to copy the public key.

* Connect the Cloud9 IDE to the instance: 
    * [Install Node.js](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions) on the instance.
    * Create a [Cloud9 remote SSH workspace](https://docs.c9.io/docs/running-your-own-ssh-workspace), copy the public SSH key from Cloud9 to the instance's `authorized_keys`, then open the workspace.[^3][^4]

[^3]:
    My Cloud9 remote SSH settings:  
    `Username: samuel_harrold` (in the instance shell, run `whoami`)  
    `Hostname: 123.123.123.123` (the instance's external IP address)  
    `Initial path: /home/samuel_harrold`  
    `Port: 22`  
    `Node.js binary path: /usr/bin/nodejs` (in the instance shell, run `which nodejs`)  
    To copy the public SSH key from Cloud9 to the instance's `authorized_keys`, in the instance shell, run:  
    `$ cat >> ~/authorized_keys/.ssh`  
    `[Ctrl+V to paste the key, then Enter]`  
    `[Ctrl+D to signal end of file]`  
[^4]:
    If the Cloud9 workspace fails to connect to the instance, i.e. the terminal within the workspace doesn't receive input, run the Cloud9 [installation script](https://github.com/c9/install/) (requires HTTPS traffic allowed in the instance firewall settings):  
    `$ wget -O - https://raw.githubusercontent.com/c9/install/master/install.sh | bash`
* Start a Jupyter (IPython) Notebook server on the instance:
    * [Install Python](https://www.continuum.io/downloads) on the instance.[^5]
    * 

[^5]: I prefer the Continuum Analytics Anaconda Python distribution for its [Conda package manager](http://conda.pydata.org/docs/). 

* To upgrade the vm instance
===

Google Compute Engine settings: f1-micro, debian, only port forward - no http, snapshots as backups, fixed external ip

Cloud9 and DigitalOcean hosted VM instances were too small (Cloud9 offers up to 2.5 GB RAM, 1 core; DigitalOcean up to 8GB RAM, 4 core). I now use Cloud9 for its fancy IDE, but only as a SSH workspace. I use Google Compute Engine as my VM instance. I port forward from the VM instance to my Chromebook to run jupyter notebook using the app "Secure Shell" (screenshot attached with options). I used the VM instance to create the id_rsa key pair for my Chromebook.

copy-paste tool for key-pairs

## Why __?

### IPython Notebooks

[IPython (Jupyter) Notebooks](http://ipython.org/notebook.html) enable me to
develop quickly and to share my work in-progress. The notebook serves as a top-level script, the parts of which I eventually modularize as components of installable packages.

### Chromebook

low-profile flash drive: http://www.amazon.com/gp/product/B00LLER2CS

large cheap monitor with hdmi input

so far avoided needing chrome os's dev mode. using now for 2 months.

### Cloud

It's useful to have a reproducible environment that can scale with the problem.

### Google Compute Engine

Between Google Cloud and Amazon Web Services, I chose Google Cloud due to its intuitive UI. SSH within the browser is amazing.

I chose [Google Compute Engine](https://cloud.google.com/compute/) over 



### Environment

I use the [Anaconda Python distribution](https://www.continuum.io/downloads) for the `conda` package manager.

### Cloud9

TODO: cloud9, and instructions for connecting, need to provide public key

[Cloud9](https://c9.io/?redirect=0) insta, digitalocean instances too small

I don't use cloud9 for debugging. I use [pdb](https://docs.python.org/3.5/library/pdb.html) for debugging and [pytest](http://pytest.org/latest/) for testing. I use the IDE mostly for code navigation, autocomplete, and managing packages with many files


### SSH port forwarding

TODO

### Daily usage

1. Start the Google Compute Engine VM instance under
project: "stharrold-sandbox", instance: "instance-20151028t103000".
Check that the IP address matches as the host for Secure Shell and Cloud9.
2. Start jupyter notebook in the Google secure shell:
$ lsof -i:8889
$ jupyter notebook --ip=0.0.0.0 --port=8889 --no-browser &
$ disown 800 # where 800 is the process ID (pid)
3. Forward the port of the jupyter notebook to the Chomebook using the app "Secure Shell":
connection: stharrold-sandbox jupyter notebook
username: samuel_harrold
hostname: 104.154.56.50
port: 22
Identity: id_rsa (both id_rsa.pub and id_rsa files were imported)
SSH Arguments: -N -L localhost:8889:0.0.0.0:8889
Note: If the remote host identification has changed, open the Javascript console
(ctrl+shift+j) and execute `term_.command.removeKnownHostByIndex(idx)` where idx
is the given line number, e.g. `Offending ECDSA key in /.ssh/known_hosts:1`.
3. Open Chrome to http://localhost:8889
4. Open the Cloud9 workspace "sandbox".
5. To shutdown sandbox, follow the setup steps in reverse.