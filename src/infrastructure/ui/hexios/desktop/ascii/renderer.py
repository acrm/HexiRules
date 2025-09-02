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
    from .viewmodel import AsciiViewModel
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
        # We'll draw borders into a connectivity grid (bitmask per cell) then
        # translate that into box-drawing characters so adjacent frames share
        # proper connectors.
        bits_grid = [[0 for _ in range(W)] for _ in range(H)]
        # Bits: N=1, E=2, S=4, W=8
        N, E, S, Wb = 1, 2, 4, 8

        # Keep simple record of border ranges for tagging per line
        tags: List[List[Tuple[int, int, str]]] = [[] for _ in range(H)]

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

        frame_border_ranges = {}

        def mark_box(x: int, y: int, w: int, h: int, fid: str, sel: bool = False) -> None:
            # top row
            for xi in range(x, x + w):
                if xi == x:
                    bits_grid[y][xi] |= (E | S)
                elif xi == x + w - 1:
                    bits_grid[y][xi] |= (Wb | S)
                else:
                    bits_grid[y][xi] |= (E | Wb)
            # middle verticals
            for yy in range(y + 1, y + h - 1):
                bits_grid[yy][x] |= (N | S)
                bits_grid[yy][x + w - 1] |= (N | S)
            # bottom row
            if h > 1:
                by = y + h - 1
                for xi in range(x, x + w):
                    if xi == x:
                        bits_grid[by][xi] |= (E | N)
                    elif xi == x + w - 1:
                        bits_grid[by][xi] |= (Wb | N)
                    else:
                        bits_grid[by][xi] |= (E | Wb)

            # record ranges for tags
            branges = []
            branges.append((y, x, x + w, "border_sel" if sel else "border"))
            branges.append((y + h - 1, x, x + w, "border_sel" if sel else "border"))
            for yy in range(y + 1, y + h - 1):
                branges.append((yy, x, x + 1, "border_sel" if sel else "border"))
                branges.append((yy, x + w - 1, x + w, "border_sel" if sel else "border"))
            frame_border_ranges[fid] = branges

        # Mark bits for all frames first
        for fid, rect in layout_map.items():
            if fid not in frames_by_id:
                continue
            frame = frames_by_id[fid]
            x, y, w, h = rect
            sel = self.selection.mode == "frame" and self.selection.frame_id == fid
            mark_box(x, y, w, h, fid, sel)

        # Map bitmask to box-drawing char
        bits_to_char = {
            0: " ",
            N: "\u2502",
            S: "\u2502",
            E: "\u2500",
            Wb: "\u2500",
            N | S: "\u2502",
            E | Wb: "\u2500",
            N | E: "\u2514",  # up+right -> corner? will be adjusted
            N | Wb: "\u2518",
            S | E: "\u250c",
            S | Wb: "\u2510",
            N | E | Wb: "\u2524",
            S | E | Wb: "\u2534",
            N | S | E: "\u251c",
            N | S | Wb: "\u252c",
            N | S | E | Wb: "\u253c",
        }

        # Fallback helper: compute char from bits
        def char_for_bits(b: int) -> str:
            # Normalize symmetrical cases
            if b in bits_to_char:
                return bits_to_char[b]
            # try common combos
            if b & (E | Wb) and b & (N | S):
                return "\u253c"
            if b & (E | Wb):
                return "\u2500"
            if b & (N | S):
                return "\u2502"
            return " "

        # Build surface from bits
        surface = [[" " for _ in range(W)] for _ in range(H)]
        for y in range(H):
            for x in range(W):
                ch = char_for_bits(bits_grid[y][x])
                surface[y][x] = ch

        # Now overlay frame content (body lines) and titles/hotkeys, and record tags
        for fid, rect in layout_map.items():
            if fid not in frames_by_id:
                continue
            frame = frames_by_id[fid]
            x, y, w, h = rect
            # Title centered
            title = f" {frame.title} "
            start = x + max(1, (w - len(title)) // 2)
            for i, ch in enumerate(title):
                xi = start + i
                if 0 <= xi < self.layout.width and 0 <= y < self.layout.height:
                    surface[y][xi] = ch
            # Hotkey hint in corner
            if frame.hotkey:
                hk = f"[{frame.hotkey.upper()}]"
                for i, ch in enumerate(hk):
                    xi = x + 2 + i
                    if 0 <= xi < self.layout.width and 0 <= y < self.layout.height:
                        surface[y][xi] = ch
            # Body lines
            max_lines = max(0, h - 2)
            for i, line in enumerate(frame.lines[:max_lines]):
                yy = y + 1 + i
                if 0 <= yy < self.layout.height:
                    for j, ch in enumerate(line[: w - 2]):
                        xi = x + 1 + j
                        if 0 <= xi < self.layout.width:
                            surface[yy][xi] = ch
                    # tag whole content area line
                    tags[yy].append((x + 1, min(self.layout.width, x + w - 1), "normal"))

        # Collect border tags from recorded ranges
        for fid, branges in frame_border_ranges.items():
            for (yy, sx, ex, tag) in branges:
                if 0 <= yy < H:
                    tags[yy].append((sx, min(ex, W), tag))

        lines = ["".join(row) for row in surface]
        return lines, tags
