from __future__ import annotations

import tkinter as tk
from typing import Optional

from application.world_service import WorldService
from domain.constants import STATE_COLORS
from main import HexCanvas


def run_hexiscope(
    parent: tk.Widget,
    controller: Optional[WorldService] = None,
    radius: int | None = None,
) -> None:
    """Render the HexiScope (hex grid canvas) into the given parent widget."""
    controller = controller or WorldService()
    world = controller.get_current_world()
    r = radius if radius is not None else int(getattr(world, "radius", 8))

    helper = HexCanvas(parent, radius=r, cell_size=20)
    helper.canvas.config(bg="#3d033d", highlightthickness=0)
    helper.canvas.pack(anchor="center", expand=True, fill=tk.BOTH)

    # Initial draw
    canvas = helper.canvas
    canvas.delete("all")
    for (q, r_ax), (cx, cy) in helper.cells.items():
        cell = world.hex.get_cell(q, r_ax)
        color = "#111111" if cell.state == "_" else STATE_COLORS.get(cell.state, "#ffffff")
        pts = helper.polygon_corners(cx, cy)
        canvas.create_polygon(pts, fill=color, outline="#333333")
