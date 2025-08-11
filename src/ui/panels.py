"""
Panel builders for HexiRules GUI.
Each builder creates widgets for a section and returns key widgets to the caller.
"""

from typing import Tuple
import tkinter as tk


def build_world_tab(
    frame: tk.Misc, on_select, on_new, on_load, on_save, on_delete
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
    tk.Button(btns, text="New", command=on_new, bg="lightgreen").pack(
        side=tk.LEFT, padx=3
    )
    tk.Button(btns, text="Load", command=on_load).pack(side=tk.LEFT, padx=3)
    tk.Button(btns, text="Save", command=on_save).pack(side=tk.LEFT, padx=3)
    tk.Button(btns, text="Delete", command=on_delete, bg="lightcoral").pack(
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
            "HexiDirect: Left=cycle state, Right=cycle direction, Middle=clear.\n"
            "Conway: Left=toggle."
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
    tk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
    tk.Radiobutton(
        mode_frame,
        text="Conway",
        variable=is_hexidirect,
        value=False,
        command=on_mode_change,
    ).pack(side=tk.LEFT, padx=(6, 0))
    tk.Radiobutton(
        mode_frame,
        text="HexiDirect",
        variable=is_hexidirect,
        value=True,
        command=on_mode_change,
    ).pack(side=tk.LEFT, padx=(6, 0))

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
    tk.Button(btns, text="Step", command=on_step, bg="lightgreen").pack(
        side=tk.LEFT, padx=3
    )
    status_label = tk.Label(frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(fill=tk.X, padx=8, pady=6)
    return status_label


def build_log_tab(frame: tk.Misc, on_clear) -> tk.Text:
    log_text_frame = tk.Frame(frame)
    log_text_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
    log_text = tk.Text(log_text_frame, height=16, font=("Consolas", 9), wrap=tk.WORD)
    log_scrollbar = tk.Scrollbar(
        log_text_frame, orient=tk.VERTICAL, command=log_text.yview
    )
    log_text.configure(yscrollcommand=log_scrollbar.set)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tk.Button(frame, text="Clear Log", command=on_clear).pack(pady=4)
    return log_text
