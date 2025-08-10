#!/usr/bin/env python3
"""
Command-line interface for HexiRules.
Provides text-based interaction with the hexagonal cellular automaton.
"""

import argparse
import time
from automaton import Automaton
from version import __version__


def print_grid(automaton: Automaton, radius: int = 3) -> None:
    """Print the current state of the automaton as text."""
    print("\nCurrent State:")
    for r in range(-radius, radius + 1):
        spaces = " " * abs(r)
        line = []
        for q in range(-radius, radius + 1):
            if abs(q + r) <= radius:
                if (q, r) in automaton.state:
                    line.append("●")
                else:
                    line.append("○")
        print(spaces + " ".join(line))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"HexiRules v{__version__} - Hexagonal Cellular Automaton CLI"
    )
    parser.add_argument(
        "--version", action="version", version=f"HexiRules {__version__}"
    )
    parser.add_argument("--rule", default="B3/S23", help="CA rule (e.g., B3/S23)")
    parser.add_argument(
        "--steps", type=int, default=10, help="Number of steps to simulate"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5, help="Delay between steps (seconds)"
    )
    parser.add_argument("--radius", type=int, default=3, help="Grid radius")

    args = parser.parse_args()

    automaton = Automaton(args.rule)

    # Set up initial pattern (simple test pattern)
    automaton.toggle_cell(0, 0)
    automaton.toggle_cell(1, 0)
    automaton.toggle_cell(0, 1)

    print(f"HexiRules v{__version__} CLI - Rule: {args.rule}")
    print(f"Simulating {args.steps} steps with {args.delay}s delay")

    print_grid(automaton, args.radius)

    for step in range(args.steps):
        time.sleep(args.delay)
        automaton.step()
        print(f"\n--- Step {step + 1} ---")
        print_grid(automaton, args.radius)

        if not automaton.state:
            print("All cells died - ending simulation")
            break


if __name__ == "__main__":
    main()
