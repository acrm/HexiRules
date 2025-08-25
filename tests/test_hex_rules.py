import unittest
from unittest.mock import patch
from domain.hexidirect.rule_engine import HexAutomaton
from domain.hexidirect.rule_parser import HexRule
from domain.hexidirect.models import HexCell


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
        self.automaton.set_cell(1, -1, "x")  # Neighbor in direction 1 (upper-right)

        # Apply one step
        self.automaton.step()

        # Check result - should change to 'b' because neighbor exists
        self.assertEqual(self.automaton.get_cell(0, 0).state, "b")

    def test_conditional_rule_no_match(self) -> None:
        """Test conditional rule when condition is not met."""
        self.automaton.set_rules(["a[x] => b"])

        # Set up initial state - 'a' cell without 'x' neighbor
        self.automaton.set_cell(0, 0, "a")
        self.automaton.set_cell(1, -1, "y")  # Different neighbor

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

        with patch(
            "domain.hexidirect.rule_engine.random.choice",
            side_effect=lambda seq: seq[0],
        ):
            self.automaton.apply_random_rules(selections)

        self.assertEqual(self.automaton.get_cell(0, 0).state, "b")

    def test_rotation_when_source_directionless_branches(self) -> None:
        """a => b%2 with directionless source expands to 6 target variants; one is chosen deterministically for test."""
        # Explicitly craft a rule without source direction; expansion will create 6 target variants
        self.automaton.set_rules(["a => b%2"])
        self.automaton.set_cell(0, 0, "a", None)
        with patch(
            "domain.hexidirect.rule_engine.random.choice",
            side_effect=lambda seq: seq[0],
        ):
            self.automaton.step()
        # Deterministically first variant selected -> b1
        cell = self.automaton.get_cell(0, 0)
        self.assertEqual((cell.state, cell.direction), ("b", 1))

    def test_source_direction_exact_match(self) -> None:
        """'a3 => b' applies only to cells with direction 3."""
        self.automaton.set_rules(["a3 => b"])
        # a without direction should not match
        self.automaton.set_cell(0, 0, "a", None)
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "a")
        # a with different direction should not match
        self.automaton.set_cell(0, 1, "a", 2)
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 1).state, "a")
        # a with direction 3 should match
        self.automaton.set_cell(1, 0, "a", 3)
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(1, 0).state, "b")

    def test_source_direction_unspecified_means_directionless(self) -> None:
        """'a => b' applies only to directionless 'a' cells (direction None)."""
        self.automaton.set_rules(["a => b"])
        # directionless matches
        self.automaton.set_cell(0, 0, "a", None)
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "b")
        # a with direction should not match
        self.automaton.set_cell(0, 1, "a", 5)
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 1).state, "a")

    def test_source_direction_any_with_percent(self) -> None:
        """'a% => b' applies to 'a' with any specified direction (not None)."""
        self.automaton.set_rules(["a% => b"])
        # None should NOT match
        self.automaton.set_cell(0, 0, "a", None)
        # Any direction should match
        self.automaton.set_cell(1, 0, "a", 1)
        self.automaton.set_cell(1, 1, "a", 6)
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "a")
        self.assertEqual(self.automaton.get_cell(1, 0).state, "b")
        self.assertEqual(self.automaton.get_cell(1, 1).state, "b")

    def test_multi_condition_parsing(self) -> None:
        """Rules may contain multiple condition blocks and OR expressions."""
        rule = HexRule("a[b][c] => d")
        self.assertEqual(len(rule.conditions), 2)
        self.assertEqual(rule.conditions[0][0].state, "b")
        self.assertEqual(rule.conditions[1][0].state, "c")

        rule_or = HexRule("a[b|c] => d")
        self.assertEqual(len(rule_or.conditions), 1)
        states = {opt.state for opt in rule_or.conditions[0]}
        self.assertEqual(states, {"b", "c"})

    def test_multi_condition_application(self) -> None:
        """Rule requires two specific neighbors and supports OR."""
        self.automaton.clear()
        self.automaton.set_rules(["a[b][c] => d"])
        self.automaton.set_cell(0, 0, "a")
        self.automaton.set_cell(1, 0, "b")
        self.automaton.set_cell(0, 1, "c")
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "d")

        self.automaton.clear()
        self.automaton.set_rules(["a[b|c] => d"])
        self.automaton.set_cell(0, 0, "a")
        self.automaton.set_cell(1, 0, "c")
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "d")

    def test_multi_condition_requires_distinct_neighbors(self) -> None:
        """Repeated conditions consume distinct neighbor slots."""
        self.automaton.clear()
        self.automaton.set_rules(["a[b][b] => d"])
        self.automaton.set_cell(0, 0, "a")
        self.automaton.set_cell(1, 0, "b")
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "a")
        self.automaton.set_cell(0, 1, "b")
        self.automaton.step()
        self.assertEqual(self.automaton.get_cell(0, 0).state, "d")

    def test_repetition_syntax(self) -> None:
        """[state]N repeats the condition block N times."""
        rules = self.automaton._expand_macros("_[a]3[_]3 => a")
        self.assertEqual(rules, ["_[a][a][a][_][_][_] => a"])


if __name__ == "__main__":
    unittest.main()
