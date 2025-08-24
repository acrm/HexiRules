from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from application.world_service import WorldService
from infrastructure.ui.hexios.desktop.ascii.facade import AsciiUILayout, SelectionState


def run_hexios(parent: tk.Widget, controller: Optional[WorldService] = None) -> None:
    controller = controller or WorldService()
    frame = ttk.Frame(parent)
    frame.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

    text = tk.Text(frame, width=81, height=51, wrap="none", font=("Courier", 10))
    text.config(bg="#3d033d", fg="#ffffff", insertbackground="#ffffff")
    text.pack(side=tk.TOP)

    # Configure tags
    for tag, fg in {
        "border": "#cccccc",
        "title": "#ffffff",
        "status": "#d0d0d0",
        "section_header": "#a0a0ff",
        "selected_item": "#000000",
        "history_line": "#88ff88",
        "log_line": "#ffff88",
        "command_border": "#8888ff",
        "command_prompt": "#ffffff",
        "normal": "#ffffff",
        "hotkey": "#ffff00",
        "border_sel": "#ffff00",
    }.items():
        text.tag_config(tag, foreground=fg)

    # Render once (static); you can wire keybindings similarly to the Tk app later
    layout = AsciiUILayout(controller, selection=SelectionState(mode="top"))
    lines, tags = layout.render()

    text.config(state=tk.NORMAL)
    for line in lines:
        text.insert(tk.END, line + "\n")
    for i, line_tags in enumerate(tags):
        line_no = i + 1
        width = len(lines[i]) if i < len(lines) else 81
        for start, end, tag in line_tags:
            s = max(0, min(width - 1, start))
            e = max(0, min(width, end))
            try:
                text.tag_add(tag, f"{line_no}.{s}", f"{line_no}.{e}")
            except Exception:
                pass
    text.config(state=tk.DISABLED)
