from pathlib import Path
import runpy

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_SCRIPTS_DIR = PROJECT_ROOT / "Src" / "Validation" / "TestScripts"


def run_test_script(script_name: str) -> bool:
    """
    Run a validation test script by filename.

    Args:
        script_name: Name of the Python test file inside Src/Validation/TestScripts.

    Returns:
        True if the script completed without raising an exception, otherwise False.
    """
    script_path = TEST_SCRIPTS_DIR / script_name

    print()
    print("=" * 100)
    print(f"Running {script_name}")
    print("=" * 100)

    if not script_path.exists():
        print(f"FAILED: Test script not found: {script_path}")
        return False

    try:
        runpy.run_path(str(script_path), run_name="__main__")
    except Exception as error:
        print()
        print("-" * 100)
        print(f"FAILED: {script_name}")
        print(f"Error type: {type(error).__name__}")
        print(f"Error     : {error}")
        print("-" * 100)
        return False

    print()
    print("-" * 100)
    print(f"COMPLETED: {script_name}")
    print("-" * 100)
    return True


def main() -> None:
    """
    Run all validation cases.
    """
    test_scripts = [
        "baseline_test.py",
        "case1_test.py",
        "case2_test.py",
    ]

    results = {}

    for script_name in test_scripts:
        results[script_name] = run_test_script(script_name)

    print()
    print("=" * 100)
    print("Validation Summary")
    print("=" * 100)

    for script_name, passed in results.items():
        status = "COMPLETED" if passed else "FAILED"
        print(f"{script_name:20s} {status}")

    print("=" * 100)

    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()