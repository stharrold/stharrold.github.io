r"""Write redirect pages for the `Alias:` metadata of articles and pages.

Notes:
    * Python 3 port of pelican_alias.py from https://github.com/Nitron/pelican-alias
      (commit c4ff0304cfb03a24e887e2643e5e5c373a995978). Changes: `urlparse` import, ruff lint and format.
    * The upstream package (PyPI `pelican-alias` 1.1) is Python 2 only.

License:
    The MIT License (MIT)

    Copyright (c) 2013 Christopher Williams

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

"""

import logging
import os.path
from urllib.parse import urlparse

from pelican import signals

logger = logging.getLogger(__name__)


class AliasGenerator:
    TEMPLATE = """<!DOCTYPE html><html><head><meta charset="utf-8" />
<meta http-equiv="refresh" content="0;url={destination}" />
</head></html>"""

    def __init__(self, context, settings, path, theme, output_path, *args):
        self.output_path = output_path
        self.context = context
        self.alias_delimiter = settings.get("ALIAS_DELIMITER", ",")

    def create_alias(self, page, alias):
        # If path starts with a /, remove it
        if alias[0] == "/":
            relative_alias = alias[1:]
        else:
            relative_alias = alias

        path = os.path.join(self.output_path, relative_alias)
        directory, filename = os.path.split(path)

        try:
            os.makedirs(directory)
        except OSError:
            pass

        if filename == "":
            path = os.path.join(path, "index.html")

        logger.info("[alias] Writing to alias file %s", path)
        with open(path, "w") as fd:
            destination = page.url
            # if schema is empty then we are working with a local path
            if not urlparse(destination).scheme:
                # if local path is missing a leading slash then add it
                if not destination.startswith("/"):
                    destination = f"/{destination}"
            fd.write(self.TEMPLATE.format(destination=destination))

    def generate_output(self, writer):
        pages = self.context["pages"] + self.context["articles"] + self.context.get("hidden_pages", [])

        for page in pages:
            aliases = page.metadata.get("alias", [])
            if not isinstance(aliases, list):
                aliases = aliases.split(self.alias_delimiter)
            for alias in aliases:
                alias = alias.strip()
                logger.info("[alias] Processing alias %s", alias)
                self.create_alias(page, alias)


def get_generators(generators):
    return AliasGenerator


def register():
    signals.get_generators.connect(get_generators)
