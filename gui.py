#!/usr/bin/env python3
"""
HexiRules GUI Module

Unified GUI supporting both Conway-style totalistic rules and HexiDirect symbolic rules.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Tuple, Optional
import math
from automaton import Automaton
from hex_rules import HexAutomaton

# Configuration
GRID_RADIUS = 8
CELL_SIZE = 15
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
GRID_WIDTH = WINDOW_WIDTH // 2  # Right half for grid
CONTROLS_WIDTH = WINDOW_WIDTH // 2  # Left half for controls

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
        self.is_hexidirect = tk.BooleanVar(value=False)
        self.hex_items: Dict[Tuple[int, int], int] = {}

        # Automatons
        self.conway_automaton = Automaton(radius=GRID_RADIUS)
        self.hex_automaton = HexAutomaton(radius=GRID_RADIUS)

        self.create_widgets()
        self.update_display()

    @property
    def current_automaton(self):
        """Get the currently active automaton based on mode."""
        return self.hex_automaton if self.is_hexidirect.get() else self.conway_automaton

    def create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Controls
        self.create_controls_panel(main_frame)

        # Right side - Grid
        self.create_grid_panel(main_frame)

    def create_controls_panel(self, parent) -> None:
        """Create the controls panel on the left side."""
        controls_frame = tk.Frame(parent, width=CONTROLS_WIDTH, bg="lightblue")
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        controls_frame.pack_propagate(False)  # Maintain fixed width

        # Mode toggle
        mode_frame = tk.LabelFrame(controls_frame, text="Rule Mode", padx=10, pady=5)
        mode_frame.pack(fill=tk.X, pady=5)

        tk.Radiobutton(
            mode_frame,
            text="Conway/Totalistic Rules",
            variable=self.is_hexidirect,
            value=False,
            command=self.on_mode_change,
        ).pack(anchor=tk.W)
        tk.Radiobutton(
            mode_frame,
            text="HexiDirect Symbolic Rules",
            variable=self.is_hexidirect,
            value=True,
            command=self.on_mode_change,
        ).pack(anchor=tk.W)

        # Rules input
        rules_frame = tk.LabelFrame(controls_frame, text="Rules", padx=10, pady=5)
        rules_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.rule_label = tk.Label(
            rules_frame, text="Enter Conway rules (e.g., B3/S23):"
        )
        self.rule_label.pack(anchor=tk.W)

        # Text area for rules
        text_frame = tk.Frame(rules_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        self.rule_text = tk.Text(text_frame, height=8, font=("Consolas", 10))
        rule_scrollbar = tk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.rule_text.yview
        )
        self.rule_text.configure(yscrollcommand=rule_scrollbar.set)

        self.rule_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rule_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Default Conway rule
        self.rule_text.insert("1.0", "B3/S23")

        # Control buttons
        button_frame = tk.Frame(rules_frame)
        button_frame.pack(fill=tk.X, pady=5)

        tk.Button(button_frame, text="Step", command=self.step, bg="lightgreen").pack(
            side=tk.LEFT, padx=2
        )
        tk.Button(button_frame, text="Clear", command=self.clear, bg="lightcoral").pack(
            side=tk.LEFT, padx=2
        )
        tk.Button(
            button_frame, text="Random", command=self.randomize, bg="lightyellow"
        ).pack(side=tk.LEFT, padx=2)

        # Status and help
        status_frame = tk.LabelFrame(
            controls_frame, text="Status & Help", padx=10, pady=5
        )
        status_frame.pack(fill=tk.X, pady=5)

        self.status_label = tk.Label(
            status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady=2)

        self.help_label = tk.Label(
            status_frame,
            text="Conway mode: Click to toggle cells\nHexiDirect mode: Left click: cycle states | Right click: cycle directions | Middle click: clear",
            font=("Arial", 9),
            justify=tk.LEFT,
            wraplength=CONTROLS_WIDTH - 40,
        )
        self.help_label.pack(fill=tk.X, pady=2)

        # Comprehensive processing log
        log_frame = tk.LabelFrame(
            controls_frame, text="Processing Log", padx=10, pady=5
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        log_text_frame = tk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_text_frame, height=12, font=("Consolas", 9), wrap=tk.WORD
        )
        log_scrollbar = tk.Scrollbar(
            log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Clear log button
        tk.Button(
            log_frame, text="Clear Log", command=self.clear_log, bg="lightblue"
        ).pack(pady=2)

    def create_grid_panel(self, parent) -> None:
        """Create the grid panel on the right side."""
        grid_frame = tk.Frame(parent, width=GRID_WIDTH, bg="lightgray")
        grid_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas for hexagonal grid
        self.canvas = tk.Canvas(
            grid_frame, width=GRID_WIDTH - 20, height=WINDOW_HEIGHT - 20, bg="lightgray"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_middle_click)

    def get_hex_coordinates(self, canvas_x: int, canvas_y: int) -> Tuple[int, int]:
        """Convert canvas coordinates to hex grid coordinates."""
        center_x = (GRID_WIDTH - 20) // 2
        center_y = (WINDOW_HEIGHT - 20) // 2

        # Convert to hex coordinates
        x = (canvas_x - center_x) / (CELL_SIZE * 1.5)
        y = (canvas_y - center_y) / (CELL_SIZE * math.sqrt(3))

        # Round to nearest hex
        q = round(x)
        r = round(y - x / 2)

        return q, r

    def get_canvas_position(self, q: int, r: int) -> Tuple[float, float]:
        """Convert hex coordinates to canvas position."""
        center_x = (GRID_WIDTH - 20) // 2
        center_y = (WINDOW_HEIGHT - 20) // 2

        x = center_x + q * CELL_SIZE * 1.5
        y = center_y + (r + q / 2) * CELL_SIZE * math.sqrt(3)

        return x, y

    def draw_hex(
        self,
        x: float,
        y: float,
        color: str,
        state: str = "",
        direction: Optional[int] = None,
    ) -> int:
        """Draw a hexagon at the given position with state and direction."""
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            px = x + CELL_SIZE * math.cos(angle)
            py = y + CELL_SIZE * math.sin(angle)
            points.extend([px, py])

        hex_id = self.canvas.create_polygon(
            points, fill=color, outline="black", width=1
        )

        if self.is_hexidirect.get():
            # HexiDirect mode - show state and direction
            if state and state != "_":
                if direction is not None:
                    text = f"{state}{direction}"
                else:
                    text = state
                self.canvas.create_text(
                    x, y, text=text, font=("Arial", 8, "bold"), fill="black"
                )

            # Add small dot indicator on the side for directional cells
            if direction is not None:
                dot_distance = CELL_SIZE * 0.8
                # Direction mapping: 1=90°, 2=30°, 3=-30°, 4=-90°, 5=-150°, 6=150°
                # Convert direction (1-6) to angle in radians
                angle_degrees = 90 - (direction - 1) * 60  # 90, 30, -30, -90, -150, 150
                angle = math.radians(angle_degrees)
                dot_x = x + dot_distance * math.cos(angle)
                dot_y = y - dot_distance * math.sin(
                    angle
                )  # Negative because screen Y increases downward
                self.canvas.create_oval(
                    dot_x - 3,
                    dot_y - 3,
                    dot_x + 3,
                    dot_y + 3,
                    fill="red",
                    outline="darkred",
                )
        else:
            # Conway mode - show simple state
            if state == "1":
                self.canvas.create_oval(
                    x - 4, y - 4, x + 4, y + 4, fill="black", outline="black"
                )

        return hex_id

    def update_display(self) -> None:
        """Update the visual display."""
        self.canvas.delete("all")
        self.hex_items.clear()

        automaton = self.current_automaton

        # Draw grid
        for q in range(-GRID_RADIUS, GRID_RADIUS + 1):
            for r in range(-GRID_RADIUS, GRID_RADIUS + 1):
                if abs(q + r) <= GRID_RADIUS:
                    x, y = self.get_canvas_position(q, r)

                    if self.is_hexidirect.get():
                        # HexiDirect mode
                        cell = automaton.get_cell(q, r)
                        color = STATE_COLORS.get(cell.state, "gray")
                        hex_id = self.draw_hex(x, y, color, cell.state, cell.direction)
                    else:
                        # Conway mode
                        state = automaton.get_cell_state(q, r)
                        color = "black" if state == "1" else "white"
                        hex_id = self.draw_hex(x, y, color, state)

                    self.hex_items[(q, r)] = hex_id

        # Update status
        if self.is_hexidirect.get():
            active_cells = len(automaton.get_active_cells())
        else:
            active_cells = sum(
                1
                for q in range(-GRID_RADIUS, GRID_RADIUS + 1)
                for r in range(-GRID_RADIUS, GRID_RADIUS + 1)
                if abs(q + r) <= GRID_RADIUS and automaton.get_cell_state(q, r) == "1"
            )

        current_rules = self.rule_text.get("1.0", tk.END).strip().replace("\n", ", ")
        if len(current_rules) > 30:
            current_rules = current_rules[:27] + "..."
        self.status_label.config(
            text=f"Active cells: {active_cells} | Rules: {current_rules}"
        )

    def on_mode_change(self) -> None:
        """Handle mode toggle between Conway and HexiDirect."""
        if self.is_hexidirect.get():
            # Switch to HexiDirect mode
            self.rule_label.config(text="Enter HexiDirect rules (e.g., a[b] => c):")
            self.rule_text.delete("1.0", tk.END)
            self.rule_text.insert("1.0", "t[-a] => t%\n_[t.] => a\nt%[a] => t")
            self.help_label.config(
                text="HexiDirect mode: Left click: cycle states | Right click: cycle directions | Middle click: clear"
            )
        else:
            # Switch to Conway mode
            self.rule_label.config(text="Enter Conway rules (e.g., B3/S23):")
            self.rule_text.delete("1.0", tk.END)
            self.rule_text.insert("1.0", "B3/S23")
            self.help_label.config(text="Conway mode: Click to toggle cells")

        self.update_display()

    def on_left_click(self, event: Any) -> None:
        """Handle left mouse click."""
        q, r = self.get_hex_coordinates(event.x, event.y)
        if (
            abs(q) <= GRID_RADIUS
            and abs(r) <= GRID_RADIUS
            and abs(q + r) <= GRID_RADIUS
        ):
            if self.is_hexidirect.get():
                # HexiDirect mode - cycle through states
                current_cell = self.hex_automaton.get_cell(q, r)
                current_state = current_cell.state

                try:
                    current_idx = SYMBOLIC_STATES.index(current_state)
                    next_idx = (current_idx + 1) % len(SYMBOLIC_STATES)
                except ValueError:
                    next_idx = 1  # Start with 'a' if unknown state

                new_state = SYMBOLIC_STATES[next_idx]
                self.hex_automaton.set_cell(q, r, new_state, current_cell.direction)
            else:
                # Conway mode - toggle cell
                self.conway_automaton.toggle_cell(q, r)

            self.update_display()

    def on_right_click(self, event: Any) -> None:
        """Handle right mouse click (HexiDirect only)."""
        if not self.is_hexidirect.get():
            return

        q, r = self.get_hex_coordinates(event.x, event.y)
        if (
            abs(q) <= GRID_RADIUS
            and abs(r) <= GRID_RADIUS
            and abs(q + r) <= GRID_RADIUS
        ):
            current_cell = self.hex_automaton.get_cell(q, r)

            # Only add directions to non-empty cells
            if current_cell.state != "_":
                current_dir = current_cell.direction
                if current_dir is None:
                    new_dir = 1
                elif current_dir == 6:
                    new_dir = None  # After 6, go to None
                else:
                    new_dir = current_dir + 1

                self.hex_automaton.set_cell(q, r, current_cell.state, new_dir)
                self.update_display()

    def on_middle_click(self, event: Any) -> None:
        """Handle middle mouse click (HexiDirect only)."""
        if not self.is_hexidirect.get():
            return

        q, r = self.get_hex_coordinates(event.x, event.y)
        if (
            abs(q) <= GRID_RADIUS
            and abs(r) <= GRID_RADIUS
            and abs(q + r) <= GRID_RADIUS
        ):
            self.hex_automaton.set_cell(q, r, "_")
            self.update_display()

    def clear_log(self) -> None:
        """Clear the processing log."""
        self.log_text.delete("1.0", tk.END)

    def log_message(self, message: str) -> None:
        """Add a message to the processing log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def step(self) -> None:
        """Advance simulation by one step."""
        rules_text = self.rule_text.get("1.0", tk.END).strip()
        if not rules_text:
            return

        self.log_message("=" * 50)
        self.log_message("STEP: Starting new simulation step")

        if self.is_hexidirect.get():
            # HexiDirect rules
            rules = []
            for line in rules_text.split("\n"):
                line_rules = [r.strip() for r in line.split(",") if r.strip()]
                rules.extend(line_rules)

            if rules:
                self.log_message(f"Rules: {rules}")
                self.hex_automaton.set_rules(rules)

                # Log expanded rules
                self.log_message("Expanded rules:")
                for i, rule in enumerate(self.hex_automaton.rules, 1):
                    self.log_message(f"  {i}: {rule.rule_str}")

                # Log active cells before step
                active_cells = []
                for (q, r), cell in self.hex_automaton.grid.items():
                    if cell.state != "_":
                        active_cells.append(f"({q},{r}):{cell}")

                self.log_message(f"Active cells before step: {len(active_cells)}")
                for cell_info in active_cells[:10]:  # Show first 10
                    self.log_message(f"  {cell_info}")
                if len(active_cells) > 10:
                    self.log_message(f"  ... and {len(active_cells) - 10} more")

                # Log rule applications
                self.log_rule_applications()

                self.hex_automaton.step()

                # Log active cells after step
                new_active_cells = []
                for (q, r), cell in self.hex_automaton.grid.items():
                    if cell.state != "_":
                        new_active_cells.append(f"({q},{r}):{cell}")

                self.log_message(f"Active cells after step: {len(new_active_cells)}")
                for cell_info in new_active_cells[:10]:  # Show first 10
                    self.log_message(f"  {cell_info}")
                if len(new_active_cells) > 10:
                    self.log_message(f"  ... and {len(new_active_cells) - 10} more")
        else:
            # Conway rules
            self.log_message(f"Conway rule: {rules_text}")
            self.conway_automaton.set_rule(rules_text)
            self.conway_automaton.step()

        self.log_message("STEP: Completed")
        self.update_display()

    def log_rule_applications(self) -> None:
        """Log detailed rule application analysis."""
        self.log_message("Analyzing rule applications:")

        checked_count = 0
        match_count = 0

        for (q, r), cell in self.hex_automaton.grid.items():
            for rule in self.hex_automaton.rules:
                checked_count += 1

                # Check if this rule would apply to this cell
                if rule.source_state == cell.state:
                    if (
                        rule.source_direction is None
                        or rule.source_direction == "random"
                        or rule.source_direction == cell.direction
                    ):
                        if self.hex_automaton.matches_condition(cell, q, r, rule):
                            match_count += 1
                            result = self.hex_automaton.apply_rule(cell, q, r, rule)
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
        """Clear all cells."""
        if self.is_hexidirect.get():
            self.hex_automaton.clear()
        else:
            self.conway_automaton.clear()
        self.update_display()

    def randomize(self) -> None:
        """Randomize the grid."""
        import random

        if self.is_hexidirect.get():
            # Random HexiDirect states
            for q in range(-GRID_RADIUS // 2, GRID_RADIUS // 2 + 1):
                for r in range(-GRID_RADIUS // 2, GRID_RADIUS // 2 + 1):
                    if abs(q + r) <= GRID_RADIUS // 2 and random.random() < 0.3:
                        state = random.choice(SYMBOLIC_STATES[1:4])  # a, b, c
                        direction = random.choice([None, 1, 2, 3, 4, 5, 6])
                        self.hex_automaton.set_cell(q, r, state, direction)
        else:
            # Random Conway states
            for q in range(-GRID_RADIUS // 2, GRID_RADIUS // 2 + 1):
                for r in range(-GRID_RADIUS // 2, GRID_RADIUS // 2 + 1):
                    if abs(q + r) <= GRID_RADIUS // 2 and random.random() < 0.3:
                        self.conway_automaton.set_cell_state(q, r, "1")

        self.update_display()

    def run(self) -> None:
        """Start the GUI main loop."""
        self.root.mainloop()


def create_gui() -> HexiRulesGUI:
    """Create and return a new HexiRules GUI instance."""
    return HexiRulesGUI()
