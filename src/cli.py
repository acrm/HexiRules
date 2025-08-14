#!/usr/bin/env python3
"""Command-line interface for HexiRules (HexiDirect-only).

Provides an interactive shell for configuring and running the hex automaton.
"""

from __future__ import annotations

import argparse
import cmd
from typing import Iterable, Sequence

from hex_rules import HexAutomaton
from version import __version__


def grid_to_ascii(automaton: HexAutomaton, radius: int = 3) -> str:
    """Return the current grid state as ASCII art (● for non-empty cells)."""
    lines = []
    for r in range(-radius, radius + 1):
        spaces = " " * abs(r)
        line = []
        for q in range(-radius, radius + 1):
            if abs(q + r) <= radius:
                cell = automaton.get_cell(q, r)
                line.append("●" if cell.state != "_" else "○")
        lines.append(spaces + " ".join(line))
    return "\n".join(lines)


def print_grid(automaton: HexAutomaton, radius: int = 3) -> None:
    """Print the grid to standard output."""
    print(grid_to_ascii(automaton, radius))


class HexCLI(cmd.Cmd):
    """Interactive command shell for the automaton."""

    intro = f"HexiRules v{__version__}. Type 'help' for commands."
    prompt = "hex> "

    def __init__(self, automaton: HexAutomaton, stdout=None):
        super().__init__(stdout=stdout)
        self.automaton = automaton

    # --- Commands -------------------------------------------------
    def do_rule(self, arg: str) -> None:
        """rule [RULE] - set or show the current HexiDirect rules."""
        rule = arg.strip()
        if rule:
            rules = [r.strip() for r in rule.replace(";", "\n").split("\n") if r.strip()]
            self.automaton.set_rules(rules)
            print("Rules set.", file=self.stdout)
        else:
            self.do_rules(arg)

    def do_rules(self, arg: str) -> None:  # noqa: D401 - simple wrapper
        """rules - list applied rules."""
        for rule in self.automaton.rules:
            print(rule.rule_str, file=self.stdout)

    def do_set(self, arg: str) -> None:
        """set Q R STATE - set hex cell state.

        STATE can be '_', 'a', 'b', ... or legacy '1' (alias for 'a') and '0' (alias for '_').
        """
        parts = arg.split()
        if len(parts) != 3:
            print("Usage: set Q R STATE", file=self.stdout)
            return
        q, r, state = parts
        if state == "1":
            state = "a"
        if state == "0":
            state = "_"
        self.automaton.set_cell(int(q), int(r), state)
        print(f"Cell {q} {r} set to {state}", file=self.stdout)

    def do_toggle(self, arg: str) -> None:
        """toggle Q R - toggle a cell between '_' and 'a'."""
        parts = arg.split()
        if len(parts) != 2:
            print("Usage: toggle Q R", file=self.stdout)
            return
        q, r = map(int, parts)
        cell = self.automaton.get_cell(q, r)
        new_state = "_" if cell.state != "_" else "a"
        self.automaton.set_cell(q, r, new_state, cell.direction)
        print(f"Toggled {q} {r}", file=self.stdout)

    def do_query(self, arg: str) -> None:
        """query Q R - get cell state ('1' if not '_' else '0')."""
        parts = arg.split()
        if len(parts) != 2:
            print("Usage: query Q R", file=self.stdout)
            return
        q, r = map(int, parts)
        cell = self.automaton.get_cell(q, r)
        print("1" if cell.state != "_" else "0", file=self.stdout)

    def do_summary(self, arg: str) -> None:  # noqa: D401 - simple wrapper
        """summary - show number of non-empty cells."""
        print(f"Alive cells: {len(self.automaton.get_active_cells())}", file=self.stdout)

    def do_cells(self, arg: str) -> None:  # noqa: D401 - simple wrapper
        """cells - list coordinates of non-empty cells."""
        for q, r in sorted(self.automaton.get_active_cells()):
            print(f"{q} {r}", file=self.stdout)

    def do_grid(self, arg: str) -> None:
        """grid [RADIUS] - print grid state."""
        radius = int(arg.strip()) if arg.strip() else self.automaton.radius
        print(grid_to_ascii(self.automaton, radius), file=self.stdout)

    def do_step(self, arg: str) -> None:
        """step [N] - advance N generations."""
        n = int(arg.strip()) if arg.strip() else 1
        for _ in range(n):
            self.automaton.step()
        print(f"Stepped {n}", file=self.stdout)

    def do_clear(self, arg: str) -> None:  # noqa: D401 - simple wrapper
        """clear - remove all cells."""
        self.automaton.clear()
        print("Cleared", file=self.stdout)

    def do_exit(self, arg: str) -> bool:  # noqa: D401 - simple wrapper
        """exit - quit the shell."""
        return True

    do_quit = do_exit
    do_EOF = do_exit


def main(argv: Sequence[str] | None = None) -> None:
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(
        description=f"HexiRules v{__version__} - Hexagonal Cellular Automaton CLI (HexiDirect)"
    )
    # Default to directionless HexiDirect B3/S23 equivalent
    default_rules = (
        "_[a][a][a][_][_][_] => a; "
        "a[a][a][_][_][_][_] | a[a][a][a][_][_][_] => a; "
        "a[_][_][_][_][_][_] | a[a][_][_][_][_][_] | a[a][a][a][a][_][_] | a[a][a][a][a][a][_] | a[a][a][a][a][a][a] => _"
    )
    parser.add_argument("--rule", default=default_rules, help="HexiDirect rules (use ';' or newlines to separate)")
    parser.add_argument("--radius", type=int, default=3, help="Grid radius")
    args = parser.parse_args(argv)

    automaton = HexAutomaton(radius=args.radius)
    rules = [r.strip() for r in str(args.rule).replace(";", "\n").split("\n") if r.strip()]
    if rules:
        automaton.set_rules(rules)
    HexCLI(automaton).cmdloop()


if __name__ == "__main__":
    main()
