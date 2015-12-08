Title: Running an IPython Notebook on Google Compute Engine from Chrome
Status: published
Date: 2015-12-08T03:20:00Z
Modified: 2015-12-08T03:20:00Z
Tags: devops, how_to, ipynb, gce, chrome, cloud9, ssh
Category: DevOps
Slug: 20151208_ipynb_on_gce_from_chrome
Authors: Samuel Harrold
Summary: As a data scientist, I develop from a Chromebook using IPython Notebooks, Google Compute Engine, Cloud9, and SSH port forwarding.

[TOC]

## Overview

In October 2015, I bought a Chromebook with the intent of learning how to move my data-science development environment to the cloud. In exchange for an extra 5&nbsp;minutes of setup, I now have a flexible infrastructure that can scale with the task. This setup is cross-platform in that it can be used on any laptop with Chrome, not just a Chromebook.

Brief setup routine:

<a href="/static/20151208_ipynb_on_gce_from_chrome/20151208_chrome_secure_shell_settings_821x451pix.png" type="image/jpeg">
    <img src="/static/20151208_ipynb_on_gce_from_chrome/20151208_chrome_secure_shell_settings_821x451pix.png" alt="Chrome Secure Shell settings" align="right" width="320" />
</a>

* Start a [Google Compute Engine](https://cloud.google.com/compute/) virtual machine instance.
* Start a [Jupyter Notebook](http://jupyter.org/) server on the instance:  
`$ jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser &`  
`$ disown 1234` (where `1234` is the process ID)
* Create an [SSH tunnel](http://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html) to forward a local port to the server's port on the instance:  
`$ ssh -f -N -L localhost:8888:0.0.0.0:8888 samuel_harrold@123.123.123.123`  
For [Chrome Secure Shell](https://chrome.google.com/webstore/detail/secure-shell/pnhechapfaindjhompbnflcldabbghjo), omit `-f` to keep the tunnel open (see screenshot).
* View the server at `http://localhost:8888`
* I use the [Cloud9 IDE](https://c9.io/?redirect=0) and connect the instance as an [SSH workspace](https://docs.c9.io/docs/running-your-own-ssh-workspace).

## Motivations

**Why did I move to the cloud?**

* I wanted to save money.
    * With a cloud-based platform, I only need a laptop as a web browser. I spent $170 on my [ASUS C201 Chromebook with 4GB RAM](http://www.amazon.com/gp/product/B00VUV0MG0).
    * I spend about $20 per month on [Google Cloud](https://cloud.google.com/) services.[^gce_prices]
    * I spend $10 per month on a [Cloud9 micro plan](https://c9.io/pricing/public) for the SSH workspaces.
* I wanted a reproducible environment. Snapshots can serve as simple backups of instances. For more complex platform managment, there's the [Google Cloud Shell](https://cloud.google.com/cloud-shell/docs/).
* I wanted to test the scalability of a pipeline. On a cloud platform, I can mount disks with large data sets and change the instance size to test how efficiently algorithms use CPUs and memory. Connecting other cloud services expands the possibilities.[^alts]

**Why do I use Google Cloud?**

Between Google Cloud and Amazon Web Services, I chose Google Cloud due to its intuitive UI. [SSH within the browser](https://cloud.google.com/compute/docs/ssh-in-browser) is very convenient.

**Why do I use IPython Notebooks?**

[IPython (Jupyter) Notebooks](http://ipython.org/notebook.html) are an important part of my development process since they enable me to prototype quickly and to share my work in-progress. The notebook serves as a top-level script, the parts of which I eventually modularize as components of installable packages. I prefer the [Continuum Analytics Anaconda Python distribution](https://www.continuum.io/) for its [Conda package manager](http://conda.pydata.org/docs/). I'm using Python 3.5.

**Why do I use Cloud9?**

I saw that [Cloud9 is popular](http://stackshare.io/stackups/cloud9-ide-vs-nitrous-io-vs-koding) and has good [documentation](https://docs.c9.io/docs/).[^c9_debug] I wanted a cloud-based IDE since I didn't want to spend resources on my Chromebook or on my instances to run the IDE.

## First-time setup

There are many ways to run a Jupyter Notebook server on a virtual machine instance. This is one example setup working from my Chromebook with details for newcomers:

* Create a Google Compute Engine virtual machine instance and SSH keys:
    * Make a project in the [Google Developers Console](https://console.developers.google.com).
    * Configure an instance:
        * Machine type: Start with the smallest machine type.[^mem_cpu]
        * Boot disk: Start with the default boot disk (Debian, 10GB).[^disk]
        * Firewall: Allow HTTP and HTTPS connections to use `curl` and `wget`.
        * Project access: Reserve an external IP address ("Networking" > "External IP"). Other settings can be left at default.[^ext_ip] For this example, I give `123.123.123.123` as my instance's static external IP address.
    * Connect to the instance, e.g. with Google's [in-browser SSH](https://cloud.google.com/compute/docs/ssh-in-browser).
    * [Update the Debian system.](http://askubuntu.com/questions/222348/what-does-sudo-apt-get-update-do)
    * [Generate an SSH key pair for the instance](https://help.github.com/articles/generating-ssh-keys/) and might as well connect to GitHub.[^use_less]
* Start a Jupyter Notebook server on the instance from the in-browser SSH:
    * [Install Python](https://www.continuum.io/downloads) on the instance.
    * Start a [Jupyter Notebook](http://jupyter.org/) server:  
      `$ jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser &`  
      `$ disown 1234` (where `1234` is the process ID)[^disown]
* Create an SSH tunnel to forward a local port to the server's port on the instance:
    * Generate an SSH key pair for the Chromebook as above[^keys] and add the Chromebook's public key to the instance's `authorized_keys`.[^cat]
    * Within Chrome, install [Chrome Secure Shell](https://chrome.google.com/webstore/detail/secure-shell/pnhechapfaindjhompbnflcldabbghjo) and forward a port (see screenshot above):  
    `Username: samuel_harrold` (in the instance's shell, run `whoami`)  
    `Hostname: 123.123.123.123` (the instance's external IP address)  
    `Port: 22`
    `Identity: id_rsa` [^import]  
    `SSH Arguments: -N -L localhost:8888:0.0.0.0:8888` [^no_f] [^paste]
    * View the server at `http://localhost:8888`.
* For an IDE, connect a Cloud9 remote SSH workspace to the instance:
    * [Install Node.js](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions) on the instance.
    * Create a [Cloud9 SSH workspace](https://docs.c9.io/docs/running-your-own-ssh-workspace), copy the public SSH key from Cloud9 to the instance's `authorized_keys` as above, then open the workspace:[^install_deps]  
      `Username: samuel_harrold` (in the instance's shell, run `whoami`)  
      `Hostname: 123.123.123.123` (the instance's external IP address)  
      `Initial path: /home/samuel_harrold`  
      `Port: 22`  
      `Node.js binary path: /usr/bin/nodejs` (in the instance's shell, run `which nodejs`)
* To shutdown the instance:
    * Close the Jupyter Notebook and the Chrome Secure Shell tabs. Kill the Jupyter Notebook server.[^lsof_kill]
    * Close the Cloud9 workspace tab.
    * "Stop" the instance in the Developers Console.
* For a simple backup of the instance, create a snapshot from the Developers Console. This can be done while the instance is running.
* To change the instance's machine type or disk size:
    * Shutdown the instance as above.
    * Create a snapshot of the instance.
    * Clone the instance but set the new boot disk to the new snapshot and...
        * ...if changing the machine type, set the new machine type.
        * ...if changing the disk size, set the new disk size.
    * Reassign the external IP address to the new instance.[^networking]
    * Start the Jupyter Notebook server on the instance and create an SSH tunnel as above.[^host_id]
    * Open the Cloud9 workspace.

## Helpful links

Some links I found helpful for this blog post:

* Chrome:
    * [Chrome app Secure Shell.](https://chrome.google.com/webstore/detail/secure-shell/pnhechapfaindjhompbnflcldabbghjo)
    * [Chrome app cookies.txt](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg) to export cookies from Chrome for `wget`.
    * To inspect system resources, `chrome://system` in Chrome's address bar.
    * To inspect RAM usage by Chrome, `chrome://memory-redirect` in Chrome's address bar (from the Chrome Task Manager).
* Chromebook:
    * [Chromebook 2GB vs 4GB Demo.](https://www.youtube.com/watch?v=y1dAnXkednM) I had to upgrade from a 2GB RAM Chromebook to a model with 4GB RAM since I typically use about 2.5GB RAM while working.
    * [Using a Chromebook as a developer.](http://jjg.svbtle.com/chromebook-for-developers-part-3) I've had my Chromebook for 2&nbsp;months and haven't yet needed developer mode.
    * [Low-profile flash drive](http://www.amazon.com/gp/product/B00LLER2CS) to expand the Chromebook's storage.
    * [Chromebook app SFTP.](https://chrome.google.com/webstore/detail/sftp-file-system/gbheifiifcfekkamhepkeogobihicgmn)
    * [Chomebook app Caret text editor.](https://chrome.google.com/webstore/detail/caret/fljalecfjciodhpcledpamjachpmelml)
* Linux:
    * [Choosing between Debian and Ubuntu.](http://www.datamation.com/open-source/debian-vs-ubuntu-which-is-best-for-you-1.html)
    * [SSH login without password.](http://www.linuxproblem.org/art_9.html)
    * [SSH port forwarding (tunnels) explained.](http://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html)
    * [Download from Google Drive with `wget`](http://unix.stackexchange.com/questions/136371/how-to-download-a-folder-from-google-drive-using-terminal)
    * [Download from Kaggle with `wget`](https://www.kaggle.com/forums/f/15/kaggle-forum/t/6604/downloading-data-via-command-line)
    * [`disown` examples.](http://www.cyberciti.biz/faq/unix-linux-disown-command-examples-usage-syntax/)
* IPython Notebooks:
    * [Running an IPython Notebook from Amazon Web Services.](https://gist.github.com/iamatypeofwalrus/5183133)
    * [Hosting a password-protected IPython Notebook on Google Compute Engine.](https://gist.github.com/samklr/07bee2868a6ed72a8ec4)

## Footnotes
<!-- From https://pythonhosted.org/Markdown/extensions/footnotes.html -->
///Footnotes Go Here///

[^gce_prices]:
    As of December 2015 on Google Compute Engine, running a 1-core shared virtual CPU instance with 0.6GB RAM costs about <span>$4.50</span> per month. Running a 32-core virtual CPU instance with 120GB RAM costs about <span>$1.12</span> per hour.
[^alts]:
    There are also hosted services like [Continuum Analytics Wakari](https://wakari.io/), [Cloud9 hosted workspaces](https://c9.io/?redirect=0), and [Digital Ocean](https://www.digitalocean.com/).
[^c9_debug]:
    As of December 2015, Cloud9 doesn't support debugging in Python. However, this hasn't been a problem for me since I use [pdb](https://docs.python.org/3.5/library/pdb.html) for debugging and [pytest](http://pytest.org/latest/) for testing. I use the IDE mostly for code navigation, autocomplete, and managing packages with many files.
[^mem_cpu]:
    Determine if more RAM is necessary by using `free -m` to display the free memory (RAM) in MB. Use the Developers Console to determine the CPU utilization.
[^disk]:
    Determine if more disk space is necessary by using `df -B MB` to display the free disk space in MB.
[^ext_ip]:
    Reassigning a static external IP address to a new instance when changing instances is often more convenient than changing an ephemeral IP address in all connections to the instance, e.g. in Chrome Secure Shell and Cloud9.
[^use_less]:
    For Google's in-browser SSH, `xclip` does not function. Copy the public key from `less`.
[^disown]:
    Disowning a background process (the control operator `&`) from the shell allows a process to continue running in the background when the shell is closed.
[^keys]:
    To create an SSH key pair for the Chromebook without going into the laptop's developer mode, generate an extra pair of keys on the instance as above then move them to the Chromebook. I save mine under `Downloads/ssh` (no dot-file access without developer mode). Transfer the keys by copy-paste using `less` from instance's in-browser SSH and [a text editor app for Chromebook](https://chrome.google.com/webstore/detail/caret/fljalecfjciodhpcledpamjachpmelml) or download them from a connected [Cloud9 SSH workspace](https://docs.c9.io/docs/running-your-own-ssh-workspace): right-click the file > "Download".
[^cat]:
    To copy a local public SSH key, e.g. `id_rsa.pub`, to a remote machine's `authorized_keys`, in the instance's in-browser shell:  
    `$ cat >> ~/.ssh/authorized_keys`  
    `[Ctrl+V to paste the local public key, then Enter]`  
    `[Ctrl+D to signal end of file]`  
[^import]:
    Select both of the Chromebook's private and public keys, `id_rsa` and `id_rsa.pub`, to import as a pair.
[^no_f]:
    Omit the `-f` option to keep Chrome Secure Shell's tunnel open. Pin the tab in Chrome (right-click the tab > "Pin tab") to keep Chrome Secure Shell open and minimized in the browser.
[^paste]:
    To paste the password for the Chromebook's SSH key, use Chrome's paste function ("Customize and control" > "Edit" > "Paste"; using Ctrl+V will input `^v` as the password). In place of `ssh-add` on my Chromebook, I use [LastPass](https://lastpass.com/) to manage passwords.
[^install_deps]:
    If the Cloud9 workspace fails to connect to the instance, e.g. the terminal within the workspace doesn't receive input, run the [Cloud9 dependency installation script](https://github.com/c9/install/) then reopen the workspace:  
    `curl -L https://raw.githubusercontent.com/c9/install/master/install.sh | bash`  
    (requires HTTPS traffic allowed in the instance's firewall settings)
[^lsof_kill]:
    In the instance's in-browser SSH:  
    `$ lsof -i:8888` (list process IDs filtered by port)  
    `$ kill 1234` (send a termination signal to the process ID)  
    (install `lsof` with `sudo apt-get install lsof`)
[^networking]:
    In the Developers Console, manage IP addresses under "Products & services" > "Networking".
[^host_id]:
    Because the external IP address was reassigned to a new instance, a warning will appear that the remote host identification has changed. To remove the offending ECDSA key from `known_hosts`, in Chrome, open the JavaScript console (Ctrl+Shift+J) and run `term_.command.removeKnownHostByIndex(idx)` where idx is the given line number in `known_hosts`, e.g. from the warning line `Offending ECDSA key in /.ssh/known_hosts:1`, idx=1.
