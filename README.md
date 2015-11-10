# stharrold.github.io

GitHub page for stharrold, [Data Science Demos](https://stharrold.github.io), with source code (`_src` branches).  

## Building

This repository contains both the source code for the page and the generated output from [`pelican`](http://blog.getpelican.com/). The pages served by GitHub are on the `master` branch, which is managed with [`ghp-import`](https://pypi.python.org/pypi/ghp-import). The `_src` branches are managed following [Vincent Driessen's Git branching model](http://nvie.com/posts/a-successful-git-branching-model/).

How to build the site for development:
```bash
$ git checkout develop_src
$ pelican --settings publishconf.py
$ cd output
$ python -m http.server 8000 &
$ # Inspect the page at localhost:8000
```

How to build the site for deployment:
```bash
$ git checkout master_src
$ pelican --settings publishconf.py
$ ghp-import output -b master -p
$ # View the page at https://stharrold.github.io/
```
