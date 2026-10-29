"""Channel art for the blog's YouTube channel, Data Science Demos (@DSDemos), in the site's own colours and font.

The avatar is the site's "DS" monogram (content/extra/apple-touch-icon.png): white Lato on Flatly's navbar navy,
#2c3e50. Each image is an HTML page rendered by headless Chrome with the theme's Lato files
(themes/datasciencedemos/static/fonts/), so nothing is downloaded. Output goes to assets/youtube/, which is outside
content/ so Pelican does not publish it; assets/youtube/README.md records what was uploaded to YouTube and when.

Run from the repository root (needs Google Chrome):

    uv run --no-sync python scripts/youtube_art.py
"""

import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "themes" / "datasciencedemos" / "static" / "fonts"
OUT = ROOT / "assets" / "youtube"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NAVY = "#2c3e50"  # Flatly --bs-primary, the navbar and the favicon background

TEAL = "#18bc9c"  # Flatly --bs-success, the site's link colour; only for the rule, as text it is 4.6:1 on the navy

# name: (width, height, page body, extra CSS). YouTube recommends an 800 x 800 avatar and shows it as a circle,
# as small as 24 px, so the monogram is two letters centred well inside the circle. The banner is 2560 x 1440, but
# phones show only the centre 1546 x 423, so all its text sits inside that box.
ART = {
    "avatar": (800, 800, '<div class="t">DS</div>', ".t { font-weight: 400; font-size: 380px; letter-spacing: 4px; line-height: 1; margin-top: -20px; }"),
    "banner": (
        2560,
        1440,
        '<div class="safe"><div class="name">Data Science Demos</div><div class="rule"></div><div class="sub">stharrold.github.io</div></div>',
        ".safe { width: 1546px; height: 423px; display: flex; flex-direction: column; align-items: center; justify-content: center; }"
        " .name { font-weight: 700; font-size: 128px; line-height: 1; }"
        f" .rule {{ width: 160px; height: 8px; background: {TEAL}; margin: 40px 0 36px; border-radius: 4px; }}"
        " .sub { font-weight: 400; font-size: 56px; line-height: 1; color: #dee2e6; letter-spacing: 1px; }",
    ),
}


def page(width: int, height: int, body: str, css: str) -> str:
    faces = "\n".join(
        f'@font-face {{ font-family: Lato; font-weight: {w}; src: url("{(FONTS / f"lato-latin-{w}-normal.woff2").as_uri()}") format("woff2"); }}' for w in (400, 700)
    )
    return f"""<!doctype html><meta charset="utf-8"><style>
{faces}
html, body {{ margin: 0; width: {width}px; height: {height}px; overflow: hidden; background: {NAVY}; }}
body {{ display: flex; align-items: center; justify-content: center; font-family: Lato; color: #fff; }}
{css}
</style><body>{body}</body>
"""


def png_size(png: Path) -> tuple[int, int]:
    """Width and height from the PNG's IHDR chunk."""
    return struct.unpack(">II", png.read_bytes()[16:24])


def render(name: str, width: int, height: int, body: str, css: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / f"{name}.png"
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / f"{name}.html"
        html.write_text(page(width, height, body, css))
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                f"--user-data-dir={tmp}/profile",
                f"--window-size={width},{height}",
                "--virtual-time-budget=2000",  # let the web fonts load before the screenshot
                f"--screenshot={png}",
                html.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    if png_size(png) != (width, height):
        raise SystemExit(f"{png} is {png_size(png)}, expected {(width, height)}")
    return png


def main() -> None:
    for name, (width, height, body, css) in ART.items():
        print(render(name, width, height, body, css).relative_to(ROOT))


if __name__ == "__main__":
    main()
