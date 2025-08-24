from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class SelectionState:
    mode: str  # "top" or "frame"
    frame_id: Optional[str] = None


@dataclass
class GridLayoutSpec:
    width: int
    height: int

    # Frame rectangles: (x, y, w, h)
    header: Tuple[int, int, int, int]
    worlds: Tuple[int, int, int, int]
    rules: Tuple[int, int, int, int]
    history: Tuple[int, int, int, int]
    logs: Tuple[int, int, int, int]
    selected: Tuple[int, int, int, int]
    footer: Tuple[int, int, int, int]

    @staticmethod
    def default_layout() -> "GridLayoutSpec":
        width, height = 81, 51
        # Two columns of frames with header/footer spanning
        col1_x, col2_x = 0, 41
        header = (0, 0, width, 1)
        worlds = (col1_x, 1, 40, 16)
        rules = (col2_x, 1, 40, 16)
        history = (col1_x, 17, 40, 16)
        logs = (col2_x, 17, 40, 16)
        selected = (0, 33, width, 1)
        footer = (0, height - 1, width, 1)
        return GridLayoutSpec(
            width=width,
            height=height,
            header=header,
            worlds=worlds,
            rules=rules,
            history=history,
            logs=logs,
            selected=selected,
            footer=footer,
        )


try:
    # Only for typing reference; avoid circular at runtime if needed
    from .viewmodel import AsciiViewModel  # type: ignore
except Exception:  # pragma: no cover
    AsciiViewModel = object  # type: ignore


class AsciiRenderer:
    def __init__(
        self,
        vm: "AsciiViewModel",
        layout: GridLayoutSpec,
        selection: SelectionState,
    ) -> None:
        self.vm = vm
        self.layout = layout
        self.selection = selection

    def render(self) -> Tuple[List[str], List[List[Tuple[int, int, str]]]]:
        W, H = self.layout.width, self.layout.height
        # Initialize empty surface
        surface = [[" " for _ in range(W)] for _ in range(H)]
        tags: List[List[Tuple[int, int, str]]] = [[] for _ in range(H)]

        def put_text(x: int, y: int, text: str, tag: Optional[str] = None) -> None:
            if 0 <= y < H:
                for i, ch in enumerate(text):
                    xi = x + i
                    if 0 <= xi < W:
                        surface[y][xi] = ch
                if tag:
                    tags[y].append((x, min(W, x + len(text)), tag))

        # Borders helper
        def box(x: int, y: int, w: int, h: int, sel: bool = False) -> None:
            if h <= 0 or w <= 0:
                return
            horiz = "\u2500"
            vert = "\u2502"
            tl, tr, bl, br = "\u250C", "\u2510", "\u2514", "\u2518"
            tag = "border_sel" if sel else "border"
            # top
            put_text(x, y, tl + horiz * (w - 2) + tr, tag)
            # middle
            for yy in range(y + 1, y + h - 1):
                put_text(x, yy, vert, tag)
                put_text(x + w - 1, yy, vert, tag)
            # bottom
            put_text(x, y + h - 1, bl + horiz * (w - 2) + br, tag)

        # Render frames
        frames_by_id = {f.id: f for f in self.vm.frames}
        layout_map = {
            "header": self.layout.header,
            "worlds": self.layout.worlds,
            "rules": self.layout.rules,
            "history": self.layout.history,
            "logs": self.layout.logs,
            "selected": self.layout.selected,
            "footer": self.layout.footer,
        }

        for fid, rect in layout_map.items():
            if fid not in frames_by_id:
                continue
            frame = frames_by_id[fid]
            x, y, w, h = rect
            sel = self.selection.mode == "frame" and self.selection.frame_id == fid
            box(x, y, w, h, sel)
            # Title centered (spans two columns for header/footer)
            title = f" {frame.title} "
            start = x + max(1, (w - len(title)) // 2)
            put_text(start, y, title, "title")
            # Body lines within box
            max_lines = max(0, h - 2)
            for i, line in enumerate(frame.lines[:max_lines]):
                put_text(x + 1, y + 1 + i, line[: w - 2], "normal")
            # Hotkey hint in corner
            if frame.hotkey:
                put_text(x + 2, y, f"[{frame.hotkey.upper()}]", "hotkey")

        # Compose
        lines = ["".join(row) for row in surface]
        return lines, tags
