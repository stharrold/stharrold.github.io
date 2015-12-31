# code

Source code for examples from [Data Science Demos](https://stharrold.github.io).

## Installation

Clone from GitHub, import `stharrold.github.io/content/static/code/code` as a local package:
```
$ git clone https://github.com/stharrold/stharrold.github.io.git
$ python
>>> import sys
>>> sys.path.insert(0, r'stharrold.github.io/content/static/code')
>>> import code
```

## Testing

Use [pytest](http://pytest.org/) within `stharrold.github.io/content/static/code`:
```
$ git clone https://github.com/stharrold/stharrold.github.io.git
$ cd stharrold.github.io/content/static/code
$ py.test -v
```
