from typing import Tuple
import tkinter as tk


def build_rules_tab(
    frame: tk.Misc, _is_hexidirect: tk.BooleanVar, _on_mode_change
) -> Tuple[tk.Label, tk.Text]:
    # HexiDirect-only
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
