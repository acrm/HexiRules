#!/usr/bin/env python3
"""
Comprehensive test runner for HexiRules.
Runs root-level tests (e.g., test_hex_rules.py) and automatically discovers and runs all test modules in the tests/ directory.
Provides a compact, Windows-friendly summary without Unicode emojis.
"""

import unittest
import sys
import os
from typing import Iterator, Callable

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


def _load_root_tests(loader: unittest.TestLoader, suite: unittest.TestSuite, tests_dir: str) -> int:
    """Load root-level tests if tests/ isn't a package."""
    total_loaded = 0
    has_tests_pkg = os.path.isdir(tests_dir) and os.path.isfile(
        os.path.join(tests_dir, "__init__.py")
    )
    if not has_tests_pkg:
        root_tests = ["test_hex_rules", "test_gui_constants"]
        for name in root_tests:
            try:
                module = __import__(name)
                mod_suite = loader.loadTestsFromModule(module)
                suite.addTest(mod_suite)
                count = mod_suite.countTestCases()
                total_loaded += count
                print(f"Loaded {count} tests from {name}")
            except ImportError:
                continue
    return total_loaded

def _load_package_tests(loader: unittest.TestLoader, suite: unittest.TestSuite, tests_dir: str, include_gui: bool) -> int:
    """Discover and load all tests from the tests/ directory."""
    total_loaded = 0
    if os.path.isdir(tests_dir):
        discovered_suite = loader.discover(
            start_dir=tests_dir,
            pattern="test*.py",
            top_level_dir=os.path.dirname(__file__),
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
                return not mod.endswith(".test_canvas")

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
    tests_dir = os.path.join(os.path.dirname(__file__), "tests")

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
