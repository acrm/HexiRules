import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from automaton import Automaton


class TestAutomaton(unittest.TestCase):
    def test_parse_rule(self):
        a = Automaton("B3/S23")
        self.assertEqual(a.birth, [3])
        self.assertEqual(a.survive, [2, 3])
        self.assertEqual(a.rule, "B3/S23")

    def test_single_cell_dies(self):
        a = Automaton()
        a.toggle_cell(0, 0)
        a.step()
        self.assertNotIn((0, 0), a.state)

    def test_triangle_survives(self):
        a = Automaton()
        a.toggle_cell(0, 0)
        a.toggle_cell(1, 0)
        a.toggle_cell(0, 1)
        a.step()
        self.assertIn((0, 0), a.state)
        self.assertIn((1, 0), a.state)
        self.assertIn((0, 1), a.state)

    def test_birth_on_three_neighbors(self):
        a = Automaton()
        a.toggle_cell(1, 0)
        a.toggle_cell(-1, 0)
        a.toggle_cell(0, 1)
        a.step()
        self.assertIn((0, 0), a.state)


if __name__ == "__main__":
    unittest.main()
