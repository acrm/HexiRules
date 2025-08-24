#!/usr/bin/env python3
"""HexiRules Code Quality Checker."""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=".", check=False
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")


def print_result(check_name: str, passed: bool, output: str = "") -> None:
    """Print the result of a check."""
    status = "PASSED" if passed else "FAILED"
    print(f"{check_name}: {status}")
    if output and not passed:
        print(f"Output:\n{output}")


def module_available(module: str) -> bool:
    """Return True if a Python module can be imported."""
    try:
        __import__(module)
        return True
    except Exception:
        return False


def discover_python_files(root: Path) -> List[str]:
    """Discover all Python files to check, excluding common ignore paths.

    Also skips top-level compatibility wrapper(s) like check_quality.py to
    avoid MyPy duplicate module conflicts with tools/check_quality.py.
    """
    ignore_dirs = {
        ".git",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        "venv",
        ".venv",
        "env",
        "build",
        "dist",
    }
    files: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # prune ignored directories in-place for efficiency
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for fname in filenames:
            if fname.endswith(".py"):
                path = Path(dirpath) / fname
                # Skip root-level compatibility wrappers to avoid module duplication
                if path.parent == root and path.name in {
                    "check_quality.py",
                    "run_tests.py",
                }:
                    continue
                files.append(str(path))
    return files


# Define the web directory path as a constant for flexibility
WEB_DIR_RELATIVE = Path("src/infrastructure/ui/hexios/web")

def main() -> int:
    """Run all code quality checks."""
    print("HexiRules Code Quality Checker")
    print("Running comprehensive code quality checks...")

    all_passed = True
    repo_root = Path(__file__).resolve().parent.parent
    py_files = discover_python_files(repo_root)
    # Ensure deterministic order for tooling output
    py_files.sort()

    # 1. MyPy Type Checking
    print_header("MyPy Type Checking")
    mypy_status = "skipped"
    if module_available("mypy"):
        mypy_cmd = [sys.executable, "-m", "mypy", *py_files]
        mypy_passed, mypy_output = run_command(mypy_cmd, "MyPy Type Checking")
        print_result("MyPy", mypy_passed, mypy_output if not mypy_passed else "")
        all_passed = all_passed and mypy_passed
        mypy_status = "passed" if mypy_passed else "failed"
    else:
        print("MyPy: SKIPPED (module not installed)")

    # 2. Black Code Formatting
    print_header("Black Code Formatting Check")
    black_status = "skipped"
    if module_available("black"):
        black_cmd = [sys.executable, "-m", "black", "--check", str(repo_root)]
        black_passed, black_output = run_command(black_cmd, "Black Formatting")
        print_result("Black", black_passed, black_output if not black_passed else "")
        all_passed = all_passed and black_passed
        black_status = "passed" if black_passed else "failed"
    else:
        print("Black: SKIPPED (module not installed)")

    # 3. Unit Tests
    print_header("Unit Tests")
    test_cmd = [sys.executable, str(repo_root / "tools" / "run_tests.py")]
    test_passed, test_output = run_command(test_cmd, "Unit Tests")
    print_result("Tests", test_passed, test_output if not test_passed else "")
    all_passed = all_passed and test_passed

    # 4. Web Build and Type Check
    print_header("Web Build and Type Check")
    web_dir = repo_root / WEB_DIR_RELATIVE
    if (web_dir / "package.json").exists():
        ci_cmd = ["npm", "--prefix", str(web_dir), "ci"]
        ci_passed, ci_output = run_command(ci_cmd, "Web Dependency Install")
        print_result(
            "Web Dependency Install", ci_passed, ci_output if not ci_passed else ""
        )

        build_cmd = ["npm", "--prefix", str(web_dir), "run", "build"]
        build_passed, build_output = run_command(build_cmd, "Web Build")
        print_result(
            "Web Build", build_passed, build_output if not build_passed else ""
        )

        type_cmd = ["npm", "--prefix", str(web_dir), "run", "typecheck"]
        type_passed, type_output = run_command(type_cmd, "Web Type Check")
        print_result(
            "Web Type Check", type_passed, type_output if not type_passed else ""
        )
        all_passed = all_passed and ci_passed and build_passed and type_passed
    else:
        print("Web directory not found; skipping web checks")

    # Final Summary
    print_header("Final Summary")
    if all_passed:
        print("All code quality checks passed")
        if mypy_status == "passed":
            print("MyPy: No type errors")
        elif mypy_status == "skipped":
            print("MyPy: Skipped (not installed)")
        else:
            print("MyPy: Failed")

        if black_status == "passed":
            print("Black: Code properly formatted")
        elif black_status == "skipped":
            print("Black: Skipped (not installed)")
        else:
            print("Black: Formatting issues found")

        print("Tests: All tests passing")
        return 0

    print("Some code quality checks failed")
    print("Check the output above for details")
    return 1


if __name__ == "__main__":
    sys.exit(main())
