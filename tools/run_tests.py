#!/usr/bin/env python3
"""Run the HexiRules test suite."""

import os
import sys
import unittest
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
# Ensure imports work for both 'from src.module' and 'from module'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))


def _load_root_tests(
    loader: unittest.TestLoader, suite: unittest.TestSuite, tests_dir: str
) -> int:
    """Backward compatibility placeholder."""
    return 0


def _load_package_tests(
    loader: unittest.TestLoader,
    suite: unittest.TestSuite,
    tests_dir: str,
    include_gui: bool,
) -> int:
    """Discover and load all tests from the tests/ directory."""
    total_loaded = 0
    if os.path.isdir(tests_dir):
        discovered_suite = loader.discover(
            start_dir=tests_dir,
            pattern="test*.py",
            top_level_dir=str(ROOT),
        )

        def iter_cases(suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
            for item in suite:
                if isinstance(item, unittest.TestSuite):
                    yield from iter_cases(item)
                else:
                    yield item

        if not include_gui or os.getenv("HEXIRULES_NO_GUI") == "1":

            def predicate(tc: unittest.TestCase) -> bool:
                mod = getattr(tc.__class__, "__module__", "")
                return not (
                    mod.endswith(".test_canvas") or mod.endswith(".test_gui_constants")
                )

            filtered = unittest.TestSuite()
            for case in iter_cases(discovered_suite):
                if predicate(case):
                    filtered.addTest(case)
            discovered_suite = filtered
        suite.addTests(discovered_suite)
        count = discovered_suite.countTestCases()
        total_loaded += count
        print(f"Loaded {count} tests from tests/ directory")
    return total_loaded


def run_all_tests(include_gui: bool = True) -> int:
    """Run all test suites and return process exit code."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    tests_dir = str(ROOT / "tests")

    total_loaded = _load_root_tests(loader, suite, tests_dir)
    total_loaded += _load_package_tests(loader, suite, tests_dir, include_gui)

    print("\nRunning tests...\n")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_rate = (
        (result.testsRun - len(result.failures) - len(result.errors))
        / result.testsRun
        * 100
        if result.testsRun
        else 0
    )
    print(f"Success rate: {success_rate:.1f}%")

    return 0 if result.wasSuccessful() else 1


def run_tests(include_gui: bool = True) -> bool:
    """Compatibility wrapper returning True on success."""
    return run_all_tests(include_gui=include_gui) == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run HexiRules tests")
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Skip GUI tests (useful for headless environments)",
    )

    args = parser.parse_args()
    exit_code = run_all_tests(include_gui=not args.no_gui)
    sys.exit(exit_code)
