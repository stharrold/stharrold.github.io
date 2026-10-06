"""Build the site and check the published output.

These encode checks that were previously done by hand before deploying:
no drafts, analytics only in publish builds, working redirects and favicons.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GA_ID = "G-K4PX9089RZ"
DRAFT_SLUG = "20160221-predict-household-income-from-census"


def build(settings, output):
    """Run pelican with `settings` into `output`; fail on any warning."""
    result = subprocess.run(
        [sys.executable, "-m", "pelican", "--settings", settings, "--output", str(output), "--fatal", "warnings"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return output


def index_search(output):
    """Build the Pagefind search index into output/pagefind/, as CI does after Pelican."""
    result = subprocess.run([sys.executable, "-m", "pagefind", "--site", str(output)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return output


@pytest.fixture(scope="session")
def site(tmp_path_factory):
    return index_search(build("publishconf.py", tmp_path_factory.mktemp("publish")))


@pytest.fixture(scope="session")
def dev_site(tmp_path_factory):
    return build("pelicanconf.py", tmp_path_factory.mktemp("dev"))


def site_pages(site):
    """Theme-rendered HTML pages (excludes static notebook exports and alias redirect stubs)."""
    pages = [p for p in site.rglob("*.html") if "static" not in p.relative_to(site).parts]
    return [p for p in pages if 'http-equiv="refresh"' not in p.read_text()]


def test_publish_build_has_core_pages(site):
    for name in ["index.html", "archives.html", "tags.html", "categories.html", "search.html", "pages/about.html", "robots.txt"]:
        assert (site / name).is_file(), name


def test_drafts_are_not_published(site):
    assert not (site / "drafts").exists()
    leaked = [str(p.relative_to(site)) for p in site.rglob("*") if p.is_file() and DRAFT_SLUG in p.read_text(errors="ignore") + str(p)]
    assert leaked == []


def test_dev_build_still_renders_drafts(dev_site):
    assert (dev_site / "drafts" / f"{DRAFT_SLUG}.html").is_file()


def test_analytics_on_every_page_of_publish_build(site):
    pages = site_pages(site)
    assert pages
    for page in pages:
        html = page.read_text()
        assert f"gtag/js?id={GA_ID}" in html, page
        assert re.search(rf"gtag\('config', \"{GA_ID}\"", html), page
        assert "gtm.js" not in html, page
        assert "UA-43020842" not in html, page


def test_no_analytics_in_dev_build(dev_site):
    for page in site_pages(dev_site):
        assert "googletagmanager.com" not in page.read_text(), page


def test_alias_redirects(site):
    for alias, target in [("20151030_test.html", "/20151030-test.html"), ("20151208_ipynb_on_gce_from_chrome.html", "/20151208-ipynb-on-gce-from-chrome.html")]:
        html = (site / alias).read_text()
        assert f'content="0;url={target}"' in html
        assert (site / target.lstrip("/")).is_file()


def test_favicons_at_site_root(site):
    for name in ["favicon.ico", "favicon.png", "apple-touch-icon.png"]:
        assert (site / name).stat().st_size > 0, name
    assert 'rel="icon"' in (site / "index.html").read_text()


def test_search_index_covers_published_posts_and_pages_only(site):
    assert (site / "pagefind" / "pagefind-component-ui.js").is_file()
    entry = json.loads((site / "pagefind" / "pagefind-entry.json").read_text())
    # 3 published articles + the About page; list pages, drafts, and notebook exports are not indexed.
    assert sum(lang["page_count"] for lang in entry["languages"].values()) == 4


def test_no_third_party_fonts_or_jquery(site):
    for page in site_pages(site):
        html = page.read_text()
        assert "fonts.googleapis.com" not in html, page
        assert not re.search(r"<script[^>]+src=\"[^\"]*jquery", html, re.IGNORECASE), page
    for css in (site / "theme" / "css").glob("*.css"):
        assert "fonts.googleapis.com" not in css.read_text(), css


def test_math_rendering(site):
    etl = (site / "20160110-etl-census-with-python.html").read_text()
    # Display equations are blocks and inline math stays inline; MathJax 4 is loaded with SRI.
    assert etl.count('<div class="arithmatex">\\[') == 2
    assert etl.count('<span class="arithmatex">\\(') == 2
    assert re.search(r'mathjax@4[^"]*/tex-chtml\.js" integrity="sha384-', etl)
    # Prices such as "$20 per month" are not math, and pages without math don't load MathJax.
    gce = (site / "20151208-ipynb-on-gce-from-chrome.html").read_text()
    assert "arithmatex" not in gce
    assert "mathjax" not in gce.lower()


def test_feeds_use_absolute_urls(site):
    atom = (site / "feeds" / "all.atom.xml").read_text()
    assert "https://stharrold.github.io/" in atom
