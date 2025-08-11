import tkinter as tk


def build_run_tab(frame: tk.Misc, on_step) -> tk.Label:
    btns = tk.Frame(frame)
    btns.pack(fill=tk.X, padx=8, pady=6)
    tk.Button(btns, text="Step", command=on_step, bg="lightgreen").pack(
        side=tk.LEFT, padx=3
    )
    status_label = tk.Label(frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(fill=tk.X, padx=8, pady=6)
    return status_label
