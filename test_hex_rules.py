#!/usr/bin/env python3
"""
Comprehensive test suite for HexiRules system
Tests all core functionality including macro expansion, rule application, and cellular automaton behavior
"""

import unittest
from hex_rules import HexCell, HexRule, HexAutomaton


class TestHexCell(unittest.TestCase):
    """Test HexCell class functionality."""

    def test_hex_cell_creation(self):
        """Test creating HexCell instances."""
        # Empty cell
        cell = HexCell()
        self.assertEqual(cell.state, "_")
        self.assertIsNone(cell.direction)
        self.assertEqual(str(cell), "_")

        # Cell with state only
        cell = HexCell("a")
        self.assertEqual(cell.state, "a")
        self.assertIsNone(cell.direction)
        self.assertEqual(str(cell), "a")

        # Cell with state and direction
        cell = HexCell("t", 3)
        self.assertEqual(cell.state, "t")
        self.assertEqual(cell.direction, 3)
        self.assertEqual(str(cell), "t3")

    def test_hex_cell_equality(self):
        """Test HexCell equality comparison."""
        cell1 = HexCell("a", 1)
        cell2 = HexCell("a", 1)
        cell3 = HexCell("a", 2)
        cell4 = HexCell("b", 1)

        self.assertEqual(cell1, cell2)
        self.assertNotEqual(cell1, cell3)
        self.assertNotEqual(cell1, cell4)


class TestHexRule(unittest.TestCase):
    """Test HexRule parsing and functionality."""

    def test_simple_rule_parsing(self):
        """Test parsing simple rules."""
        rule = HexRule("a => b")
        self.assertEqual(rule.source_state, "a")
        self.assertIsNone(rule.source_direction)
        self.assertEqual(rule.target_state, "b")
        self.assertIsNone(rule.target_direction)
        self.assertEqual(rule.condition_state, "")

    def test_directional_rule_parsing(self):
        """Test parsing rules with directions."""
        rule = HexRule("a3 => b2")
        self.assertEqual(rule.source_state, "a")
        self.assertEqual(rule.source_direction, 3)
        self.assertEqual(rule.target_state, "b")
        self.assertEqual(rule.target_direction, 2)

    def test_condition_rule_parsing(self):
        """Test parsing rules with conditions."""
        rule = HexRule("a[b] => c")
        self.assertEqual(rule.source_state, "a")
        self.assertEqual(rule.condition_state, "b")
        self.assertEqual(rule.target_state, "c")
        self.assertFalse(rule.condition_negated)

        # Negated condition
        rule = HexRule("a[-b] => c")
        self.assertEqual(rule.condition_state, "b")
        self.assertTrue(rule.condition_negated)

    def test_directional_condition_parsing(self):
        """Test parsing rules with directional conditions."""
        rule = HexRule("a[2b] => c")
        self.assertEqual(rule.condition_direction, 2)
        self.assertEqual(rule.condition_state, "b")

        # Pointing condition
        rule = HexRule("a[2b4] => c")
        self.assertEqual(rule.condition_direction, 2)
        self.assertEqual(rule.condition_state, "b")
        self.assertEqual(rule.condition_pointing_direction, 4)

    def test_macro_rule_parsing(self):
        """Test parsing rules with % macro."""
        rule = HexRule("t% => x")
        self.assertEqual(rule.source_state, "t")
        self.assertEqual(rule.source_direction, "random")

        rule = HexRule("a => b%")
        self.assertEqual(rule.target_state, "b")
        self.assertEqual(rule.target_rotation, 0)


class TestHexAutomaton(unittest.TestCase):
    """Test HexAutomaton functionality."""

    def setUp(self):
        """Set up test automaton."""
        self.automaton = HexAutomaton(radius=3)

    def test_automaton_initialization(self):
        """Test automaton initialization."""
        self.assertEqual(self.automaton.radius, 3)
        self.assertEqual(len(self.automaton.rules), 0)

        # Check grid is initialized with empty cells
        empty_count = sum(
            1 for cell in self.automaton.grid.values() if cell.state == "_"
        )
        total_cells = len(self.automaton.grid)
        self.assertEqual(empty_count, total_cells)

    def test_cell_manipulation(self):
        """Test setting and getting cells."""
        # Set a cell
        self.automaton.set_cell(0, 0, "a", 3)
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "a")
        self.assertEqual(cell.direction, 3)

        # Get non-existent cell (should return empty)
        cell = self.automaton.get_cell(100, 100)
        self.assertEqual(cell.state, "_")
        self.assertIsNone(cell.direction)

    def test_neighbors(self):
        """Test neighbor calculation."""
        neighbors = self.automaton.get_neighbors(0, 0)
        expected = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        self.assertEqual(neighbors, expected)

    def test_simple_rule_application(self):
        """Test applying simple rules."""
        # Set up: a cell at (0,0)
        self.automaton.set_cell(0, 0, "a")

        # Rule: a => b
        self.automaton.set_rules(["a => b"])
        self.assertEqual(len(self.automaton.rules), 1)

        # Step
        self.automaton.step()

        # Check result
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "b")
        self.assertIsNone(cell.direction)

    def test_conditional_rule_application(self):
        """Test applying rules with conditions."""
        # Set up: 'a' at (0,0), 'b' at (1,0)
        self.automaton.set_cell(0, 0, "a")
        self.automaton.set_cell(1, 0, "b")

        # Rule: a[b] => c (a becomes c if adjacent to b)
        self.automaton.set_rules(["a[b] => c"])

        # Step
        self.automaton.step()

        # Check result - should change because b is adjacent
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "c")

    def test_negated_condition(self):
        """Test rules with negated conditions."""
        # Set up: 'a' at (0,0), no 'b' neighbors
        self.automaton.set_cell(0, 0, "a")

        # Rule: a[-b] => c (a becomes c if NOT adjacent to b)
        self.automaton.set_rules(["a[-b] => c"])

        # Step
        self.automaton.step()

        # Check result - should change because no b is adjacent
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "c")

        # Now add a 'b' neighbor and test again
        self.automaton.set_cell(0, 0, "a")  # Reset
        self.automaton.set_cell(1, 0, "b")  # Add b neighbor

        # Step again
        self.automaton.step()

        # Should NOT change because b is now adjacent
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "a")

    def test_directional_rule_matching(self):
        """Test that directional rules only match correct directions."""
        # Set up: t1 at (0,0)
        self.automaton.set_cell(0, 0, "t", 1)

        # Rule: t2 => a (should NOT match t1)
        self.automaton.set_rules(["t2 => a"])

        # Step
        self.automaton.step()

        # Should not change
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "t")
        self.assertEqual(cell.direction, 1)

        # Now test matching rule
        self.automaton.set_rules(["t1 => a"])
        self.automaton.step()

        # Should change
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "a")

    def test_non_directional_rule_matching(self):
        """Test that non-directional rules only match non-directional cells."""
        # Set up: t1 at (0,0) (has direction)
        self.automaton.set_cell(0, 0, "t", 1)

        # Rule: t => a (should NOT match t1)
        self.automaton.set_rules(["t => a"])

        # Step
        self.automaton.step()

        # Should not change
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "t")
        self.assertEqual(cell.direction, 1)

        # Now test with non-directional cell
        self.automaton.set_cell(0, 0, "t")  # No direction
        self.automaton.step()

        # Should change
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "a")
        self.assertIsNone(cell.direction)


class TestMacroExpansion(unittest.TestCase):
    """Test macro expansion functionality."""

    def setUp(self):
        """Set up test automaton."""
        self.automaton = HexAutomaton(radius=3)

    def test_target_macro_expansion(self):
        """Test expansion of target % macro."""
        # Rule: a => b%
        self.automaton.set_rules(["a => b%"])

        # Should expand to 6 rules
        self.assertEqual(len(self.automaton.rules), 6)

        # Check all directions are present
        rule_strings = [rule.rule_str for rule in self.automaton.rules]
        for i in range(1, 7):
            self.assertIn(f"a => b{i}", rule_strings)

    def test_source_macro_expansion(self):
        """Test expansion of source % macro."""
        # Rule: t%[a] => b
        self.automaton.set_rules(["t%[a] => b"])

        # Should expand to 7 rules (6 directions + no direction)
        self.assertEqual(len(self.automaton.rules), 7)

        # Check expansions
        rule_strings = [rule.rule_str for rule in self.automaton.rules]
        self.assertIn("t[a] => b", rule_strings)  # No direction
        for i in range(1, 7):
            self.assertIn(f"t{i}[a] => b", rule_strings)  # Each direction

    def test_pointing_condition_expansion(self):
        """Test expansion of pointing condition [x.] macro."""
        # Rule: _[t.] => a
        self.automaton.set_rules(["_[t.] => a"])

        # Should expand to 6 rules (one for each direction)
        self.assertEqual(len(self.automaton.rules), 6)

        # Check expansions - each rule should check for t pointing toward center
        rule_strings = [rule.rule_str for rule in self.automaton.rules]
        expected_rules = [
            "_[1t4] => a",  # t in direction 1 pointing to direction 4 (opposite)
            "_[2t5] => a",  # t in direction 2 pointing to direction 5
            "_[3t6] => a",  # t in direction 3 pointing to direction 6
            "_[4t1] => a",  # t in direction 4 pointing to direction 1
            "_[5t2] => a",  # t in direction 5 pointing to direction 2
            "_[6t3] => a",  # t in direction 6 pointing to direction 3
        ]
        for expected in expected_rules:
            self.assertIn(expected, rule_strings)


class TestComplexScenarios(unittest.TestCase):
    """Test complex cellular automaton scenarios."""

    def setUp(self):
        """Set up test automaton."""
        self.automaton = HexAutomaton(radius=5)

    def test_movement_and_direction_persistence(self):
        """Test that % macro creates persistent direction."""
        # Set up: t at (0,0) with no direction
        self.automaton.set_cell(0, 0, "t")

        # Rules that should create movement with persistent direction
        rules = ["t[-a] => t%", "_[t.] => a", "t%[a] => t"]
        self.automaton.set_rules(rules)

        # Step 1: t should gain a direction
        self.automaton.step()
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "t")
        self.assertIsNotNone(cell.direction)
        initial_direction = cell.direction

        # Step 2: direction should be preserved, pointing rule should fire
        self.automaton.step()
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "t")
        self.assertEqual(cell.direction, initial_direction)  # Direction preserved

        # Check that 'a' was created by pointing rule
        active_cells = self.automaton.get_active_cells()
        self.assertGreater(len(active_cells), 1)  # Should have t and at least one a

    def test_direction_removal(self):
        """Test that rules can remove direction from cells."""
        # Set up: t2 at (0,0), a at (1,0)
        self.automaton.set_cell(0, 0, "t", 2)
        self.automaton.set_cell(1, 0, "a")

        # Rule: t%[a] => t (directional t with adjacent a becomes non-directional)
        self.automaton.set_rules(["t%[a] => t"])

        # Step
        self.automaton.step()

        # Check result - should lose direction
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual(cell.state, "t")
        self.assertIsNone(cell.direction)

    def test_randomization_behavior(self):
        """Test that multiple matching macro rules are chosen randomly."""
        # Set up: multiple t cells that should all match the same macro
        positions = [(0, 0), (2, 0), (-2, 0)]
        for pos in positions:
            self.automaton.set_cell(pos[0], pos[1], "t")

        # Rule: t => a% (should randomly choose direction for each)
        self.automaton.set_rules(["t => a%"])

        # Step multiple times and collect results
        results = []
        for _ in range(10):
            # Reset
            for pos in positions:
                self.automaton.set_cell(pos[0], pos[1], "t")

            # Step
            self.automaton.step()

            # Collect directions
            step_result = []
            for pos in positions:
                cell = self.automaton.get_cell(pos[0], pos[1])
                step_result.append(cell.direction)
            results.append(step_result)

        # Check that we got different results (randomization working)
        unique_results = set(tuple(r) for r in results)
        self.assertGreater(len(unique_results), 1, "Should have randomized results")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test automaton."""
        self.automaton = HexAutomaton(radius=3)

    def test_invalid_rule_syntax(self):
        """Test handling of invalid rule syntax."""
        # Should not crash, just skip invalid rules
        self.automaton.set_rules(["invalid rule", "a => b", "another invalid"])

        # Should have parsed only the valid rule
        self.assertEqual(len(self.automaton.rules), 1)
        self.assertEqual(self.automaton.rules[0].rule_str, "a => b")

    def test_boundary_conditions(self):
        """Test behavior at grid boundaries."""
        # Set up cell at boundary
        self.automaton.set_cell(3, 0, "a")  # At radius boundary

        # Rule that checks neighbors
        self.automaton.set_rules(["a[b] => c"])

        # Should not crash even though some neighbors are out of bounds
        self.automaton.step()

        # Cell should remain unchanged (no b neighbors)
        cell = self.automaton.get_cell(3, 0)
        self.assertEqual(cell.state, "a")

    def test_clear_functionality(self):
        """Test clearing the automaton."""
        # Set up some cells
        self.automaton.set_cell(0, 0, "a", 1)
        self.automaton.set_cell(1, 0, "b", 2)

        # Clear
        self.automaton.clear()

        # Check all cells are empty
        for cell in self.automaton.grid.values():
            self.assertEqual(cell.state, "_")
            self.assertIsNone(cell.direction)


if __name__ == "__main__":
    unittest.main()
