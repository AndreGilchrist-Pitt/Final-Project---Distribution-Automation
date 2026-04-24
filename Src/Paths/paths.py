from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Main directories
SRC_DIR = PROJECT_ROOT / "Src"
MAIN_FILE = SRC_DIR / "main.py"
UTILS_DIR = SRC_DIR / "Utils"
CLASSES_DIR = UTILS_DIR / "Classes"
CLASS_DIAGRAMS_DIR = SRC_DIR / "ClassDiagrams"
UNITTEST_DIR = PROJECT_ROOT / "UnitTest"
UNITTEST_CLASSES_DIR = UNITTEST_DIR / "Classes"
MILESTONE_VALIDATION_HELP_DIR = PROJECT_ROOT / "MilestoneValidationHelp"