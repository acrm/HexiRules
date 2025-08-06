#!/usr/bin/env python3
"""
Test suite for non-GUI components that can be tested without Tkinter
"""

import unittest
from gui import STATE_COLORS, SYMBOLIC_STATES


class TestGUIConstants(unittest.TestCase):
    """Test GUI constants and configurations."""
    
    def test_state_colors_completeness(self):
        """Test that all symbolic states have colors defined."""
        for state in SYMBOLIC_STATES:
            self.assertIn(state, STATE_COLORS, f"State '{state}' missing color")
    
    def test_state_colors_format(self):
        """Test that all colors are properly formatted."""
        for state, color in STATE_COLORS.items():
            self.assertIsInstance(color, str, f"Color for state '{state}' is not a string")
            self.assertTrue(len(color) > 0, f"Color for state '{state}' is empty")
            # Colors should be either named colors or hex colors
            if color.startswith('#'):
                self.assertTrue(len(color) in [4, 7], f"Invalid hex color format: {color}")
    
    def test_symbolic_states_coverage(self):
        """Test that we have a reasonable set of symbolic states."""
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
