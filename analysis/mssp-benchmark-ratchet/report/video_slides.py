"""The PDF of the video deck and the transcript for the post, from the deck.

The deck is content/static/<slug>/video-slides.pptx ("Resetting the Target Early"); the narration is in its speaker
notes, one "[Clip NN]" per slide, and matches the video (analysis/mssp-benchmark-ratchet/video/). Browsers cannot
show a .pptx, so this writes video-slides.pdf next to it (the deck with its fonts embedded, the portable download)
and prints the transcript as HTML for the post, under the video. Every word comes from the deck; nothing is retyped.
Until 2026-10-29 it also wrote slide images and slides.json for a slide viewer, which the embedded video replaced.

Rendering needs Keynote and the deck's two fonts installed for the user: Public Sans (embedded in the .pptx, under
ppt/fonts/, as uncompressed EOT; the TrueType data is each file's last FontDataSize bytes) and Domine (used for the
headings but not embedded; OFL, from https://github.com/google/fonts/tree/main/ofl/domine). Without them Keynote
substitutes Helvetica. Keynote reads only files under the home folder, so the export runs in ~/.keynote-export-tmp.

Run from the repository root (pdffonts and pdfinfo are from poppler):

    uv run --no-sync python analysis/mssp-benchmark-ratchet/report/video_slides.py            # export with Keynote
    uv run --no-sync python analysis/mssp-benchmark-ratchet/report/video_slides.py --pdf X.pdf  # use an exported PDF
"""

import argparse
import html
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[3]
STATIC = ROOT / "content" / "static" / "20261027-preregistered-mssp-early-renewal"
DECK = STATIC / "video-slides.pptx"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
CLIP_RE = re.compile(r"\[Clip [0-9]+[a-z]?\]\s*")


def paragraphs(xml: bytes) -> list[str]:
    """The text of each non-empty paragraph (a:p) in a slide or notes part, in document order."""
    # Office parts never declare a DOCTYPE; refusing one rules out entity tricks (XXE, entity expansion).
    if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml:
        raise SystemExit("refusing an XML part with a DOCTYPE or ENTITY declaration")
    out = []
    for p in ElementTree.fromstring(xml).iter(f"{A}p"):
        text = "".join(t.text or "" for t in p.iter(f"{A}t")).strip()
        if text:
            out.append(text)
    return out


def slide_number(name: str) -> int:
    return int(re.search(r"(\d+)\.xml$", name).group(1))


def read_deck(deck: Path) -> list[dict]:
    """Per slide: its text (joined paragraphs) and its narration (the notes without clip markers)."""
    with zipfile.ZipFile(deck) as z:
        names = z.namelist()
        slides = sorted((n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)), key=slide_number)
        out = []
        for name in slides:
            n = slide_number(name)
            notes_name = f"ppt/notesSlides/notesSlide{n}.xml"
            notes = paragraphs(z.read(notes_name)) if notes_name in names else []
            # Notes placeholders also hold the slide number; drop bare numbers.
            narration = " ".join(CLIP_RE.sub("", t) for t in notes if not t.isdigit()).strip()
            out.append({"text": " ".join(paragraphs(z.read(name))), "narration": narration})
    return out


def keynote_pdf(deck: Path, work: Path) -> Path:
    """Export the deck to PDF with Keynote (fonts must be installed; see the module docstring)."""
    work.mkdir(parents=True, exist_ok=True)
    src, pdf = work / "deck.pptx", work / "deck.pdf"
    shutil.copy2(deck, src)
    pdf.unlink(missing_ok=True)
    script = f'''tell application "Keynote"
  set d to open POSIX file "{src}"
  delay 3
  export d to POSIX file "{pdf}" as PDF
  close d saving no
end tell'''
    subprocess.run(["osascript", "-e", script], check=True)
    return pdf


def check_fonts(pdf: Path) -> None:
    """Refuse a PDF where Keynote substituted a font: the deck uses only Public Sans and Domine."""
    fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    names = {line.split()[0].split("+")[-1] for line in fonts if line.strip()}
    wrong = sorted(n for n in names if not n.startswith(("PublicSans", "Domine")))
    if wrong:
        raise SystemExit(f"{pdf} uses substituted fonts {wrong}; install Public Sans and Domine (see the docstring)")


def transcript_html(slides: list[dict]) -> str:
    items = "\n".join(f"<li>{html.escape(s['narration'])}</li>" for s in slides)
    return f'<ol class="mssp-video-transcript">\n{items}\n</ol>'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pdf", type=Path, help="a PDF already exported from the deck (skips Keynote)")
    args = parser.parse_args()
    slides = read_deck(DECK)
    pdf = args.pdf or keynote_pdf(DECK, Path.home() / ".keynote-export-tmp")
    check_fonts(pdf)
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout).group(1))
    if pages != len(slides):
        raise SystemExit(f"{pdf} has {pages} pages, the deck {len(slides)} slides")

    if pdf.resolve() != (STATIC / "video-slides.pdf").resolve():
        shutil.copyfile(pdf, STATIC / "video-slides.pdf")
    print(transcript_html(slides))


if __name__ == "__main__":
    main()
