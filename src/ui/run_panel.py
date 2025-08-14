import tkinter as tk


def build_run_tab(frame: tk.Misc, on_step) -> tk.Label:
    btns = tk.Frame(frame)
    btns.pack(fill=tk.X, padx=8, pady=6)
    tk.Button(btns, text="Step", width=10, command=on_step, bg="lightgreen").pack(
        side=tk.LEFT, padx=3
    )
    # Hide old status label; kept for compatibility
    status_label = tk.Label(frame, text="")
    status_label.pack_forget()
    return status_label
