"""Download the study's CMS data snapshot and check every file against data-snapshot.tsv.

Each file listed in data-snapshot.tsv is downloaded from its data.cms.gov URL into the data directory (by default
the one the pipeline reads, ratchet/config.py DEFAULT_DATA_DIR) and kept only if its sha256 matches the manifest.
Files already present with the right hash are left alone, so the script can be rerun after an interruption.

CMS sometimes replaces a file in place. If a download no longer matches, the script takes that file from the archived
copy of the snapshot on OSF (ARCHIVE_URL), a zip of exactly the files in the manifest. `--archive` points at another
copy (a URL or a local zip), and `--archive-only` skips data.cms.gov entirely.

Standard library only; outside the registered analysis code (ratchet/, dbt/, tests/), so it changes nothing in it.

Usage, from the repository root:

    python3 analysis/mssp-benchmark-ratchet/fetch_snapshot.py                     # download and check
    python3 analysis/mssp-benchmark-ratchet/fetch_snapshot.py --data-dir <dir>    # elsewhere; pass the same --data-dir to run.py
    python3 analysis/mssp-benchmark-ratchet/fetch_snapshot.py --archive-only      # everything from the OSF archive
    python3 analysis/mssp-benchmark-ratchet/fetch_snapshot.py --make-archive <zip>  # maintainers: build the archive
"""

import argparse
import csv
import hashlib
import io
import shutil
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ratchet import config  # noqa: E402

# The archived snapshot on OSF (osf.io/53aqd in project osf.io/z4an5); its sha256 is in the study README.
ARCHIVE_URL = "https://osf.io/53aqd/download"
USER_AGENT = "mssp-benchmark-ratchet fetch_snapshot (+https://github.com/stharrold/stharrold.github.io)"
# Fixed zip metadata, so rebuilding the archive from the same files (with the same zlib) gives the same sha256.
ZIP_DATE = (2026, 10, 22, 0, 0, 0)


def manifest(path: Path = config.MANIFEST) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, attempts: int = 3) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except OSError as error:
            if attempt == attempts:
                raise
            print(f"  retrying ({error})", file=sys.stderr)
            time.sleep(5 * attempt)
    raise AssertionError("unreachable")


def write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(data)
    Path(tmp.name).replace(path)


def open_archive(source: str) -> zipfile.ZipFile:
    if source.startswith(("http://", "https://")):
        print(f"downloading the archived snapshot from {source}")
        return zipfile.ZipFile(io.BytesIO(download(source)))
    return zipfile.ZipFile(source)


def fetch(data_dir: Path, archive: str | None, archive_only: bool) -> int:
    data_dir.mkdir(parents=True, exist_ok=True)
    rows = manifest()
    missing = []
    for row in rows:
        path = data_dir / row["file"]
        if path.is_file() and sha256_file(path) == row["sha256"]:
            print(f"ok       {row['file']}")
            continue
        if archive_only:
            missing.append(row)
            continue
        try:
            data = download(row["url"])
        except OSError as error:
            print(f"failed   {row['file']}: {error}")
            missing.append(row)
            continue
        if sha256_bytes(data) != row["sha256"]:
            print(f"changed  {row['file']}: CMS now serves a different file; will use the archive")
            missing.append(row)
            continue
        write(path, data)
        print(f"fetched  {row['file']}")

    if missing:
        if not archive:
            print(f"\n{len(missing)} file(s) not fetched, and no archive is set (pass --archive <url or zip>).")
            return 1
        with open_archive(archive) as zf:
            names = set(zf.namelist())
            for row in missing:
                if row["file"] not in names:
                    print(f"absent   {row['file']}: not in the archive")
                    continue
                data = zf.read(row["file"])
                if sha256_bytes(data) != row["sha256"]:
                    print(f"bad      {row['file']}: the archive copy does not match the manifest")
                    continue
                write(data_dir / row["file"], data)
                print(f"archive  {row['file']}")

    bad = [row["file"] for row in rows if not (data_dir / row["file"]).is_file() or sha256_file(data_dir / row["file"]) != row["sha256"]]
    if bad:
        print(f"\n{len(bad)} of {len(rows)} files are still missing or wrong: {', '.join(bad)}")
        return 1
    print(f"\nAll {len(rows)} files match data-snapshot.tsv, in {data_dir}")
    return 0


def make_archive(data_dir: Path, out: Path) -> int:
    """Zip exactly the manifest's files, checked, with fixed metadata."""
    rows = sorted(manifest(), key=lambda row: row["file"])
    bad = [row["file"] for row in rows if not (data_dir / row["file"]).is_file() or sha256_file(data_dir / row["file"]) != row["sha256"]]
    if bad:
        print(f"not archiving: {len(bad)} file(s) missing or wrong in {data_dir}: {', '.join(bad)}")
        return 1
    with zipfile.ZipFile(out, "w") as zf:
        for name in ["data-snapshot.tsv"] + [row["file"] for row in rows]:
            info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            source = config.MANIFEST if name == "data-snapshot.tsv" else data_dir / name
            with open(source, "rb") as src, zf.open(info, "w") as dst:
                shutil.copyfileobj(src, dst)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB), sha256 {sha256_file(out)}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", type=Path, default=config.DEFAULT_DATA_DIR, help=f"where to put the files (default {config.DEFAULT_DATA_DIR})")
    parser.add_argument("--archive", default=ARCHIVE_URL, help="URL or local path of the archived snapshot zip (default: the OSF copy)")
    parser.add_argument("--archive-only", action="store_true", help="take every file from the archive, not data.cms.gov")
    parser.add_argument("--make-archive", type=Path, metavar="ZIP", help="build the archive zip from --data-dir and exit")
    args = parser.parse_args()
    if args.make_archive:
        sys.exit(make_archive(args.data_dir, args.make_archive))
    if args.archive_only and not args.archive:
        parser.error("--archive-only needs an archive (--archive)")
    sys.exit(fetch(args.data_dir, args.archive, args.archive_only))


if __name__ == "__main__":
    main()
