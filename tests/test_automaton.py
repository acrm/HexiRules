import unittest
import unittest

from hex_rules import HexAutomaton


class TestHexAutomatonBasic(unittest.TestCase):
    def setUp(self) -> None:
        self.hex = HexAutomaton(radius=3)

    def test_rule_set_and_apply(self) -> None:
        self.hex.set_rules(["a => _"])
        self.hex.set_cell(0, 0, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "_")

    def test_b3s23_equivalence_birth(self) -> None:
        self.hex.set_rules(["B3/S23"])
        self.hex.set_cell(1, 0, "a")
        self.hex.set_cell(1, -1, "a")
        self.hex.set_cell(0, -1, "a")
        self.hex.step()
        self.assertEqual(self.hex.get_cell(0, 0).state, "a")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
