import sys
from pathlib import Path

# The study directory name has hyphens, so make the `ratchet` package importable directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
