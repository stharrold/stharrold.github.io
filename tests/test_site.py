"""Build the site and check the published output.

These encode checks that were previously done by hand before deploying: no drafts published, analytics only in
publish builds, redirects, search, math, comments, sitemap. Expectations are derived from content/ and data/,
so adding, publishing, or editing posts needs no test changes.
"""

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
SITEURL = "https://stharrold.github.io"
GA_ID = "G-K4PX9089RZ"


def metadata(path):
    """Pelican Markdown metadata: `Key: value` lines up to the first blank line, keys lowercased."""
    meta = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            break
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip().lower()] = value.strip()
    return meta


def posts(status):
    """Articles in content/ (not pages) with the given status; Pelican's default status is 'published'."""
    return [m for m in map(metadata, sorted(CONTENT.glob("*.md"))) if m.get("status", "published").lower() == status]


def pages(*statuses):
    return [m for m in map(metadata, sorted((CONTENT / "pages").glob("*.md"))) if m.get("status", "published").lower() in statuses]


def source_text(slug):
    return next(p for p in CONTENT.glob("*.md") if metadata(p).get("slug") == slug).read_text()


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
    html_pages = [p for p in site.rglob("*.html") if "static" not in p.relative_to(site).parts]
    return [p for p in html_pages if 'http-equiv="refresh"' not in p.read_text()]


def test_publish_build_has_core_pages(site):
    for name in ["index.html", "archives.html", "tags.html", "categories.html", "search.html", "robots.txt"]:
        assert (site / name).is_file(), name
    for post in posts("published"):
        assert (site / f"{post['slug']}.html").is_file(), post["slug"]


def test_drafts_are_not_published(site):
    assert not (site / "drafts").exists()
    for draft in posts("draft"):
        leaked = [str(p.relative_to(site)) for p in site.rglob("*") if p.is_file() and draft["slug"] in p.read_text(errors="ignore") + str(p)]
        assert leaked == [], f"Draft {draft['slug']} leaked; if it has content/static/{draft['slug']}/, add it to STATIC_EXCLUDES in publishconf.py"


def test_static_excludes_only_hold_drafts():
    """STATIC_EXCLUDES hides drafts' static files; a published post must not be excluded (its links would break)."""
    excludes = re.search(r"STATIC_EXCLUDES = \[(.*?)\]", (ROOT / "publishconf.py").read_text(), re.S)
    excluded = set(re.findall(r'"static/([^"]+)"', excludes.group(1))) if excludes else set()
    drafts = {d["slug"] for d in posts("draft")}
    stale = excluded - drafts
    assert not stale, f"Published posts still in STATIC_EXCLUDES in publishconf.py; remove: {sorted(stale)}"


def test_dev_build_still_renders_drafts(dev_site):
    for draft in posts("draft"):
        assert (dev_site / "drafts" / f"{draft['slug']}.html").is_file(), draft["slug"]


def test_analytics_on_every_page_of_publish_build(site):
    rendered = site_pages(site)
    assert rendered
    for page in rendered:
        html = page.read_text()
        assert f"gtag/js?id={GA_ID}" in html, page
        assert re.search(rf"gtag\('config', \"{GA_ID}\"", html), page
        assert "gtm.js" not in html, page
        assert "UA-43020842" not in html, page


def test_no_analytics_in_dev_build(dev_site):
    for page in site_pages(dev_site):
        assert "googletagmanager.com" not in page.read_text(), page


def test_alias_redirects(site):
    aliases = [(alias.strip(), post["slug"]) for post in posts("published") for alias in post.get("alias", "").split(",") if alias.strip()]
    assert aliases
    for alias, slug in aliases:
        html = (site / alias.lstrip("/")).read_text()
        assert f'content="0;url=/{slug}.html"' in html, alias


def test_favicons_at_site_root(site):
    for name in ["favicon.ico", "favicon.png", "apple-touch-icon.png"]:
        assert (site / name).stat().st_size > 0, name
    assert 'rel="icon"' in (site / "index.html").read_text()


def test_search_index_covers_published_posts_and_pages_only(site):
    assert (site / "pagefind" / "pagefind-component-ui.js").is_file()
    entry = json.loads((site / "pagefind" / "pagefind-entry.json").read_text())
    # Published articles + published and hidden pages; list pages, drafts, and notebook exports are not indexed.
    expected = len(posts("published")) + len(pages("published", "hidden"))
    assert sum(lang["page_count"] for lang in entry["languages"].values()) == expected


def test_sitemap_and_robots(site):
    urls = set(re.findall(r"<loc>([^<]+)</loc>", (site / "sitemap.xml").read_text()))
    expected = {f"{SITEURL}/", f"{SITEURL}/archives.html"}
    expected |= {f"{SITEURL}/{p['slug']}.html" for p in posts("published")}
    expected |= {f"{SITEURL}/pages/{p['slug']}.html" for p in pages("published")}
    assert urls == expected
    assert f"Sitemap: {SITEURL}/sitemap.xml" in (site / "robots.txt").read_text()


def test_privacy_page_linked_from_footer_not_menu(site):
    index = (site / "index.html").read_text()
    assert (site / "pages" / "privacy.html").is_file()
    assert f'href="{SITEURL}/pages/privacy.html">Privacy</a>' in index
    assert f'class="nav-link" href="{SITEURL}/pages/privacy.html"' not in index


def test_no_third_party_fonts_or_jquery(site):
    for page in site_pages(site):
        html = page.read_text()
        assert "fonts.googleapis.com" not in html, page
        assert not re.search(r"<script[^>]+src=\"[^\"]*jquery", html, re.IGNORECASE), page
    for css in (site / "theme" / "css").glob("*.css"):
        assert "fonts.googleapis.com" not in css.read_text(), css


def test_math_rendering(site):
    for post in posts("published"):
        html = (site / f"{post['slug']}.html").read_text()
        # Every $$...$$ in the source (outside code) must render as a display block, not inline.
        prose = re.sub(r"```.*?```|`[^`\n]*`", "", source_text(post["slug"]), flags=re.S)
        assert html.count('<div class="arithmatex">') == prose.count("$$") // 2, post["slug"]
        # MathJax (pinned, with SRI) loads exactly on pages that have math.
        has_math = 'class="arithmatex"' in html
        assert has_math == bool(re.search(r'mathjax@4[^"]*/tex-chtml\.js" integrity="sha384-', html)), post["slug"]
        assert has_math or "mathjax" not in html.lower(), post["slug"]


def test_comments_are_giscus_with_archived_disqus(site):
    for post in posts("published"):
        html = (site / f"{post['slug']}.html").read_text()
        assert 'src="https://giscus.app/client.js"' in html, post["slug"]
        assert f'data-term="{post["slug"]}"' in html, post["slug"]
        assert "disqus.com/embed.js" not in html, post["slug"]
    archived = sorted((ROOT / "data" / "archived-comments").glob("*.html"))
    assert archived
    for snippet in archived:
        count = snippet.read_text().count('<div class="comment">')
        html = (site / f"{snippet.stem}.html").read_text()
        assert f"Archived comments ({count})" in html, snippet.stem
        assert "disq.us/url" not in html, snippet.stem


def test_feeds_use_absolute_urls(site):
    atom = (site / "feeds" / "all.atom.xml").read_text()
    assert f"{SITEURL}/" in atom


def test_copyright_range_in_footer(site):
    """Footer shows first-post year through build year on every page, including tag and category pages."""
    first_year = min(int(post["date"][:4]) for post in posts("published"))
    expected = f"&copy; {first_year}&ndash;{datetime.date.today().year} "
    for page in site_pages(site):
        assert expected in page.read_text(), page


def test_structured_data_on_posts(site):
    """Every published post carries schema.org BlogPosting JSON-LD (issue #49)."""
    for post in posts("published"):
        html = (site / f"{post['slug']}.html").read_text()
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        assert len(blocks) == 1, post["slug"]
        data = json.loads(blocks[0])
        assert data["@type"] == "BlogPosting", post["slug"]
        assert data["url"] == f"{SITEURL}/{post['slug']}.html", post["slug"]
        assert data["headline"] and data["datePublished"] and data["author"]["name"], post["slug"]
        assert "<" not in data["description"], post["slug"]
