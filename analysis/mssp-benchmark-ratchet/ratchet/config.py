"""File names, paths and fixed settings. Section numbers refer to PREREGISTRATION.md."""

from pathlib import Path

STUDY_DIR = Path(__file__).resolve().parents[1]
MANIFEST = STUDY_DIR / "data-snapshot.tsv"
REGISTRATION = STUDY_DIR / "REGISTRATION.md"
RESULTS_DIR = STUDY_DIR / "results"
SQL_DIR = Path(__file__).resolve().parent / "sql"
DEFAULT_DATA_DIR = Path.home() / ".cache" / "stharrold-github-io" / "mssp-snapshot-2026-10-22"

# Marker written by ratchet.synthetic; a data directory without it must hash-match the manifest.
SYNTHETIC_MARKER = "SYNTHETIC-DATA-NOT-CMS"

# Enrollment files by table suffix (section 2.1). Both PY2019 files are read for agreement history (4.3 step 3).
ENROLLMENT_FILES = {
    "2016": "SSP_ACOs_2016_12_31.csv",
    "2017": "SSP_ACOs_2017_01_01.csv",
    "2018": "SSP_ACOs_2018_01_01.csv",
    "2019a": "SSP_ACOs_2019_01_01.csv",
    "2019b": "SSP_ACOs_2019_07_31.csv",
    "2020": "SSP_ACOs_2020_01_07.csv",
    "2021": "SSP_ACOs_2021_01_01.csv",
    "2022": "SSP_ACOs_2022_01_01.csv",
    # PY2023-PY2024: agreement status in the H4 post-period (section 4.5).
    "2023": "SSP_ACOs_2023_01_01.csv",
    "2024": "PY2024_Medicare_Shared_Savings_Program_Organizations.csv",
}

# Outcome files: locked until REGISTRATION.md exists (ratchet.snapshot). PY2019 is the 12-month / July-December file, never 2019A.
RESULTS_FILES = {
    2016: "Performance_Year_Financial_and_Quality_Results_2016_suppress.csv",
    2017: "Performance_Year_Financial_and_Quality_Results_2017_suppress.csv",
    2018: "Performance_Year_Financial_and_Quality_Results_2018_suppress.csv",
    2019: "Performance_Year_Financial_and_Quality_Results_2019_suppress.csv",
    2020: "Performance_Year_Financial_and_Quality_Results_2020_suppress.csv",
    2021: "Performance_Year_Financial_and_Quality_Results_2021_suppress.csv",
    2022: "Performance_Year_Financial_and_Quality_Results_PUF_2022_01_01.csv",
}
# Only for the descriptive spending-by-agreement-year table (section 5.6).
DESCRIPTIVE_RESULTS_FILES = {2023: "PY 2023 ACO Results PUF.csv", 2024: "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv"}
COUNTY_FILES = {year: f"FFS_Data_for_SSP_CRB_PUF_{year}_01_01_Cal_Year_Assignable_2022_2023_Starters.csv" for year in (2019, 2020, 2021)}
ASSIGNMENT_FILE = "Number_Of_ACO_Assigned_Beneficiaries_by_County_PUF_2021_01_01.csv"
OUTCOME_PREFIXES = ("Performance_Year_Financial", "PY_Financial", "PY 2023", "FFS_Data_for_SSP", "Number_Of_ACO_Assigned")

# Enrollment types, in the order used everywhere.
TYPES = ("ESRD", "DIS", "AGDU", "AGND")

# Resampling (sections 5, 5.4).
N_RESAMPLES = 10_000
SEED = 20261022
