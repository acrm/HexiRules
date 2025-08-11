#!/usr/bin/env python3
"""HexiRules launcher that forwards to src/.

Keeps existing debug/run setups that point to top-level main.py working after the
src/ reorg.
"""
import importlib
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

_spec = importlib.util.spec_from_file_location("src_main", os.path.join(SRC, "main.py"))
assert _spec and _spec.loader
_src_main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_src_main)
HexCanvas = _src_main.HexCanvas


def main() -> None:
    gui_mod = importlib.import_module("gui")
    gui = gui_mod.create_gui()
    gui.run()


if __name__ == "__main__":
    main()
