"""
Panel builders for HexiRules GUI.
Each builder creates widgets for a section and returns key widgets to the caller.
"""

from typing import Tuple
import tkinter as tk


def build_world_tab(
    frame: tk.Misc, on_select, on_new, on_load, on_save, on_delete, on_rename=None
) -> Tuple[tk.Listbox, tk.Label]:
    # World list
    list_frame = tk.Frame(frame)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
    world_list = tk.Listbox(list_frame, height=8)
    world_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=world_list.yview)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    world_list.configure(yscrollcommand=sb.set)
    world_list.bind("<<ListboxSelect>>", on_select)

    # Actions
    btns = tk.Frame(frame)
    btns.pack(fill=tk.X, padx=8, pady=6)
    tk.Button(btns, text="New", width=10, command=on_new, bg="lightgreen").pack(
        side=tk.LEFT, padx=3
    )
    tk.Button(btns, text="Load", width=10, command=on_load).pack(side=tk.LEFT, padx=3)
    tk.Button(btns, text="Save", width=10, command=on_save).pack(side=tk.LEFT, padx=3)
    tk.Button(btns, text="Delete", width=10, command=on_delete, bg="lightcoral").pack(
        side=tk.RIGHT, padx=3
    )
    if on_rename is not None:
        tk.Button(btns, text="Rename", width=10, command=on_rename).pack(
            side=tk.RIGHT, padx=3
        )

    # Info
    world_info = tk.Label(
        frame,
        text="Create, select, load/save worlds. Radius can vary per world.",
        anchor=tk.W,
        justify=tk.LEFT,
        wraplength=360,
    )
    world_info.pack(fill=tk.X, padx=8, pady=4)
    return world_list, world_info


def build_cells_tab(frame: tk.Misc, on_clear, on_random) -> None:
    info = tk.Label(
        frame,
        text=(
            "Click on the grid to edit cells.\n"
            "HexiDirect: Left=cycle state, Right=cycle direction, Middle=clear."
        ),
        justify=tk.LEFT,
        wraplength=360,
    )
    info.pack(fill=tk.X, padx=8, pady=6)

    btns = tk.Frame(frame)
    btns.pack(fill=tk.X, padx=8, pady=6)
    tk.Button(btns, text="Clear", command=on_clear, bg="lightcoral").pack(
        side=tk.LEFT, padx=3
    )
    tk.Button(btns, text="Random", command=on_random, bg="lightyellow").pack(
        side=tk.LEFT, padx=3
    )


def build_rules_tab(
    frame: tk.Misc, is_hexidirect: tk.BooleanVar, on_mode_change
) -> Tuple[tk.Label, tk.Text]:
    # Compact one-line mode switcher
    mode_frame = tk.Frame(frame)
    mode_frame.pack(fill=tk.X, padx=8, pady=4)
    tk.Label(mode_frame, text="Mode: HexiDirect").pack(side=tk.LEFT)

    rules_frame = tk.LabelFrame(frame, text="Rules", padx=8, pady=5)
    rules_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

    rule_label = tk.Label(rules_frame, text="Enter HexiDirect rules (e.g., a[b] => c):")
    rule_label.pack(anchor=tk.W)

    text_frame = tk.Frame(rules_frame)
    text_frame.pack(fill=tk.BOTH, expand=True, pady=2)

    rule_text = tk.Text(text_frame, height=12, font=("Consolas", 10))
    rule_scrollbar = tk.Scrollbar(
        text_frame, orient=tk.VERTICAL, command=rule_text.yview
    )
    rule_text.configure(yscrollcommand=rule_scrollbar.set)
    rule_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    rule_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    return rule_label, rule_text


def build_run_tab(frame: tk.Misc, on_step) -> tk.Label:
    btns = tk.Frame(frame)
    btns.pack(fill=tk.X, padx=8, pady=6)
    tk.Button(btns, text="Step", width=10, command=on_step, bg="lightgreen").pack(
        side=tk.LEFT, padx=3
    )
    # No global status label anymore; return a dummy label for compatibility
    status_label = tk.Label(frame, text="")
    status_label.pack_forget()
    return status_label


def build_log_tab(frame: tk.Misc, on_clear) -> tk.Text:
    # Deprecated: keep a minimal stub to avoid crashes if referenced
    container = tk.Frame(frame)
    container.pack_forget()
    text = tk.Text(container)
    return text


def build_history_panel(
    frame: tk.Misc,
    on_select,
    on_progress,
    on_prev,
    on_next,
) -> Tuple[tk.Listbox, tk.Text]:
    """Builds the history panel with list (left) and step logs (right) side-by-side, and navigation including Progress."""
    outer = tk.Frame(frame)
    outer.pack(fill=tk.BOTH, expand=True)

    # Grid layout: row 0 = content, row 1 = navigation
    outer.grid_rowconfigure(0, weight=1)
    outer.grid_rowconfigure(1, weight=0)
    outer.grid_columnconfigure(0, weight=1, minsize=140)
    outer.grid_columnconfigure(1, weight=2, minsize=180)

    # Left: list of steps with scrollbar
    list_frame = tk.Frame(outer)
    list_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=4)
    history_list = tk.Listbox(list_frame)
    history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=history_list.yview)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    history_list.configure(yscrollcommand=sb.set)
    history_list.bind("<<ListboxSelect>>", on_select)

    # Right: logs of selected step
    logs_frame = tk.Frame(outer)
    logs_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=4)
    tk.Label(logs_frame, text="Step Logs:").pack(anchor=tk.W)
    log_text = tk.Text(logs_frame, font=("Consolas", 9), wrap=tk.WORD)
    log_scroll = tk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=log_text.yview)
    log_text.configure(yscrollcommand=log_scroll.set)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # Bottom: navigation
    nav = tk.Frame(outer)
    nav.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=4)
    tk.Button(nav, text="Prev", width=8, command=on_prev).pack(side=tk.LEFT)
    tk.Button(nav, text="Next", width=8, command=on_next).pack(side=tk.LEFT, padx=6)
    tk.Button(
        nav, text="Progress", width=10, command=on_progress, bg="lightgreen"
    ).pack(side=tk.RIGHT)

    return history_list, log_text
