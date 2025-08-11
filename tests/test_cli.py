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

    def test_hex_rule_mode(self) -> None:
        cli = HexCLI(Automaton(radius=3, rule="a%=>_"), stdout=io.StringIO())
        rules_output = run_cmd(cli, "rules")
        self.assertIn("a1 => _", rules_output)
        run_cmd(cli, "set 0 0 1")
        self.assertEqual("1", run_cmd(cli, "query 0 0"))
        run_cmd(cli, "step")
        self.assertEqual("0", run_cmd(cli, "query 0 0"))


if __name__ == "__main__":
    unittest.main()
