#!/usr/bin/env python3
"""
Test suite for non-GUI components that can be tested without Tkinter
"""

import unittest

# Import constants from domain layer now that UI is decoupled
from domain.constants import STATE_COLORS, SYMBOLIC_STATES
GUI_AVAILABLE = True


class TestGUIConstants(unittest.TestCase):
    """Test GUI constants and configurations."""

    def test_state_colors_completeness(self):
        """Test that all symbolic states have colors defined."""
        if not GUI_AVAILABLE:
            self.skipTest("GUI not available (no tkinter)")
        for state in SYMBOLIC_STATES:
            self.assertIn(state, STATE_COLORS, f"State '{state}' missing color")

    def test_state_colors_format(self):
        """Test that all colors are properly formatted."""
        if not GUI_AVAILABLE:
            self.skipTest("GUI not available (no tkinter)")
        for state, color in STATE_COLORS.items():
            self.assertIsInstance(
                color, str, f"Color for state '{state}' is not a string"
            )
            self.assertTrue(len(color) > 0, f"Color for state '{state}' is empty")
            # Colors should be either named colors or hex colors
            if color.startswith("#"):
                self.assertTrue(
                    len(color) in [4, 7], f"Invalid hex color format: {color}"
                )

    def test_symbolic_states_coverage(self):
        """Test that we have a reasonable set of symbolic states."""
        if not GUI_AVAILABLE:
            self.skipTest("GUI not available (no tkinter)")
        # Should have empty state
        self.assertIn("_", SYMBOLIC_STATES)

        # Should have basic states
        expected_states = ["_", "a", "b", "c", "t", "x"]
        for state in expected_states:
            self.assertIn(state, SYMBOLIC_STATES, f"Expected state '{state}' not found")

        # Should have enough states for interesting automata
        self.assertGreaterEqual(len(SYMBOLIC_STATES), 6)


if __name__ == "__main__":
    unittest.main()
