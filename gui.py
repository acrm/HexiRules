#!/usr/bin/env python3
"""
HexiRules GUI Module

Unified GUI supporting both Conway-style totalistic rules and HexiDirect symbolic rules.
Adds responsive scaling and multi-panel workflow: worlds, cells, rules, run, and log.
"""

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from typing import Any, Dict, List, Tuple, Optional, cast
import math
import json
import os
from automaton import Automaton
from hex_rules import HexAutomaton

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
        self.is_hexidirect = tk.BooleanVar(value=True)
        self.hex_items: Dict[Tuple[int, int], int] = {}

        # Per-canvas dynamic layout
        self.canvas: tk.Canvas
        self.canvas_center: Tuple[int, int] = (0, 0)
        self.cell_size: float = 15.0

        # Worlds management: name -> dict
        self.worlds: Dict[str, Dict[str, Any]] = {}
        self.current_world: Optional[str] = None

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
        world: Dict[str, Any] = {
            "name": name,
            "radius": radius,
            "is_hex": is_hex,
            "rules_text": rules_text,
            "conway": Automaton(
                radius=radius, rule=rules_text if not is_hex else "B3/S23"
            ),
            "hex": HexAutomaton(radius=radius),
        }
        # Apply hex rules if needed
        if is_hex and rules_text:
            rules = [
                r.strip()
                for r in rules_text.replace(";", "\n").split("\n")
                if r.strip()
            ]
            cast(HexAutomaton, world["hex"]).set_rules(rules)
        self.worlds[name] = world
        # Update world list UI
        if hasattr(self, "world_list"):
            if name not in self.world_list.get(0, tk.END):
                self.world_list.insert(tk.END, name)

    def _select_world(self, name: str) -> None:
        if name not in self.worlds:
            return
        self.current_world = name
        world = self.worlds[name]
        # Sync UI
        self.is_hexidirect.set(bool(world.get("is_hex", False)))
        self.rule_text.delete("1.0", tk.END)
        self.rule_text.insert("1.0", world.get("rules_text", ""))
        # Sync rule label with current mode
        if bool(world.get("is_hex", False)):
            self.rule_label.config(text="Enter HexiDirect rules (e.g., a[b] => c):")
        else:
            self.rule_label.config(text="Enter Conway rules (e.g., B3/S23):")
        # Select in listbox
        if hasattr(self, "world_list"):
            try:
                idx = list(self.worlds).index(name)
                self.world_list.selection_clear(0, tk.END)
                self.world_list.selection_set(idx)
                self.world_list.see(idx)
            except Exception:
                pass
        self.update_display()

    def _get_current_world(self) -> Dict[str, Any]:
        if not self.current_world:
            # Shouldn't happen after init, but guard
            self._init_default_world()
        assert self.current_world is not None
        return self.worlds[self.current_world]

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
        self._build_world_tab(world_section)

        # Cells section
        cells_section = tk.LabelFrame(controls_frame, text="Cells", bg="lightblue")
        cells_section.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self._build_cells_tab(cells_section)

        # Rules section
        rules_section = tk.LabelFrame(controls_frame, text="Rules", bg="lightblue")
        rules_section.grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
        self._build_rules_tab(rules_section)

        # Run section
        run_section = tk.LabelFrame(controls_frame, text="Run", bg="lightblue")
        run_section.grid(row=3, column=0, sticky="nsew", padx=4, pady=4)
        self._build_run_tab(run_section)

        # Log section
        log_section = tk.LabelFrame(controls_frame, text="Log", bg="lightblue")
        log_section.grid(row=4, column=0, sticky="nsew", padx=4, pady=4)
        self._build_log_tab(log_section)

    def _build_world_tab(self, frame: tk.Misc) -> None:
        # World list
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self.world_list = tk.Listbox(list_frame, height=8)
        self.world_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.world_list.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.world_list.configure(yscrollcommand=sb.set)
        self.world_list.bind("<<ListboxSelect>>", self.on_world_select)

        # Actions
        btns = tk.Frame(frame)
        btns.pack(fill=tk.X, padx=8, pady=6)
        tk.Button(btns, text="New", command=self.new_world, bg="lightgreen").pack(
            side=tk.LEFT, padx=3
        )
        tk.Button(btns, text="Load", command=self.load_world).pack(side=tk.LEFT, padx=3)
        tk.Button(btns, text="Save", command=self.save_world).pack(side=tk.LEFT, padx=3)
        tk.Button(btns, text="Delete", command=self.delete_world, bg="lightcoral").pack(
            side=tk.RIGHT, padx=3
        )

        # Info
        self.world_info = tk.Label(
            frame,
            text="Create, select, load/save worlds. Radius can vary per world.",
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=CONTROLS_WIDTH - 20,
        )
        self.world_info.pack(fill=tk.X, padx=8, pady=4)

    def _build_cells_tab(self, frame: tk.Misc) -> None:
        info = tk.Label(
            frame,
            text=(
                "Click on the grid to edit cells.\n"
                "HexiDirect: Left=cycle state, Right=cycle direction, Middle=clear.\n"
                "Conway: Left=toggle."
            ),
            justify=tk.LEFT,
            wraplength=CONTROLS_WIDTH - 20,
        )
        info.pack(fill=tk.X, padx=8, pady=6)

        btns = tk.Frame(frame)
        btns.pack(fill=tk.X, padx=8, pady=6)
        tk.Button(btns, text="Clear", command=self.clear, bg="lightcoral").pack(
            side=tk.LEFT, padx=3
        )
        tk.Button(btns, text="Random", command=self.randomize, bg="lightyellow").pack(
            side=tk.LEFT, padx=3
        )

    def _build_rules_tab(self, frame: tk.Misc) -> None:
        # Compact one-line mode switcher
        mode_frame = tk.Frame(frame)
        mode_frame.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        tk.Radiobutton(
            mode_frame,
            text="Conway",
            variable=self.is_hexidirect,
            value=False,
            command=self.on_mode_change,
        ).pack(side=tk.LEFT, padx=(6, 0))
        tk.Radiobutton(
            mode_frame,
            text="HexiDirect",
            variable=self.is_hexidirect,
            value=True,
            command=self.on_mode_change,
        ).pack(side=tk.LEFT, padx=(6, 0))

        rules_frame = tk.LabelFrame(frame, text="Rules", padx=8, pady=5)
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        self.rule_label = tk.Label(
            rules_frame, text="Enter HexiDirect rules (e.g., a[b] => c):"
        )
        self.rule_label.pack(anchor=tk.W)

        text_frame = tk.Frame(rules_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        self.rule_text = tk.Text(text_frame, height=12, font=("Consolas", 10))
        rule_scrollbar = tk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.rule_text.yview
        )
        self.rule_text.configure(yscrollcommand=rule_scrollbar.set)
        self.rule_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rule_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Default rule
        self.rule_text.insert("1.0", "t[-a] => t%\n_[t.] => a\nt%[a] => t")

    def _build_run_tab(self, frame: tk.Misc) -> None:
        btns = tk.Frame(frame)
        btns.pack(fill=tk.X, padx=8, pady=6)
        tk.Button(btns, text="Step", command=self.step, bg="lightgreen").pack(
            side=tk.LEFT, padx=3
        )
        self.status_label = tk.Label(frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=8, pady=6)

    def _build_log_tab(self, frame: tk.Misc) -> None:
        log_text_frame = tk.Frame(frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self.log_text = tk.Text(
            log_text_frame, height=16, font=("Consolas", 9), wrap=tk.WORD
        )
        log_scrollbar = tk.Scrollbar(
            log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Button(frame, text="Clear Log", command=self.clear_log).pack(pady=4)

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
        if world.get("is_hex", False):
            if state and state != "_":
                label = f"{state}{direction}" if direction is not None else state
                self.canvas.create_text(x, y, text=label, font=("Arial", 8, "bold"))
            if direction is not None:
                dot_distance = self.cell_size * 0.8
                angle_degrees = 90 - (direction - 1) * 60
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
        else:
            if state == "1":
                self.canvas.create_oval(
                    x - 4, y - 4, x + 4, y + 4, fill="black", outline="black"
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
        automaton = world["hex"] if world.get("is_hex", False) else world["conway"]

        for q in range(-R, R + 1):
            for r in range(-R, R + 1):
                if abs(q + r) <= R:
                    x, y = self.get_canvas_position(q, r)
                    if world.get("is_hex", False):
                        cell = automaton.get_cell(q, r)
                        color = STATE_COLORS.get(cell.state, "gray")
                        hex_id = self.draw_hex(x, y, color, cell.state, cell.direction)
                    else:
                        state = automaton.get_cell_state(q, r)
                        color = "black" if state == "1" else "white"
                        hex_id = self.draw_hex(x, y, color, state)
                    self.hex_items[(q, r)] = hex_id

        # Status
        if world.get("is_hex", False):
            active_cells = len(automaton.get_active_cells())
        else:
            active_cells = sum(
                1
                for q in range(-R, R + 1)
                for r in range(-R, R + 1)
                if abs(q + r) <= R and automaton.get_cell_state(q, r) == "1"
            )
        current_rules = self.rule_text.get("1.0", tk.END).strip().replace("\n", ", ")
        if len(current_rules) > 40:
            current_rules = current_rules[:37] + "..."
        self.status_label.config(
            text=f"World: {world['name']} | Active: {active_cells} | Rules: {current_rules}"
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
        is_hex = messagebox.askyesno(
            "Mode", "Use HexiDirect symbolic rules for this world?", parent=self.root
        )
        default_rules = "t[-a] => t%\n_[t.] => a\nt%[a] => t" if is_hex else "B3/S23"
        self._create_world(name, radius, is_hex, default_rules)
        self._select_world(name)

    def delete_world(self) -> None:
        sel = self.world_list.curselection()
        if not sel:
            return
        name = self.world_list.get(sel[0])
        if messagebox.askyesno("Delete World", f"Delete '{name}'?", parent=self.root):
            del self.worlds[name]
            self.world_list.delete(sel[0])
            if self.worlds:
                self._select_world(next(iter(self.worlds.keys())))
            else:
                self._init_default_world()

    def save_world(self) -> None:
        world = self._get_current_world()
        # Sync rules and mode from UI
        world["is_hex"] = bool(self.is_hexidirect.get())
        world["rules_text"] = self.rule_text.get("1.0", tk.END).strip()
        data: Dict[str, Any] = {
            "name": world["name"],
            "radius": world["radius"],
            "is_hex": world["is_hex"],
            "rules_text": world["rules_text"],
            "hex_cells": [
                {"q": q, "r": r, "s": cell.state, "d": cell.direction}
                for (q, r), cell in cast(HexAutomaton, world["hex"]).grid.items()
                if cell.state != "_"
            ],
            "conway_cells": [list(pos) for pos in world["conway"].state.keys()],
        }
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("HexiRules World", "*.json")],
            initialfile=f"{world['name']}.json",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
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
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("name") or os.path.splitext(os.path.basename(path))[0]
            radius = int(data.get("radius", DEFAULT_RADIUS))
            is_hex = bool(data.get("is_hex", False))
            rules_text = str(data.get("rules_text", "B3/S23"))
            self._create_world(name, radius, is_hex, rules_text)
            world = self.worlds[name]
            # Populate cells
            cast(HexAutomaton, world["hex"]).clear()
            for item in data.get("hex_cells", []):
                cast(HexAutomaton, world["hex"]).set_cell(
                    int(item["q"]), int(item["r"]), str(item["s"]), item.get("d")
                )
            world["conway"].clear()
            for pos in data.get("conway_cells", []):
                try:
                    q, r = int(pos[0]), int(pos[1])
                    world["conway"].state[(q, r)] = 1
                except Exception:
                    continue
            self._select_world(name)
            self.log_message(f"Loaded world from {os.path.basename(path)}")
        except Exception as e:
            self.log_message(f"Load failed: {e}")

    # -------- Mode and editing --------
    @property
    def current_automaton(self):
        world = self._get_current_world()
        return world["hex"] if world.get("is_hex", False) else world["conway"]

    def on_mode_change(self) -> None:
        """Handle mode toggle between Conway and HexiDirect."""
        world = self._get_current_world()
        world["is_hex"] = bool(self.is_hexidirect.get())
        if world["is_hex"]:
            self.rule_label.config(text="Enter HexiDirect rules (e.g., a[b] => c):")
            if not self.rule_text.get("1.0", tk.END).strip():
                self.rule_text.insert("1.0", "t[-a] => t%\n_[t.] => a\nt%[a] => t")
        else:
            self.rule_label.config(text="Enter Conway rules (e.g., B3/S23):")
            if not self.rule_text.get("1.0", tk.END).strip():
                self.rule_text.insert("1.0", "B3/S23")
        self.update_display()

    def on_left_click(self, event: Any) -> None:
        q, r = self.get_hex_coordinates(event.x, event.y)
        world = self._get_current_world()
        R = int(world.get("radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            if world.get("is_hex", False):
                current_cell = world["hex"].get_cell(q, r)
                current_state = current_cell.state
                try:
                    current_idx = SYMBOLIC_STATES.index(current_state)
                    next_idx = (current_idx + 1) % len(SYMBOLIC_STATES)
                except ValueError:
                    next_idx = 1
                new_state = SYMBOLIC_STATES[next_idx]
                world["hex"].set_cell(q, r, new_state, current_cell.direction)
            else:
                world["conway"].toggle_cell(q, r)
            self.update_display()

    def on_right_click(self, event: Any) -> None:
        world = self._get_current_world()
        if not world.get("is_hex", False):
            return
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
        if not world.get("is_hex", False):
            return
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
        self.log_message("=" * 50)
        self.log_message("STEP: Starting new simulation step")

        world = self._get_current_world()
        if world.get("is_hex", False):
            rules: List[str] = []
            for line in rules_text.split("\n"):
                line_rules = [r.strip() for r in line.split(",") if r.strip()]
                rules.extend(line_rules)
            if rules:
                self.log_message(f"Rules: {rules}")
                world["hex"].set_rules(rules)
                self.log_message("Expanded rules:")
                for i, rule in enumerate(world["hex"].rules, 1):
                    self.log_message(f"  {i}: {rule.rule_str}")
                active_cells = [
                    f"({q},{r}):{cell}"
                    for (q, r), cell in world["hex"].grid.items()
                    if cell.state != "_"
                ]
                self.log_message(f"Active cells before step: {len(active_cells)}")
                for cell_info in active_cells[:10]:
                    self.log_message(f"  {cell_info}")
                if len(active_cells) > 10:
                    self.log_message(f"  ... and {len(active_cells) - 10} more")
                self.log_rule_applications()
                world["hex"].step()
                new_active = [
                    f"({q},{r}):{cell}"
                    for (q, r), cell in world["hex"].grid.items()
                    if cell.state != "_"
                ]
                self.log_message(f"Active cells after step: {len(new_active)}")
                for cell_info in new_active[:10]:
                    self.log_message(f"  {cell_info}")
                if len(new_active) > 10:
                    self.log_message(f"  ... and {len(new_active) - 10} more")
        else:
            self.log_message(f"Conway rule: {rules_text}")
            world["conway"].set_rule(rules_text)
            world["conway"].step()

        self.log_message("STEP: Completed")
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
        world = self._get_current_world()
        if world.get("is_hex", False):
            world["hex"].clear()
        else:
            world["conway"].clear()
        self.update_display()

    def randomize(self) -> None:
        import random

        world = self._get_current_world()
        R = int(world.get("radius", DEFAULT_RADIUS))
        if world.get("is_hex", False):
            for q in range(-R // 2, R // 2 + 1):
                for r in range(-R // 2, R // 2 + 1):
                    if abs(q + r) <= R // 2 and random.random() < 0.3:
                        state = random.choice(SYMBOLIC_STATES[1:4])
                        direction = random.choice([None, 1, 2, 3, 4, 5, 6])
                        world["hex"].set_cell(q, r, state, direction)
        else:
            for q in range(-R // 2, R // 2 + 1):
                for r in range(-R // 2, R // 2 + 1):
                    if abs(q + r) <= R // 2 and random.random() < 0.3:
                        world["conway"].set_cell_state(q, r, "1")
        self.update_display()

    def run(self) -> None:
        self.root.mainloop()


def create_gui() -> HexiRulesGUI:
    """Create and return a new HexiRules GUI instance."""
    return HexiRulesGUI()
