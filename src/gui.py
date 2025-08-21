#!/usr/bin/env python3
"""Tk grid renderer with ASCII control panel."""

import tkinter as tk
from typing import Any, Dict, List, Tuple, Optional
import math
import threading

from domain.hexidirect.rule_engine import HexAutomaton
from application.world_service import WorldService
from ascii_ui import AsciiControlPanel

# Configuration
DEFAULT_RADIUS = 8
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Available symbolic states for HexiDirect mode
SYMBOLIC_STATES = ["_", "a", "b", "c", "x", "t", "y", "z"]
STATE_COLORS = {
    "_": "white",
    "a": "#ff6b6b",  # Red
    "b": "#4ecdc4",  # Teal
    "c": "#45b7d1",  # Blue
    "x": "#96ceb4",  # Green
    "t": "#ffeaa7",  # Yellow
    "y": "#dda0dd",  # Plum
    "z": "#98d8c8",  # Mint
}


class HexiRulesGUI:
    """Main GUI class for HexiRules application."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("HexiRules - Hexagonal Cellular Automaton")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.hex_items = {}

        # Per-canvas dynamic layout
        self.canvas = None
        self.canvas_center = (0, 0)
        self.cell_size = 15.0

        # Worlds management delegated to controller
        self.controller = WorldService()
        self.ascii_panel = AsciiControlPanel(self.controller, self.update_display)

        self.create_widgets()
        self._init_default_world()
        self.update_display()

    # -------- World helpers --------
    def _init_default_world(self) -> None:
        self._create_world(
            "World 1",
            DEFAULT_RADIUS,
            True,
            "t[-a] => t%\n_[t.] => a\nt%[a] => t",
        )
        self._select_world("World 1")

    def _create_world(
        self, name: str, radius: int, is_hex: bool, rules_text: str
    ) -> None:
        # Delegate world creation to controller
        self.controller.create_world(name, radius, is_hex, rules_text)
        # Update world list UI
        if hasattr(self, "world_list"):
            if name not in self.world_list.get(0, tk.END):
                self.world_list.insert(tk.END, name)

    def _select_world(self, name: str) -> None:
        if name not in self.controller.worlds:
            return
        self.controller.select_world(name)
        self.update_display()

    def _get_current_world(self) -> Dict[str, Any]:
        # Ask controller for current world
        try:
            return self.controller.get_current_world()
        except Exception:
            # Shouldn't happen after init, but guard by re-initializing
            self._init_default_world()
            return self.controller.get_current_world()

    # -------- UI construction --------
    def create_widgets(self) -> None:
        """Create canvas only."""
        self.create_grid_panel(self.root)

    def create_grid_panel(self, parent) -> None:
        """Create the grid panel."""
        grid_frame = tk.Frame(parent, bg="lightgray")
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for hexagonal grid - fills available space, resizes with window
        self.canvas = tk.Canvas(grid_frame, bg="lightgray", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse and resize events
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    # -------- Scaling helpers --------
    def on_canvas_resize(self, event: Any) -> None:
        # Recompute layout when canvas resizes
        self._compute_layout()
        self.update_display()

    def _compute_layout(self) -> None:
        # Compute cell size to fit the grid for current world's radius
        world = self._get_current_world()
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        pad = 10
        # Total width = s * (3R + 2), Total height = s * (3*sqrt(3)*R + 2)
        if R <= 0:
            s_w = (width - pad) / 2.0
            s_h = (height - pad) / 2.0
        else:
            s_w = (width - pad) / (3.0 * R + 2.0)
            s_h = (height - pad) / (3.0 * math.sqrt(3) * R + 2.0)
        self.cell_size = max(2.0, min(s_w, s_h))
        self.canvas_center = (width // 2, height // 2)

    # -------- Coordinate transforms --------
    def get_hex_coordinates(self, canvas_x: int, canvas_y: int) -> Tuple[int, int]:
        """Convert canvas coordinates to hex grid coordinates."""
        cx, cy = self.canvas_center
        x = (canvas_x - cx) / (self.cell_size * 1.5)
        y = (canvas_y - cy) / (self.cell_size * math.sqrt(3))
        q = round(x)
        r = round(y - x / 2)
        return int(q), int(r)

    def get_canvas_position(self, q: int, r: int) -> Tuple[float, float]:
        """Convert hex coordinates to canvas position."""
        cx, cy = self.canvas_center
        x = cx + q * self.cell_size * 1.5
        y = cy + (r + q / 2) * self.cell_size * math.sqrt(3)
        return x, y

    # -------- Drawing --------
    def draw_hex(
        self,
        x: float,
        y: float,
        color: str,
        state: str = "",
        direction: Optional[int] = None,
    ) -> int:
        """Draw a hexagon at the given position with state and direction."""
        points: List[float] = []
        for i in range(6):
            angle = i * math.pi / 3
            px = x + self.cell_size * math.cos(angle)
            py = y + self.cell_size * math.sin(angle)
            points.extend([px, py])

        hex_id = self.canvas.create_polygon(
            points, fill=color, outline="black", width=1
        )

        world = self._get_current_world()
        if state and state != "_":
            label = f"{state}{direction}" if direction is not None else state
            self.canvas.create_text(x, y, text=label, font=("Arial", 8, "bold"))
        if direction is not None:
            dot_distance = self.cell_size * 0.8
            # Engine neighbor order is [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
            # which corresponds to angles 0°, 60°, 120°, 180°, 240°, 300°.
            # Map direction 1 -> 0° and add 60° CCW per step.
            angle_degrees = (direction - 1) * 60
            ang = math.radians(angle_degrees)
            dx = dot_distance * math.cos(ang)
            dy = -dot_distance * math.sin(ang)
            self.canvas.create_oval(
                x + dx - 3,
                y + dy - 3,
                x + dx + 3,
                y + dy + 3,
                fill="red",
                outline="darkred",
            )

        return int(hex_id)

    def update_display(self) -> None:
        """Update the visual display."""
        if not hasattr(self, "canvas"):
            return
        # Ensure layout is initialized
        self._compute_layout()
        self.canvas.delete("all")
        self.hex_items.clear()

        world = self._get_current_world()
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        automaton = world.hex

        for q in range(-R, R + 1):
            for r in range(-R, R + 1):
                if abs(q + r) <= R:
                    x, y = self.get_canvas_position(q, r)
                    cell = automaton.get_cell(q, r)
                    color = STATE_COLORS.get(cell.state, "gray")
                    hex_id = self.draw_hex(x, y, color, cell.state, cell.direction)
                    self.hex_items[(q, r)] = hex_id

    def on_left_click(self, event: Any) -> None:
        q, r = self.get_hex_coordinates(event.x, event.y)
        world = self._get_current_world()
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            current_cell = world.hex.get_cell(q, r)
            current_state = current_cell.state
            try:
                current_idx = SYMBOLIC_STATES.index(current_state)
                next_idx = (current_idx + 1) % len(SYMBOLIC_STATES)
            except ValueError:
                next_idx = 1
            new_state = SYMBOLIC_STATES[next_idx]
            world.hex.set_cell(q, r, new_state, current_cell.direction)
            self.update_display()

    def on_right_click(self, event: Any) -> None:
        world = self._get_current_world()
        q, r = self.get_hex_coordinates(event.x, event.y)
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            current_cell = world.hex.get_cell(q, r)
            if current_cell.state != "_":
                current_dir = current_cell.direction
                new_dir = (
                    1
                    if current_dir is None
                    else (None if current_dir == 6 else current_dir + 1)
                )
                world.hex.set_cell(q, r, current_cell.state, new_dir)
                self.update_display()

    def on_middle_click(self, event: Any) -> None:
        world = self._get_current_world()
        q, r = self.get_hex_coordinates(event.x, event.y)
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            world.hex.set_cell(q, r, "_")
            self.update_display()

    def step(self) -> None:
        world = self.controller.get_current_world()
        self.controller.step(world.rules_text)
        self.update_display()

    def clear(self) -> None:
        self.controller.clear()
        self.update_display()

    def randomize(self) -> None:
        self.controller.randomize(SYMBOLIC_STATES, p=0.3)
        self.update_display()

    def run(self) -> None:
        threading.Thread(target=self.ascii_panel.run, daemon=True).start()
        self.root.mainloop()


def create_gui() -> HexiRulesGUI:
    """Create and return a new HexiRules GUI instance."""
    return HexiRulesGUI()
