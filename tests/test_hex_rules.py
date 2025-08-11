import unittest
from unittest.mock import patch
from hex_rules import HexAutomaton, HexRule, HexCell


class TestHexRules(unittest.TestCase):
    """Test the hexagonal rule notation system."""

    def setUp(self) -> None:
        """Set up test automaton."""
        self.automaton = HexAutomaton(radius=5)

    def test_hex_cell_creation(self) -> None:
        """Test HexCell creation and representation."""
        cell1 = HexCell("a")
        self.assertEqual(str(cell1), "a")
        self.assertEqual(cell1.state, "a")
        self.assertIsNone(cell1.direction)

        cell2 = HexCell("b", 3)
        self.assertEqual(str(cell2), "b3")
        self.assertEqual(cell2.state, "b")
        self.assertEqual(cell2.direction, 3)

    def test_simple_rule_parsing(self) -> None:
        """Test parsing of simple rules."""
        rule = HexRule("a => b")
        self.assertEqual(rule.source_state, "a")
        self.assertEqual(rule.target_state, "b")
        self.assertIsNone(rule.source_direction)
        self.assertIsNone(rule.target_direction)

    def test_directional_rule_parsing(self) -> None:
        """Test parsing of directional rules."""
        rule = HexRule("a3 => b1")
        self.assertEqual(rule.source_state, "a")
        self.assertEqual(rule.source_direction, 3)
        self.assertEqual(rule.target_state, "b")
        self.assertEqual(rule.target_direction, 1)

    def test_conditional_rule_parsing(self) -> None:
        """Test parsing of conditional rules."""
        rule = HexRule("a[x] => b")
        self.assertEqual(rule.source_state, "a")
        self.assertEqual(rule.target_state, "b")
        self.assertEqual(rule.condition_state, "x")
        self.assertIsNone(rule.condition_direction)

    def test_directional_conditional_rule(self) -> None:
        """Test parsing of directional conditional rules."""
        rule = HexRule("a[1x] => b")
        self.assertEqual(rule.source_state, "a")
        self.assertEqual(rule.target_state, "b")
        self.assertEqual(rule.condition_state, "x")
        self.assertEqual(rule.condition_direction, 1)

    def test_negated_condition(self) -> None:
        """Test parsing of negated conditions."""
        rule = HexRule("a[-x] => b")
        self.assertEqual(rule.condition_state, "x")
        self.assertTrue(rule.condition_negated)

    def test_simple_rule_application(self) -> None:
        """Test application of simple unconditional rules."""
        self.automaton.set_rules(["a => b"])

        # Set up initial state
        self.automaton.set_cell(0, 0, "a")
        self.assertEqual(self.automaton.get_cell(0, 0).state, "a")

        # Apply one step
        self.automaton.step()

        # Check result
        self.assertEqual(self.automaton.get_cell(0, 0).state, "b")

    def test_conditional_rule_application(self) -> None:
        """Test application of conditional rules."""
        self.automaton.set_rules(["a[x] => b"])

        # Set up initial state - 'a' cell with 'x' neighbor
        self.automaton.set_cell(0, 0, "a")
        self.automaton.set_cell(1, 0, "x")  # Neighbor in direction 1

        # Apply one step
        self.automaton.step()

        # Check result - should change to 'b' because neighbor exists
        self.assertEqual(self.automaton.get_cell(0, 0).state, "b")

    def test_conditional_rule_no_match(self) -> None:
        """Test conditional rule when condition is not met."""
        self.automaton.set_rules(["a[x] => b"])

        # Set up initial state - 'a' cell without 'x' neighbor
        self.automaton.set_cell(0, 0, "a")
        self.automaton.set_cell(1, 0, "y")  # Different neighbor

        # Apply one step
        self.automaton.step()

        # Check result - should remain 'a' because condition not met
        self.assertEqual(self.automaton.get_cell(0, 0).state, "a")

    def test_multiple_rules(self) -> None:
        """Test system with multiple rules."""
        rules = ["a => b", "b => c", "c => a"]
        self.automaton.set_rules(rules)

        # Set up initial state
        self.automaton.set_cell(0, 0, "a")

        # Apply three steps to cycle through states
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "b")

        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "c")

        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "a")

    def test_macro_expansion_planning(self) -> None:
        """Test that macro expansion framework is in place."""
        # This tests that the expansion method exists and can handle basic rules
        rules = self.automaton._expand_macros("a => b")
        self.assertEqual(rules, ["a => b"])

        # Test that it doesn't crash on complex rules
        complex_rules = self.automaton._expand_macros("a[x] => b")
        self.assertIsInstance(complex_rules, list)

    def test_substep_selection_and_application(self) -> None:
        """Test rule selection and random application substeps."""
        self.automaton.set_rules(["a => b", "a => c"])
        self.automaton.set_cell(0, 0, "a")

        selections = self.automaton.select_applicable_rules()
        self.assertEqual(len(selections[(0, 0)]), 2)

        with patch("hex_rules.random.choice", side_effect=lambda seq: seq[0]):
            self.automaton.apply_random_rules(selections)

        self.assertEqual(self.automaton.get_cell(0, 0).state, "b")


if __name__ == "__main__":
    unittest.main()
