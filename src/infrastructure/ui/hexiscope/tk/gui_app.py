#!/usr/bin/env python3
"""Tk grid renderer with ASCII control panel (Tk HexiScope + ASCII HexiOS).

Infrastructure location for the Tk GUI, replacing src/ui/hexiscope/tk/gui_app.py.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Tuple

from application.world_service import WorldService
from infrastructure.ui.hexios.desktop.ascii.facade import AsciiUILayout, SelectionState
from main import HexCanvas
from domain.constants import STATE_COLORS

# Configuration
DEFAULT_RADIUS = 8
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900


class HexiRulesGUI:
    """Main GUI class for HexiRules application (Tk + ASCII)."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("HexiRules - Hexagonal Cellular Automaton")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.config(bg="#3d033d")
        self.root.config(cursor="none")

        self.selection = SelectionState(mode="top")
        self.root.bind("<Escape>", self._on_escape)
        self.root.bind("<Control-q>", self._on_ctrl_q)
        for key, frame_id in [
            ("w", "worlds"),
            ("r", "rules"),
            ("h", "history"),
            ("l", "logs"),
        ]:
            self._bind_frame_key(key, frame_id)
        self.root.focus_set()

        self.hex_items: Dict[Tuple[int, int], int] = {}
        self.canvas: tk.Canvas | None = None
        self.canvas_center = (0, 0)
        self.controller = WorldService()

        # ASCII panel
        self.ascii_frame = ttk.Frame(self.root)
        self.ascii_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
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
        self.ascii_text.config(bg="#3d033d", fg="#ffffff", insertbackground="#ffffff")
        self.ascii_text.pack(side=tk.TOP)
        self.ascii_text.bind("<MouseWheel>", lambda e: "break")
        self.ascii_text.bind("<Button-4>", lambda e: "break")
        self.ascii_text.bind("<Button-5>", lambda e: "break")

        # Command entry
        self.command_entry = ttk.Entry(self.ascii_frame, width=80)
        self.command_entry.pack(side=tk.TOP, pady=(0, 0))
        self.command_entry.bind("<Return>", self.on_command_enter)

        # Tags for ascii renderer
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
        self.ascii_text.tag_config("hotkey", foreground="#ffff00")
        self.ascii_text.tag_config("border_sel", foreground="#ffff00")

        # Right: hex canvas
        self.right_frame = tk.Frame(self.root, bg="#3d033d")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        try:
            world = self.controller.get_current_world()
            radius = int(getattr(world, "radius", DEFAULT_RADIUS))
        except Exception:
            radius = DEFAULT_RADIUS

        self.hex_canvas_helper = HexCanvas(self.root, radius=radius, cell_size=20)
        self.hex_canvas_helper.canvas.config(bg="#3d033d", highlightthickness=0)
        self.hex_canvas_helper.canvas.pack(
            in_=self.right_frame, anchor="center", expand=True
        )

        self.selected_cell = (0, 0)
        self.hex_canvas_helper.canvas.bind("<Button-1>", self._on_canvas_click)
        self.hex_canvas_helper.canvas.bind("<Motion>", self._on_canvas_motion)

        self.update_display()
        self.update_ascii_panel()

    def on_command_enter(self, event) -> None:
        command = self.command_entry.get().strip()
        if not command:
            return
        self.command_entry.delete(0, tk.END)
        self.execute_command(command)
        self.update_display()
        self.update_ascii_panel()

    def execute_command(self, command: str) -> None:
        cmd = command.strip().lower()
        if not cmd:
            return
        world = self._get_current_world()
        if cmd in ("s", "step"):
            self.step()
        elif cmd in ("c", "clear"):
            self.clear()
        elif cmd in ("r", "randomize"):
            self.randomize()
        elif cmd in ("q", "quit"):
            self.root.quit()
        elif cmd.startswith("rule "):
            rule_text = command[5:].strip()
            world.rules_text = rule_text

    def run(self) -> None:
        self.root.mainloop()

    def update_ascii_panel(self) -> None:
        try:
            selected_info = None
            if self.selected_cell:
                q, r = self.selected_cell
                try:
                    world = self._get_current_world()
                    cell = world.hex.get_cell(q, r)
                    dir_text = (
                        str(cell.direction) if cell.direction is not None else "-"
                    )
                    selected_info = (
                        f"Selected: ({q},{r}) state={cell.state} dir={dir_text}"
                    )
                except Exception:
                    selected_info = f"Selected: ({q},{r})"
            layout = AsciiUILayout(
                self.controller, selection=self.selection, selected_info=selected_info
            )
            lines, tags = layout.render()
        except Exception:
            lines = [" " * 81 for _ in range(51)]
            tags = [[] for _ in range(51)]

        self.ascii_text.config(state=tk.NORMAL)
        self.ascii_text.delete("1.0", tk.END)
        for line in lines:
            self.ascii_text.insert(tk.END, line + "\n")
        for i, line_tags in enumerate(tags):
            line_no = i + 1
            width = len(lines[i]) if i < len(lines) else 81
            for start, end, tag in line_tags:
                s = max(0, min(width - 1, start))
                e = max(0, min(width, end))
                try:
                    self.ascii_text.tag_add(tag, f"{line_no}.{s}", f"{line_no}.{e}")
                except Exception:
                    pass
        self.ascii_text.config(state=tk.DISABLED)

    def _get_current_world(self):
        return self.controller.get_current_world()

    def _on_ctrl_q(self, _event: tk.Event) -> None:
        self.root.quit()

    def _bind_frame_key(self, key: str, frame_id: str) -> None:
        def handler(_event: tk.Event) -> None:
            self._select_frame(frame_id)

        self.root.bind(key, handler)
        self.root.bind(key.upper(), handler)

    def update_display(self) -> None:
        try:
            world = self._get_current_world()
        except Exception:
            return
        canvas = self.hex_canvas_helper.canvas
        canvas.delete("all")
        for (q, r), (cx, cy) in self.hex_canvas_helper.cells.items():
            cell = world.hex.get_cell(q, r)
            color = (
                "#111111"
                if cell.state == "_"
                else STATE_COLORS.get(cell.state, "#ffffff")
            )
            pts = self.hex_canvas_helper.polygon_corners(cx, cy)
            tag = f"cell_{q}_{r}"
            canvas.create_polygon(pts, fill=color, outline="#333333", tags=(tag,))
            if getattr(cell, "direction", None):
                canvas.create_oval(
                    cx - 3, cy - 3, cx + 3, cy + 3, fill="#ffff00", outline=""
                )
        if self.selected_cell:
            q, r = self.selected_cell
            if (q, r) in self.hex_canvas_helper.cells:
                cx, cy = self.hex_canvas_helper.cells[(q, r)]
                pts = self.hex_canvas_helper.polygon_corners(cx, cy)
                canvas.create_polygon(pts, fill="", outline="#ffffff", width=2)

    def _on_canvas_click(self, event: Any) -> None:
        q, r = self.get_hex_coordinates(event.x, event.y)
        try:
            world = self._get_current_world()
        except Exception:
            return
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            self.selected_cell = (q, r)

    def step(self) -> None:
        world = self._get_current_world()
        self.controller.step(world.rules_text or "")

    def clear(self) -> None:
        world = self._get_current_world()
        world.hex.clear()

    def randomize(self) -> None:
        self.controller.randomize(list(STATE_COLORS.keys()))

    def _on_canvas_motion(self, event: Any) -> None:
        q, r = self.get_hex_coordinates(event.x, event.y)
        try:
            world = self._get_current_world()
        except Exception:
            return
        R = int(getattr(world, "radius", DEFAULT_RADIUS))
        if abs(q) <= R and abs(r) <= R and abs(q + r) <= R:
            if self.selected_cell != (q, r):
                self.selected_cell = (q, r)
                self.update_display()
                self.update_ascii_panel()

    def get_hex_coordinates(self, x: int, y: int) -> Tuple[int, int]:
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

    def _select_frame(self, frame_id: str) -> None:
        self.selection = SelectionState(mode="frame", frame_id=frame_id)
        self.update_ascii_panel()

    def _on_escape(self, event: Any) -> None:
        self.selection = SelectionState(mode="top")
        self.update_ascii_panel()


def create_gui() -> HexiRulesGUI:
    return HexiRulesGUI()
