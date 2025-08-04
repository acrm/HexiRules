#!/usr/bin/env python3
"""
HexiRules Code Quality Checker
Runs comprehensive code quality checks: MyPy, Black, and Unit Tests
"""

import subprocess
import sys
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
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"{check_name}: {status}")
    if output and not passed:
        print(f"Output:\n{output}")


def main() -> int:
    """Run all code quality checks."""
    print("🔍 HexiRules Code Quality Checker")
    print("Running comprehensive code quality checks...")

    all_passed = True

    # 1. MyPy Type Checking
    print_header("MyPy Type Checking")
    mypy_passed, mypy_output = run_command(
        [
            sys.executable,
            "-m",
            "mypy",
            "main.py",
            "automaton.py",
            "version.py",
            "cli.py",
            "check_quality.py",
        ],
        "MyPy Type Checking",
    )
    print_result("MyPy", mypy_passed, mypy_output if not mypy_passed else "")
    all_passed = all_passed and mypy_passed

    # 2. Black Code Formatting
    print_header("Black Code Formatting Check")
    black_passed, black_output = run_command(
        [
            sys.executable,
            "-m",
            "black",
            "--check",
            "main.py",
            "automaton.py",
            "version.py",
            "cli.py",
            "check_quality.py",
        ],
        "Black Formatting",
    )
    print_result("Black", black_passed, black_output if not black_passed else "")
    all_passed = all_passed and black_passed

    # 3. Unit Tests
    print_header("Unit Tests")
    test_passed, test_output = run_command(
        [sys.executable, "-m", "unittest", "discover", "tests/", "-v"],
        "Unit Tests",
    )
    print_result("Tests", test_passed, test_output if not test_passed else "")
    all_passed = all_passed and test_passed

    # Final Summary
    print_header("Final Summary")
    if all_passed:
        print("🎉 All code quality checks PASSED!")
        print("✅ MyPy: No type errors")
        print("✅ Black: Code properly formatted")
        print("✅ Tests: All tests passing")
        return 0
    else:
        print("⚠️  Some code quality checks FAILED!")
        print("❌ Check the output above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
