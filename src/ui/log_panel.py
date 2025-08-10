import tkinter as tk

def build_log_tab(frame: tk.Misc, on_clear) -> tk.Text:
    log_text_frame = tk.Frame(frame)
    log_text_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
    log_text = tk.Text(log_text_frame, height=16, font=("Consolas", 9), wrap=tk.WORD)
    log_scrollbar = tk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=log_text.yview)
    log_text.configure(yscrollcommand=log_scrollbar.set)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tk.Button(frame, text="Clear Log", command=on_clear).pack(pady=4)
    return log_text
