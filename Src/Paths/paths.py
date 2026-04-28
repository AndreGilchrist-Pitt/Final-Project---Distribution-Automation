from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Main directories
SRC_DIR = PROJECT_ROOT / "Src"
DATA_DIR = PROJECT_ROOT / "Data"
POWERWORLD_DATA_DIR = DATA_DIR / "PowerWorld"
BASELINE_DATA_DIR = POWERWORLD_DATA_DIR / "BaselineData"

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

# Legacy/test directories
UNITTEST_DIR = PROJECT_ROOT / "UnitTest"
UNITTEST_CLASSES_DIR = UNITTEST_DIR / "Classes"



def ensure_directory_exists(directory: str | Path) -> Path:
    """
    Ensure a directory exists and return it as a Path.

    Args:
        directory: Directory path.

    Returns:
        Path object for the directory.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_parent_directory_exists(file_path: str | Path) -> Path:
    """
    Ensure the parent directory of a file exists and return the file path.

    Args:
        file_path: File path.

    Returns:
        Path object for the file.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path