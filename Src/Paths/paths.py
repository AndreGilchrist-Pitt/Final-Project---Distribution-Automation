from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Main directories
SRC_DIR = PROJECT_ROOT / "Src"
DATA_DIR = PROJECT_ROOT / "Data"
POWERWORLD_DATA_DIR = DATA_DIR / "PowerWorld"

BASELINE_DATA_DIR = POWERWORLD_DATA_DIR / "BaselineData"
CASE1_DATA_DIR = POWERWORLD_DATA_DIR / "Case1Data"
CASE2_DATA_DIR = POWERWORLD_DATA_DIR / "Case2Data"

# Source directories
MAIN_FILE = SRC_DIR / "main.py"
UTILS_DIR = SRC_DIR / "Utils"
CLASSES_DIR = UTILS_DIR / "Classes"
PROCESS_FILES_DIR = UTILS_DIR / "ProcessFiles"
CLASS_DIAGRAMS_DIR = SRC_DIR / "ClassDiagrams"

# Validation/test directories
VALIDATION_DIR = SRC_DIR / "Validation"
TEST_SCRIPTS_DIR = VALIDATION_DIR / "TestScripts"

# Baseline data files
POWERWORLD_BASELINE_EXCEL_FILE = BASELINE_DATA_DIR / "Figure14_22_Baseline.xlsx"

# Case 1 data files
POWERWORLD_CASE1_EXCEL_FILE = CASE1_DATA_DIR / "Figure14_22_Case1.xlsx"
POWERWORLD_CASE1_BUSES_JSON = CASE1_DATA_DIR / "Buses.json"
POWERWORLD_CASE1_CASE_SUMMARY_JSON = CASE1_DATA_DIR / "Case_Summary.json"

# Case 2 data files
POWERWORLD_CASE2_EXCEL_FILE = CASE2_DATA_DIR / "Figure14_22_Case2.xlsx"
POWERWORLD_CASE2_BUSES_JSON = CASE2_DATA_DIR / "Buses.json"
POWERWORLD_CASE2_CASE_SUMMARY_JSON = CASE2_DATA_DIR / "Case_Summary.json"

# Legacy/test directories
LEGACY_TEST = TEST_SCRIPTS_DIR / "legacy_test.py"


def ensure_directory_exists(directory: str | Path) -> Path:
    """
    Ensure a directory exists and return it as a Path.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_parent_directory_exists(file_path: str | Path) -> Path:
    """
    Ensure the parent directory of a file exists and return the file path.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def ensure_project_directories() -> None:
    """
    Ensure standard project data directories exist.
    """
    for directory in [
        DATA_DIR,
        POWERWORLD_DATA_DIR,
        BASELINE_DATA_DIR,
        CASE1_DATA_DIR,
        CASE2_DATA_DIR,
        VALIDATION_DIR,
        TEST_SCRIPTS_DIR,
    ]:
        ensure_directory_exists(directory)