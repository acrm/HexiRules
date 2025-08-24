#!/usr/bin/env python3
"""Tk grid renderer with ASCII control panel."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Tuple, Optional
import math
import threading
import time

from domain.hexidirect.rule_engine import HexAutomaton
from application.world_service import WorldService
from ascii_ui import AsciiUILayout, SelectionState
from main import HexCanvas

# Configuration
DEFAULT_RADIUS = 8
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
ASCII_PANEL_WIDTH = 800  # Width for ASCII panel in pixels (to fit 80 chars)

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
        self.root.config(bg="#3d033d")  # Set application background
        self.root.config(cursor="none")  # Hide cursor

        # Selection state for ASCII panel
        self.selection = SelectionState(mode="top")

        # Bind hotkeys for ASCII panel selection and quit
        self.root.bind("<Escape>", self._on_escape)
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        for key, frame_id in [("w", "worlds"), ("r", "rules"), ("h", "history"), ("l", "logs")]:
            self.root.bind(key, lambda e, fid=frame_id: self._select_frame(fid))
            self.root.bind(key.upper(), lambda e, fid=frame_id: self._select_frame(fid))
        self.root.focus_set()  # Ensure root can receive key events

        self.hex_items = {}

        # Per-canvas dynamic layout
        self.canvas = None
        self.canvas_center = (0, 0)
        # Controller and ASCII panel widgets
        self.controller = WorldService()

        # ASCII panel frame
        self.ascii_frame = ttk.Frame(self.root)
        self.ascii_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        # Fixed-size monospace text widget: 81x51 characters
        self.ascii_text = tk.Text(
            self.ascii_frame,
            width=81,
            height=51,
            wrap="none",
            font=("Courier", 10),
            padx=2,
            pady=2,
            bd=0,
        )
        # Dark background for ASCII panel
        self.ascii_text.config(bg="#3d033d", fg="#ffffff", insertbackground="#ffffff")
        self.ascii_text.pack(side=tk.TOP)
        # Prevent scrolling inside the control panel
        self.ascii_text.bind("<MouseWheel>", lambda e: "break")
        self.ascii_text.bind("<Button-4>", lambda e: "break")
        self.ascii_text.bind("<Button-5>", lambda e: "break")

    # Command entry below the ASCII panel
        self.command_entry = ttk.Entry(self.ascii_frame, width=80)
        self.command_entry.pack(side=tk.TOP, pady=(0, 0))
        self.command_entry.bind("<Return>", self.on_command_enter)

        # Configure basic tags (colors can be customized further)
        self.ascii_text.tag_config("border", foreground="#cccccc")
        self.ascii_text.tag_config("title", foreground="#ffffff")
        self.ascii_text.tag_config("status", foreground="#d0d0d0")
        self.ascii_text.tag_config("section_header", foreground="#a0a0ff")
        self.ascii_text.tag_config(
            "selected_item", background="#ffffff", foreground="#000000"
        )
        self.ascii_text.tag_config("history_line", foreground="#88ff88")
        self.ascii_text.tag_config("log_line", foreground="#ffff88")
        self.ascii_text.tag_config("command_border", foreground="#8888ff")
        self.ascii_text.tag_config("command_prompt", foreground="#ffffff")
        self.ascii_text.tag_config("normal", foreground="#ffffff")
        # New tags used by ascii_ui renderer
        self.ascii_text.tag_config("hotkey", foreground="#ffff00")
        self.ascii_text.tag_config("border_sel", foreground="#ffff00")

        # Initial render
        # Right-side area: grid filling the whole space
        self.right_frame = tk.Frame(self.root, bg="#3d033d")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create hex grid canvas using HexCanvas helper
        try:
            world = self.controller.get_current_world()
            radius = int(getattr(world, "radius", DEFAULT_RADIUS))
        except Exception:
            radius = DEFAULT_RADIUS

        # cell size tuned to fit typical window; adjustable
        self.hex_canvas_helper = HexCanvas(self.root, radius=radius, cell_size=20)
        # Dark background for grid - place canvas directly in right frame
        self.hex_canvas_helper.canvas.config(bg="#3d033d", highlightthickness=0)

        # Center the canvas in the right frame instead of expanding it
        self.hex_canvas_helper.canvas.pack(
            in_=self.right_frame, anchor="center", expand=True
        )

        # Track selection - start with center cell selected
        self.selected_cell = (0, 0)

        # Bind canvas events
        self.hex_canvas_helper.canvas.bind("<Button-1>", self._on_canvas_click)
        self.hex_canvas_helper.canvas.bind("<Motion>", self._on_canvas_motion)

        # Initial render of both panels
        self.update_display()
        self.update_ascii_panel()

    def _insert_colored_text(self, text: str, tag: str) -> None:
        """Insert colored text without newline."""
        self.ascii_text.insert(tk.END, text, tag)

    def _insert_colored_line(self, text: str, tag: str) -> None:
        """Insert colored text with newline."""
        self.ascii_text.insert(tk.END, text + "\n", tag)

    def on_command_enter(self, event) -> None:
        """Handle command entry."""
        command = self.command_entry.get().strip()
        if not command:
            return

        # Clear the entry field
        self.command_entry.delete(0, tk.END)

        # Process the command
        self.execute_command(command)

        # Update displays
        self.update_display()
        self.update_ascii_panel()

    def execute_command(self, command: str) -> None:
        """Execute a command from the ASCII panel."""
        cmd = command.strip().lower()
        if not cmd:
            return

        world = self._get_current_world()

        if cmd == "s" or cmd == "step":
            self.step()
        elif cmd == "c" or cmd == "clear":
            self.clear()
        elif cmd == "r" or cmd == "randomize":
            self.randomize()
        elif cmd == "q" or cmd == "quit":
            self.root.quit()
        elif cmd.startswith("rule "):
            # Set new rules
            rule_text = command[5:].strip()
            world.rules_text = rule_text
        else:
            # Show help or unknown command
            pass

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
            self.update_ascii_panel()

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
                self.update_ascii_panel()

    def on_middle_click(self, event: Any) -> None:
        world = self._get_current_world()
        q, r = self.get_hex_coordinates(event.x, event.y)
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            world.hex.set_cell(q, r, "_")
            self.update_display()
            self.update_ascii_panel()

    def step(self) -> None:
        world = self.controller.get_current_world()
        self.controller.step(world.rules_text)
        self.update_display()
        self.update_ascii_panel()

    def clear(self) -> None:
        self.controller.clear()
        self.update_display()
        self.update_ascii_panel()

    def randomize(self) -> None:
        self.controller.randomize(SYMBOLIC_STATES, p=0.3)
        self.update_display()
        self.update_ascii_panel()

    def run(self) -> None:
        """Start the GUI application."""
        self.root.mainloop()

    def update_ascii_panel(self) -> None:
        """Render the ASCII UI using AsciiUILayout and apply tags precisely."""
        try:
            # Compose selected info for full-width frame above command line
            selected_info = None
            if self.selected_cell:
                q, r = self.selected_cell
                try:
                    world = self._get_current_world()
                    cell = world.hex.get_cell(q, r)
                    dir_text = str(cell.direction) if cell.direction is not None else "-"
                    selected_info = f"Selected: ({q},{r}) state={cell.state} dir={dir_text}"
                except Exception:
                    selected_info = f"Selected: ({q},{r})"

            layout = AsciiUILayout(self.controller, selection=self.selection, selected_info=selected_info)
            lines, tags = layout.render()
        except Exception:
            # Fail-safe: render empty grid (81x51)
            lines = [" " * 81 for _ in range(51)]
            tags = [[] for _ in range(51)]

        # Insert into text widget
        self.ascii_text.config(state=tk.NORMAL)
        self.ascii_text.delete("1.0", tk.END)

        for line in lines:
            # Each line already exactly 80 chars
            self.ascii_text.insert(tk.END, line + "\n")

        # Apply tags (line-based indices: lines start at 1)
        for i, line_tags in enumerate(tags):
            line_no = i + 1
            width = len(lines[i]) if i < len(lines) else 81
            for start, end, tag in line_tags:
                # Clamp to valid range for 81-wide surface
                s = max(0, min(width - 1, start))
                e = max(0, min(width, end))
                try:
                    self.ascii_text.tag_add(tag, f"{line_no}.{s}", f"{line_no}.{e}")
                except Exception:
                    # Ignore malformed tag ranges
                    pass

        self.ascii_text.config(state=tk.DISABLED)

    # --- Grid rendering and selection ---------------------------------
    def _get_current_world(self):
        return self.controller.get_current_world()

    def update_display(self) -> None:
        """Render the hex grid onto the canvas using world data."""
        try:
            world = self._get_current_world()
        except Exception:
            return

        canvas = self.hex_canvas_helper.canvas
        # clear previous drawings
        canvas.delete("all")

        # Draw each cell
        for (q, r), (cx, cy) in self.hex_canvas_helper.cells.items():
            cell = world.hex.get_cell(q, r)
            # background for empty cells: slightly darker than panel
            color = (
                "#111111"
                if cell.state == "_"
                else STATE_COLORS.get(cell.state, "#ffffff")
            )
            pts = self.hex_canvas_helper.polygon_corners(cx, cy)
            tag = f"cell_{q}_{r}"
            canvas.create_polygon(pts, fill=color, outline="#333333", tags=(tag,))
            # direction marker: a small dot when direction present
            if getattr(cell, "direction", None):
                canvas.create_oval(
                    cx - 3, cy - 3, cx + 3, cy + 3, fill="#ffff00", outline=""
                )

        # highlight selected cell
        if self.selected_cell:
            q, r = self.selected_cell
            if (q, r) in self.hex_canvas_helper.cells:
                cx, cy = self.hex_canvas_helper.cells[(q, r)]
                pts = self.hex_canvas_helper.polygon_corners(cx, cy)
                canvas.create_polygon(pts, fill="", outline="#ffffff", width=2)

    # Selected info now rendered inside ASCII panel; no external label below it

    def _on_canvas_click(self, event: Any) -> None:
        q, r = self.get_hex_coordinates(event.x, event.y)
        try:
            world = self._get_current_world()
        except Exception:
            return
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            # set selection and update displays
            self.selected_cell = (q, r)
            self.update_display()
            self.update_ascii_panel()
        # If outside grid, keep previous selection

    def _on_canvas_motion(self, event: Any) -> None:
        """Track mouse motion and update selection if within grid."""
        q, r = self.get_hex_coordinates(event.x, event.y)
        try:
            world = self._get_current_world()
        except Exception:
            return
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            # Update selection only if within grid
            if self.selected_cell != (q, r):
                self.selected_cell = (q, r)
                self.update_display()
                self.update_ascii_panel()

    def get_hex_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """Return axial coordinates nearest to pixel (x,y) on the hex canvas."""
        # Find nearest precomputed center
        best = None
        best_dist = float("inf")
        for (q, r), (cx, cy) in self.hex_canvas_helper.cells.items():
            dx = cx - x
            dy = cy - y
            d = dx * dx + dy * dy
            if d < best_dist:
                best_dist = d
                best = (q, r)
        if best is None:
            return (0, 0)
        return best

    # --- ASCII panel selection handlers ---
    def _select_frame(self, frame_id: str) -> None:
        self.selection = SelectionState(mode="frame", frame_id=frame_id)
        self.update_ascii_panel()

    def _on_escape(self, event: Any) -> None:
        # Esc: deselect any frame, highlight outer border
        self.selection = SelectionState(mode="top")
        self.update_ascii_panel()


def create_gui() -> HexiRulesGUI:
    """Create and return a new HexiRules GUI instance."""
    return HexiRulesGUI()
