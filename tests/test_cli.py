import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from automaton import Automaton
from cli import HexCLI


def run_cmd(cli: HexCLI, command: str) -> str:
    buffer = io.StringIO()
    cli.stdout = buffer
    cli.onecmd(command)
    return buffer.getvalue().strip()


class TestCLI(unittest.TestCase):
    def setUp(self) -> None:
        automaton = Automaton(radius=3, rule="B3/S23")
        self.cli = HexCLI(automaton, stdout=io.StringIO())

    def test_rule_management(self) -> None:
        run_cmd(self.cli, "rule B2/S3")
        output = run_cmd(self.cli, "rules")
        self.assertIn("B2/S3", output)

    def test_cell_operations_and_summary(self) -> None:
        run_cmd(self.cli, "set 0 0 1")
        run_cmd(self.cli, "set 1 0 1")
        run_cmd(self.cli, "set 0 1 1")
        query_output = run_cmd(self.cli, "query 0 0")
        self.assertEqual("1", query_output)
        cells_output = run_cmd(self.cli, "cells")
        self.assertIn("0 0", cells_output)
        summary_output = run_cmd(self.cli, "summary")
        self.assertIn("3", summary_output)
        grid_output = run_cmd(self.cli, "grid 1")
        self.assertIn("●", grid_output)

    def test_step_progression(self) -> None:
        run_cmd(self.cli, "set 0 0 1")
        run_cmd(self.cli, "step")
        summary_output = run_cmd(self.cli, "summary")
        self.assertIn("0", summary_output)


if __name__ == "__main__":
    unittest.main()
