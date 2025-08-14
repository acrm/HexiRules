import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.hex_rules import HexAutomaton

class TestHexAutomatonBasic(unittest.TestCase):
    def setUp(self) -> None:
        self.hex = HexAutomaton(radius=3)

    def test_rule_set_and_apply(self) -> None:
        # Simple rule: any 'a' becomes '_'
        self.hex.set_rules(["a => _"])
        self.hex.set_cell(0, 0, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "_")

    def test_b3s23_equivalence_birth(self) -> None:
        # Use directionless B3/S23 equivalent to birth a cell
        rules = [
            "_[a][a][a][_][_][_] => a",
            "a[a][a][_][_][_][_] | a[a][a][a][_][_][_] => a",
            (
                "a[_][_][_][_][_][_] | "
                "a[a][_][_][_][_][_] | "
                "a[a][a][a][a][_][_] | "
                "a[a][a][a][a][a][_] | "
                "a[a][a][a][a][a][a] => _"
            ),
        ]
        self.hex.set_rules(rules)
        self.hex.set_cell(1, 0, "a")
        self.hex.set_cell(1, -1, "a")
        self.hex.set_cell(0, -1, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "a")


if __name__ == "__main__":
    unittest.main()
