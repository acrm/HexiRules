import tkinter as tk


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

    # Context menu for copying
    menu = tk.Menu(log_text, tearoff=0)

    def copy_selected() -> None:
        try:
            text = log_text.selection_get()
        except Exception:
            text = ""
        if text:
            log_text.clipboard_clear()
            log_text.clipboard_append(text)

    def copy_all() -> None:
        text = log_text.get("1.0", tk.END)
        log_text.clipboard_clear()
        log_text.clipboard_append(text)

    def select_all() -> None:
        log_text.tag_add(tk.SEL, "1.0", tk.END)
        log_text.mark_set(tk.INSERT, "1.0")
        log_text.see(tk.INSERT)

    menu.add_command(label="Copy", command=copy_selected)
    menu.add_command(label="Copy All", command=copy_all)
    menu.add_separator()
    menu.add_command(label="Select All", command=select_all)

    def show_menu(event: tk.Event) -> None:
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    log_text.bind("<Button-3>", show_menu)

    # Buttons row: Copy All and Clear
    btns = tk.Frame(frame)
    btns.pack(pady=4)
    tk.Button(btns, text="Copy All", command=copy_all).pack(side=tk.LEFT, padx=4)
    tk.Button(btns, text="Clear Log", command=on_clear).pack(side=tk.LEFT, padx=4)
    return log_text
