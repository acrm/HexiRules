#!/usr/bin/env python3
"""
HexiRules GUI Module (HexiDirect-only)

Responsive multi-panel GUI: worlds, cells, rules, run, and log.
"""

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from typing import Any, Dict, List, Tuple, Optional, cast
import math
import json
import os
from hex_rules import HexAutomaton
from app.controller import HexiController
from ui import (
    build_world_tab,
    build_cells_tab,
    build_rules_tab,
    build_run_tab,
    build_log_tab,
)

# Configuration
DEFAULT_RADIUS = 8
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CONTROLS_WIDTH = WINDOW_WIDTH // 3  # Left third for controls

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
        # GUI state
        # HexiDirect-only (kept for API compatibility with builders)
        self.is_hexidirect = tk.BooleanVar(value=True)
        self.hex_items = {}

        # Per-canvas dynamic layout
        self.canvas = None  # will be created in create_grid_panel
        self.canvas_center = (0, 0)
        self.cell_size = 15.0

        # Worlds management delegated to controller
        self.controller = HexiController()

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
        world = self.controller.select_world(name)
        # Sync UI
        self.is_hexidirect.set(True)
        self.rule_text.delete("1.0", tk.END)
        self.rule_text.insert("1.0", world.get("rules_text", ""))
        # Sync rule label with current mode
        self.rule_label.config(text="Enter HexiDirect rules (e.g., a[b] => c):")
        # Select in listbox
        if hasattr(self, "world_list"):
            try:
                idx = list(self.controller.worlds).index(name)
                self.world_list.selection_clear(0, tk.END)
                self.world_list.selection_set(idx)
                self.world_list.see(idx)
            except Exception:
                pass
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
        """Create all GUI widgets."""
        # Main container split left/right
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Controls
        self.create_controls_panel(main_frame)

        # Right side - Grid Canvas (fills all space)
        self.create_grid_panel(main_frame)

    def create_controls_panel(self, parent) -> None:
        """Create the controls panel on the left side (no tabs), with equal space per section."""
        controls_frame = tk.Frame(parent, width=CONTROLS_WIDTH, bg="lightblue")
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        controls_frame.pack_propagate(False)

        # Use grid with custom weights (no uniform): Worlds=1, Cells=0, Rules=4, Run=0, Log=3
        controls_frame.grid_rowconfigure(0, weight=1)
        controls_frame.grid_rowconfigure(1, weight=0)
        controls_frame.grid_rowconfigure(2, weight=4)
        controls_frame.grid_rowconfigure(3, weight=0)
        controls_frame.grid_rowconfigure(4, weight=3)
        controls_frame.grid_columnconfigure(0, weight=1)

        # Worlds section
        world_section = tk.LabelFrame(controls_frame, text="Worlds", bg="lightblue")
        world_section.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.world_list, self.world_info = build_world_tab(
            world_section,
            self.on_world_select,
            self.new_world,
            self.load_world,
            self.save_world,
            self.delete_world,
        )

        # Cells section
        cells_section = tk.LabelFrame(controls_frame, text="Cells", bg="lightblue")
        cells_section.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        build_cells_tab(cells_section, self.clear, self.randomize)

        # Rules section
        rules_section = tk.LabelFrame(controls_frame, text="Rules", bg="lightblue")
        rules_section.grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
        self.rule_label, self.rule_text = build_rules_tab(
            rules_section, self.is_hexidirect, self.on_mode_change
        )
        # Default rule
        self.rule_text.insert("1.0", "t[-a] => t%\n_[t.] => a\nt%[a] => t")

        # Run section
        run_section = tk.LabelFrame(controls_frame, text="Run", bg="lightblue")
        run_section.grid(row=3, column=0, sticky="nsew", padx=4, pady=4)
        self.status_label = build_run_tab(run_section, self.step)

        # Log section
        log_section = tk.LabelFrame(controls_frame, text="Log", bg="lightblue")
        log_section.grid(row=4, column=0, sticky="nsew", padx=4, pady=4)
        self.log_text = build_log_tab(log_section, self.clear_log)

    # removed per-module builders; now provided by ui.panels

    def create_grid_panel(self, parent) -> None:
        """Create the grid panel on the right side."""
        grid_frame = tk.Frame(parent, bg="lightgray")
        grid_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

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
        R = int(world.get("radius", DEFAULT_RADIUS))
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
        R = int(world.get("radius", DEFAULT_RADIUS))
        automaton = world["hex"]

        for q in range(-R, R + 1):
            for r in range(-R, R + 1):
                if abs(q + r) <= R:
                    x, y = self.get_canvas_position(q, r)
                    cell = automaton.get_cell(q, r)
                    color = STATE_COLORS.get(cell.state, "gray")
                    hex_id = self.draw_hex(x, y, color, cell.state, cell.direction)
                    self.hex_items[(q, r)] = hex_id

        # Status
        active_cells = len(automaton.get_active_cells())
        mode_label = "HexiDirect"
        current_rules = self.rule_text.get("1.0", tk.END).strip().replace("\n", ", ")
        if len(current_rules) > 40:
            current_rules = current_rules[:37] + "..."
        self.status_label.config(
            text=f"World: {world['name']} | Mode: {mode_label} | Active: {active_cells} | Rules: {current_rules}"
        )

    # -------- World actions --------
    def on_world_select(self, _event: Any) -> None:
        sel = self.world_list.curselection()
        if not sel:
            return
        name = self.world_list.get(sel[0])
        self._select_world(name)

    def new_world(self) -> None:
        name = simpledialog.askstring(
            "New World", "Enter world name:", parent=self.root
        )
        if not name:
            return
        try:
            radius = int(
                simpledialog.askstring(
                    "New World", "Enter radius (e.g., 8):", parent=self.root
                )
                or DEFAULT_RADIUS
            )
        except Exception:
            radius = DEFAULT_RADIUS
        default_rules = "t[-a] => t%\n_[t.] => a\nt%[a] => t"
        self._create_world(name, radius, True, default_rules)
        self._select_world(name)

    def delete_world(self) -> None:
        sel = self.world_list.curselection()
        if not sel:
            return
        name = self.world_list.get(sel[0])
        if messagebox.askyesno("Delete World", f"Delete '{name}'?", parent=self.root):
            try:
                del self.controller.worlds[name]
            except KeyError:
                pass
            self.world_list.delete(sel[0])
            if self.controller.worlds:
                self._select_world(next(iter(self.controller.worlds.keys())))
            else:
                self._init_default_world()

    def save_world(self) -> None:
        world = self._get_current_world()
        # Sync rules and mode from UI and delegate persistence
        is_hexidirect = bool(self.is_hexidirect.get())
        rules_text = self.rule_text.get("1.0", tk.END).strip()
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("HexiRules World", "*.json")],
            initialfile=f"{world['name']}.json",
        )
        if not path:
            return
        try:
            self.controller.save_world_to_file(path, is_hexidirect, rules_text)
            self.log_message(f"Saved world to {os.path.basename(path)}")
        except Exception as e:
            self.log_message(f"Save failed: {e}")

    def load_world(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("HexiRules World", "*.json"), ("All", "*.*")]
        )
        if not path:
            return
        try:
            name = self.controller.load_world_from_file(path)
            # Ensure it's listed and selected
            if name not in self.world_list.get(0, tk.END):
                self.world_list.insert(tk.END, name)
            self._select_world(name)
            self.log_message(f"Loaded world from {os.path.basename(path)}")
        except Exception as e:
            self.log_message(f"Load failed: {e}")

    # -------- Mode and editing --------
    @property
    def current_automaton(self):
        world = self._get_current_world()
        return world["hex"]

    def on_mode_change(self) -> None:
        """Handle mode toggle (deprecated; always HexiDirect)."""
        world = self._get_current_world()
        self.is_hexidirect.set(True)
        self.rule_label.config(text="Enter HexiDirect rules (e.g., a[b] => c):")
        if not self.rule_text.get("1.0", tk.END).strip():
            self.rule_text.insert("1.0", "t[-a] => t%\n_[t.] => a\nt%[a] => t")
        self.update_display()

    def on_left_click(self, event: Any) -> None:
        q, r = self.get_hex_coordinates(event.x, event.y)
        world = self._get_current_world()
        R = int(world.get("radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            current_cell = world["hex"].get_cell(q, r)
            current_state = current_cell.state
            try:
                current_idx = SYMBOLIC_STATES.index(current_state)
                next_idx = (current_idx + 1) % len(SYMBOLIC_STATES)
            except ValueError:
                next_idx = 1
            new_state = SYMBOLIC_STATES[next_idx]
            world["hex"].set_cell(q, r, new_state, current_cell.direction)
            self.update_display()

    def on_right_click(self, event: Any) -> None:
        world = self._get_current_world()
        q, r = self.get_hex_coordinates(event.x, event.y)
        R = int(world.get("radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            current_cell = world["hex"].get_cell(q, r)
            if current_cell.state != "_":
                current_dir = current_cell.direction
                new_dir = (
                    1
                    if current_dir is None
                    else (None if current_dir == 6 else current_dir + 1)
                )
                world["hex"].set_cell(q, r, current_cell.state, new_dir)
                self.update_display()

    def on_middle_click(self, event: Any) -> None:
        world = self._get_current_world()
        q, r = self.get_hex_coordinates(event.x, event.y)
        R = int(world.get("radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            world["hex"].set_cell(q, r, "_")
            self.update_display()

    # -------- Logging and run --------
    def clear_log(self) -> None:
        self.log_text.delete("1.0", tk.END)

    def log_message(self, message: str) -> None:
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def step(self) -> None:
        rules_text = self.rule_text.get("1.0", tk.END).strip()
        if not rules_text:
            return
        logs = self.controller.step(rules_text)
        for line in logs:
            self.log_message(line)
        self.update_display()

    def log_rule_applications(self) -> None:
        self.log_message("Analyzing rule applications:")
        world = self._get_current_world()
        checked_count = 0
        match_count = 0
        for (q, r), cell in world["hex"].grid.items():
            for rule in world["hex"].rules:
                checked_count += 1
                if rule.source_state == cell.state:
                    src_dir_ok = (
                        (getattr(rule, "source_random_direction", False))
                        or (rule.source_direction is None and cell.direction is None)
                        or (rule.source_direction == cell.direction)
                    )
                    if src_dir_ok and world["hex"].matches_condition(cell, q, r, rule):
                        match_count += 1
                        result = world["hex"].apply_rule(cell, q, r, rule)
                        if result and result != cell:
                            self.log_message(
                                f"  Rule '{rule.rule_str}' applies to ({q},{r}):{cell} -> {result}"
                            )
        self.log_message(
            f"Checked {checked_count} rule-cell combinations, found {match_count} matches"
        )
        self.log_message(
            "Note: When multiple rules from same macro match, one is chosen randomly"
        )

    def clear(self) -> None:
        self.controller.clear()
        self.update_display()

    def randomize(self) -> None:
        # Use controller to randomize states
        self.controller.randomize(SYMBOLIC_STATES, p=0.3)
        self.update_display()

    def run(self) -> None:
        self.root.mainloop()


def create_gui() -> HexiRulesGUI:
    """Create and return a new HexiRules GUI instance."""
    return HexiRulesGUI()
