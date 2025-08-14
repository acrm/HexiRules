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
    tk.Button(btns, text="Load", width=10, command=on_load).pack(
        side=tk.LEFT, padx=3
    )
    tk.Button(btns, text="Save", width=10, command=on_save).pack(
        side=tk.LEFT, padx=3
    )
    if on_rename is not None:
        tk.Button(btns, text="Rename", width=10, command=on_rename).pack(
            side=tk.LEFT, padx=3
        )
    tk.Button(btns, text="Delete", width=10, command=on_delete, bg="lightcoral").pack(
        side=tk.LEFT, padx=3
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
