import unittest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.hex_rules import HexAutomaton


# Directionless HexiDirect rules implementing Conway B3/S23 on a hex grid
HEXIDIRECT_B3_S23 = [
    # Birth: exactly 3 neighbors alive
    "_[a][a][a][_][_][_] => a",
    # Survival: 2 or 3 neighbors alive
    "a[a][a][_][_][_][_] | a[a][a][a][_][_][_] => a",
    # Death: 0, 1, 4, 5, or 6 neighbors alive
    (
        "a[_][_][_][_][_][_] | "
        "a[a][_][_][_][_][_] | "
        "a[a][a][a][a][_][_] | "
        "a[a][a][a][a][a][_] | "
        "a[a][a][a][a][a][a] => _"
    ),
]


class TestHexiDirectB3S23(unittest.TestCase):
    def setUp(self) -> None:
        self.hex = HexAutomaton(radius=3)
        self.hex.set_rules(HEXIDIRECT_B3_S23)

    def test_birth_on_three_neighbors(self) -> None:
        # Neighbors around (0,0): (1,0), (1,-1), (0,-1), (-1,0), (-1,1), (0,1)
        self.hex.set_cell(1, 0, "a")
        self.hex.set_cell(1, -1, "a")
        self.hex.set_cell(0, -1, "a")
        # Center initially empty
        self.assertEqual(self.hex.get_cell(0, 0).state, "_")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "a")

    def test_survival_with_two_neighbors(self) -> None:
        # Center alive with exactly two neighbors
        self.hex.set_cell(0, 0, "a")
        self.hex.set_cell(1, 0, "a")
        self.hex.set_cell(1, -1, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "a")

    def test_survival_with_three_neighbors(self) -> None:
        # Center alive with exactly three neighbors
        self.hex.set_cell(0, 0, "a")
        self.hex.set_cell(1, 0, "a")
        self.hex.set_cell(1, -1, "a")
        self.hex.set_cell(0, -1, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "a")

    def test_death_with_one_neighbor(self) -> None:
        # Center alive with 1 neighbor -> death
        self.hex.set_cell(0, 0, "a")
        self.hex.set_cell(1, 0, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "_")

    def test_death_with_four_neighbors(self) -> None:
        # Center alive with 4 neighbors -> death
        self.hex.set_cell(0, 0, "a")
        self.hex.set_cell(1, 0, "a")
        self.hex.set_cell(1, -1, "a")
        self.hex.set_cell(0, -1, "a")
        self.hex.set_cell(-1, 0, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "_")

    def test_death_with_zero_neighbors(self) -> None:
        # Center alive with 0 neighbors -> death
        self.hex.set_cell(0, 0, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "_")

    def test_death_with_five_neighbors(self) -> None:
        # Center alive with 5 neighbors -> death
        self.hex.set_cell(0, 0, "a")
        self.hex.set_cell(1, 0, "a")
        self.hex.set_cell(1, -1, "a")
        self.hex.set_cell(0, -1, "a")
        self.hex.set_cell(-1, 0, "a")
        self.hex.set_cell(-1, 1, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "_")

    def test_death_with_six_neighbors(self) -> None:
        # Center alive with 6 neighbors -> death
        self.hex.set_cell(0, 0, "a")
        self.hex.set_cell(1, 0, "a")
        self.hex.set_cell(1, -1, "a")
        self.hex.set_cell(0, -1, "a")
        self.hex.set_cell(-1, 0, "a")
        self.hex.set_cell(-1, 1, "a")
        self.hex.set_cell(0, 1, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "_")


if __name__ == "__main__":
    unittest.main()
