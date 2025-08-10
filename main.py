#!/usr/bin/env python3
"""HexiRules launcher that forwards to src/.

Keeps existing debug/run setups that point to top-level main.py working after the src/ reorg.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
	sys.path.insert(0, SRC)

from gui import create_gui  # type: ignore


def main() -> None:
	gui = create_gui()
	gui.run()


if __name__ == "__main__":
	main()

