#!/usr/bin/env python3
"""Command-line interface for HexiRules.

Provides an interactive shell for configuring and running the automaton.
"""

from __future__ import annotations

import argparse
import cmd
from typing import Iterable, Sequence

from automaton import Automaton
from version import __version__


def grid_to_ascii(automaton: Automaton, radius: int = 3) -> str:
    """Return the current grid state as ASCII art."""
    lines = []
    for r in range(-radius, radius + 1):
        spaces = " " * abs(r)
        line = []
        for q in range(-radius, radius + 1):
            if abs(q + r) <= radius:
                line.append("●" if (q, r) in automaton.state else "○")
        lines.append(spaces + " ".join(line))
    return "\n".join(lines)


def print_grid(automaton: Automaton, radius: int = 3) -> None:
    """Print the grid to standard output."""
    print(grid_to_ascii(automaton, radius))


class HexCLI(cmd.Cmd):
    """Interactive command shell for the automaton."""

    intro = f"HexiRules v{__version__}. Type 'help' for commands."
    prompt = "hex> "

    def __init__(self, automaton: Automaton, stdout=None):
        super().__init__(stdout=stdout)
        self.automaton = automaton

    # --- Commands -------------------------------------------------
    def do_rule(self, arg: str) -> None:
        """rule [RULE] - set or show the current rule."""
        rule = arg.strip()
        if rule:
            self.automaton.set_rule(rule)
            print(f"Rule set to {self.automaton.rule}", file=self.stdout)
        else:
            self.do_rules(arg)

    def do_rules(self, arg: str) -> None:  # noqa: D401 - simple wrapper
        """rules - list applied rules."""
        if self.automaton.use_hex_rules and self.automaton.hex_automaton:
            for rule in self.automaton.hex_automaton.rules:
                print(rule.rule_str, file=self.stdout)
        else:
            print(self.automaton.rule, file=self.stdout)

    def do_set(self, arg: str) -> None:
        """set Q R STATE - set cell state (1 alive, 0 dead)."""
        parts = arg.split()
        if len(parts) != 3:
            print("Usage: set Q R STATE", file=self.stdout)
            return
        q, r, state = parts
        self.automaton.set_cell_state(int(q), int(r), state)
        print(f"Cell {q} {r} set to {state}", file=self.stdout)

    def do_toggle(self, arg: str) -> None:
        """toggle Q R - toggle a cell."""
        parts = arg.split()
        if len(parts) != 2:
            print("Usage: toggle Q R", file=self.stdout)
            return
        q, r = map(int, parts)
        self.automaton.toggle_cell(q, r)
        print(f"Toggled {q} {r}", file=self.stdout)

    def do_query(self, arg: str) -> None:
        """query Q R - get cell state."""
        parts = arg.split()
        if len(parts) != 2:
            print("Usage: query Q R", file=self.stdout)
            return
        q, r = map(int, parts)
        print(self.automaton.get_cell_state(q, r), file=self.stdout)

    def do_summary(self, arg: str) -> None:  # noqa: D401 - simple wrapper
        """summary - show number of alive cells."""
        print(f"Alive cells: {len(self.automaton.state)}", file=self.stdout)

    def do_cells(self, arg: str) -> None:  # noqa: D401 - simple wrapper
        """cells - list coordinates of alive cells."""
        for q, r in sorted(self.automaton.state):
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
        description=f"HexiRules v{__version__} - Hexagonal Cellular Automaton CLI"
    )
    parser.add_argument("--rule", default="B3/S23", help="CA rule (e.g., B3/S23)")
    parser.add_argument("--radius", type=int, default=3, help="Grid radius")
    args = parser.parse_args(argv)

    automaton = Automaton(radius=args.radius, rule=args.rule)
    HexCLI(automaton).cmdloop()


if __name__ == "__main__":
    main()
