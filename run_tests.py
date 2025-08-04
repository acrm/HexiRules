#!/usr/bin/env python3
"""
Test runner script that can run tests with or without GUI components.
"""
import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


def run_tests(include_gui=True):
    """Run tests, optionally including GUI tests."""
    if include_gui:
        # Run all tests
        loader = unittest.TestLoader()
        suite = loader.discover("tests", pattern="test_*.py")
    else:
        # Run only non-GUI tests
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Add specific test modules that don't require GUI
        from tests import test_automaton, test_logic

        suite.addTests(loader.loadTestsFromModule(test_automaton))
        suite.addTests(loader.loadTestsFromModule(test_logic))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run HexiRules tests")
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Skip GUI tests (useful for headless environments)",
    )

    args = parser.parse_args()

    success = run_tests(include_gui=not args.no_gui)
    sys.exit(0 if success else 1)
