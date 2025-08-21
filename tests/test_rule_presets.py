import unittest

from domain.hexidirect.rule_engine import HexAutomaton


class TestRulePresets(unittest.TestCase):
    def test_b3s23_preset(self) -> None:
        automaton = HexAutomaton(radius=2)
        automaton.set_rules(["b3s23"])
        self.assertEqual(len(automaton.rules), 4)

        # Birth: empty cell with exactly three neighbors becomes alive
        automaton.set_cell(0, 0, "_")
        automaton.set_cell(1, 0, "a")
        automaton.set_cell(0, 1, "a")
        automaton.set_cell(-1, 1, "a")
        automaton.step()
        self.assertEqual(automaton.get_cell(0, 0).state, "a")

        # Survival: live cell with two neighbors stays alive
        automaton.clear()
        automaton.set_cell(0, 0, "a")
        automaton.set_cell(1, 0, "a")
        automaton.set_cell(0, 1, "a")
        automaton.step()
        self.assertEqual(automaton.get_cell(0, 0).state, "a")

        # Death: live cell with one neighbor dies
        automaton.clear()
        automaton.set_cell(0, 0, "a")
        automaton.set_cell(1, 0, "a")
        automaton.step()
        self.assertEqual(automaton.get_cell(0, 0).state, "_")


if __name__ == "__main__":
    unittest.main()
