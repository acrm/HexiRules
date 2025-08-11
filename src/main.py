#!/usr/bin/env python3
"""
HexiRules - Hexagonal Cellular Automaton

Main entry point for the HexiRules application.
Supports both Conway-style totalistic rules and HexiDirect symbolic rules.

Also exposes a minimal HexCanvas helper used by geometry-focused tests.
"""

import importlib
import math
from typing import Dict, Tuple, List

try:
    import tkinter as tk  # Only needed when tests instantiate the canvas
except Exception:  # pragma: no cover - allow headless import
    tk = None  # type: ignore[assignment]


class HexCanvas:
    """A lightweight hex grid canvas providing geometry helpers for tests.

    This class is intentionally minimal and independent from the main GUI.
    Tests use it to validate coordinate conversions and hex polygon math.
    """

    def __init__(self, root: tk.Tk, radius: int = 3, cell_size: int = 20) -> None:
        if tk is None:
            raise RuntimeError("Tkinter not available")
        self.root = root
        self.radius = radius
        self.cell_size = cell_size

        # Compute a canvas size that safely fits a hex grid of the given radius
        grid_w = int((3 * self.cell_size / 2) * (2 * radius) + 2 * self.cell_size + 20)
        grid_h = int((math.sqrt(3) * self.cell_size) * (2 * radius + 1) + 20)
        self.center_x = grid_w // 2
        self.center_y = grid_h // 2

        self.canvas = tk.Canvas(root, width=grid_w, height=grid_h)

        # Precompute cell centers for axial coordinates within the radius
        self.cells: Dict[Tuple[int, int], Tuple[int, int]] = {}
        for q in range(-radius, radius + 1):
            r_min = max(-radius, -q - radius)
            r_max = min(radius, -q + radius)
            for r in range(r_min, r_max + 1):
                x, y = self.axial_to_pixel(q, r)
                self.cells[(q, r)] = (x, y)

    def axial_to_pixel(self, q: int, r: int) -> Tuple[int, int]:
        """Convert axial (q, r) to pixel coordinates (pointy-top orientation)."""
        x = self.center_x + int(round(self.cell_size * (3 / 2) * q))
        y = self.center_y + int(round(self.cell_size * math.sqrt(3) * (r + q / 2)))
        return x, y

    def polygon_corners(self, cx: int, cy: int) -> List[int]:
        """Return the 6-point polygon around (cx, cy) as a flat list of 12 ints."""
        pts: List[int] = []
        # pointy-top hexagon: start at -30 degrees and step by 60 degrees
        for i in range(6):
            angle_rad = math.radians(60 * i - 30)
            x = cx + self.cell_size * math.cos(angle_rad)
            y = cy + self.cell_size * math.sin(angle_rad)
            pts.extend([int(round(x)), int(round(y))])
        return pts


def main() -> None:
    """Main entry point for HexiRules."""
    gui_mod = importlib.import_module("gui")
    gui = gui_mod.create_gui()
    gui.run()


if __name__ == "__main__":
    main()
