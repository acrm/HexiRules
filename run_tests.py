#!/usr/bin/env python3
"""
Comprehensive test runner for HexiRules
Runs all test suites and provides a summary
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def run_all_tests():
    """Run all test suites and return results."""
    # Test modules to run
    test_modules = [
        'test_hex_rules',
        'test_gui_constants',
    ]
    
    # Load and run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    total_tests = 0
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            module_suite = loader.loadTestsFromModule(module)
            suite.addTest(module_suite)
            total_tests += module_suite.countTestCases()
            print(f"Loaded {module_suite.countTestCases()} tests from {module_name}")
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")
    
    print(f"\nRunning {total_tests} tests total...\n")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, trace in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, trace in result.errors:
            print(f"  - {test}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)


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
