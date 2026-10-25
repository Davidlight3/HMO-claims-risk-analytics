from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

# Python/ is one level below the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "Raw_Data"
VALIDATED_DATA_DIR = PROJECT_ROOT / "Validated_Data"


# ============================================================
# DATA GENERATION SETTINGS
# ============================================================

RANDOM_SEED = 42

START_DATE = "2022-01-01"
END_DATE = "2025-12-31"


# ============================================================
# TARGET RECORD COUNTS
# ============================================================

NUM_HMOS = 5
NUM_PLANS = 20
NUM_MEMBERS = 10_000
NUM_PROVIDERS = 120
NUM_DIAGNOSES = 35
NUM_SERVICES = 30

NUM_CLAIMS = 100_000

if __name__ == "__main__":
    print("Project Root:", PROJECT_ROOT)
    print("Raw Data:", RAW_DATA_DIR)
    print("Validated Data:", VALIDATED_DATA_DIR)
    print("Number of HMOs:", NUM_HMOS)
    print("Number of Members:", NUM_MEMBERS)
    print("Number of Claims:", NUM_CLAIMS)