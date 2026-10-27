"""Verified access to the data snapshot, and the pre-registration outcome lock.

Every file is hashed before it is read. A file whose hash is in data-snapshot.tsv is real CMS data; if it is an outcome
file (results, county spending, county assignment) it can be read only once REGISTRATION.md exists. Synthetic data
directories carry a marker file and never hash-match the manifest, so they load freely. There is no flag to bypass this.
"""

import csv
import hashlib
from pathlib import Path

from ratchet import config


class OutcomeLockedError(RuntimeError):
    """Raised when a real outcome file is requested before the plan is registered."""


def load_manifest(manifest: Path = config.MANIFEST) -> dict[str, str]:
    """Map file name to sha256 from the snapshot manifest."""
    with open(manifest, newline="") as fh:
        return {row["file"]: row["sha256"] for row in csv.DictReader(fh, delimiter="\t")}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def is_outcome(name: str) -> bool:
    return name.startswith(config.OUTCOME_PREFIXES)


def is_synthetic(data_dir: Path) -> bool:
    return (data_dir / config.SYNTHETIC_MARKER).exists()


def checked_path(data_dir: Path, name: str, registration: Path = config.REGISTRATION) -> Path:
    """Return the path of a snapshot file after verifying it; refuse real outcome files before registration."""
    path = data_dir / name
    digest = sha256(path)
    manifest = load_manifest()
    real = digest in manifest.values()
    if real and manifest.get(name) != digest:
        raise ValueError(f"{name}: contents match a different manifest entry")
    if not real and not is_synthetic(data_dir):
        raise ValueError(f"{name}: sha256 {digest} does not match data-snapshot.tsv")
    if real and is_outcome(name) and not registration.exists():
        raise OutcomeLockedError(f"{name} is an outcome file; it cannot be read until REGISTRATION.md exists")
    return path


def read_header(path: Path) -> list[str]:
    """Column names only: reads the first row of a CSV and nothing else (used to check names before registration)."""
    with open(path, newline="", encoding="latin-1") as fh:
        return next(csv.reader(fh))
