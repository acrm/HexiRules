import tkinter as tk


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
