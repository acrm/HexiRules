from typing import Tuple
import tkinter as tk


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
