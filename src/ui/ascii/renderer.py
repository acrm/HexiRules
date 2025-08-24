from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .viewmodel import AsciiViewModel, FrameVM

# Surface: 81x81
WIDTH = 81
HEIGHT = 51

LEFT_BORDER_COL = 0
CENTER_BORDER_COL = 40
RIGHT_BORDER_COL = 80
LEFT_CONTENT_START = 1
LEFT_CONTENT_END = 39
RIGHT_CONTENT_START = 41
RIGHT_CONTENT_END = 79

MAX_LOGICAL_ROWS = (HEIGHT - 1) // 2


@dataclass
class GridFrameSpec:
    id: str
    col: int  # 0 or 1
    row: int  # 0..MAX_LOGICAL_ROWS-1
    colspan: int = 1
    rowspan: int = 10


@dataclass
class GridLayoutSpec:
    frames: List[GridFrameSpec]

    @staticmethod
    def default_layout() -> "GridLayoutSpec":
        # Header row at 0, spans 2 columns (rowspan=1)
        # Footer at bottom (row = MAX_LOGICAL_ROWS-1), spans 2 columns (rowspan=1)
        body_top = 1
        body_band = 10
        return GridLayoutSpec(
            frames=[
                GridFrameSpec(id="header", col=0, row=0, colspan=2, rowspan=1),
                GridFrameSpec(id="worlds", col=0, row=body_top + 0 * body_band, rowspan=10),
                GridFrameSpec(id="rules", col=1, row=body_top + 0 * body_band, rowspan=10),
                GridFrameSpec(id="history", col=0, row=body_top + 1 * body_band, rowspan=10),
                GridFrameSpec(id="logs", col=1, row=body_top + 1 * body_band, rowspan=10),
                GridFrameSpec(id="selected", col=0, row=MAX_LOGICAL_ROWS - 2, colspan=2, rowspan=1),
                GridFrameSpec(id="footer", col=0, row=MAX_LOGICAL_ROWS - 1, colspan=2, rowspan=1),
            ]
        )


@dataclass
class SelectionState:
    mode: str  # "top" or "frame"
    frame_id: Optional[str] = None


class AsciiRenderer:
    def __init__(self, vm: AsciiViewModel, layout: GridLayoutSpec, selection: SelectionState):
        self.vm = vm
        self.layout = layout
        self.selection = selection
        self.vm_by_id: Dict[str, FrameVM] = {f.id: f for f in vm.frames}
        self.spec_by_id: Dict[str, GridFrameSpec] = {f.id: f for f in layout.frames}

    def render(self) -> Tuple[List[str], List[List[Tuple[int, int, str]]]]:
        canvas = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]
        tags: List[List[Tuple[int, int, str]]] = [[] for _ in range(HEIGHT)]

        def put(y: int, x: int, ch: str, tag: Optional[str] = None) -> None:
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                canvas[y][x] = ch
                if tag:
                    tags[y].append((x, x + 1, tag))

        def horiz(y: int, x1: int, x2: int, ch: str, tag: Optional[str] = None) -> None:
            for x in range(x1, x2 + 1):
                put(y, x, ch, tag)

        def vert(x: int, y1: int, y2: int, ch: str, tag: Optional[str] = None) -> None:
            for y in range(y1, y2 + 1):
                put(y, x, ch, tag)

        # Outer rectangle with corner glyphs
        horiz(0, LEFT_BORDER_COL + 1, RIGHT_BORDER_COL - 1, "═", tag="border")
        horiz(HEIGHT - 1, LEFT_BORDER_COL + 1, RIGHT_BORDER_COL - 1, "═", tag="border")
        vert(LEFT_BORDER_COL, 1, HEIGHT - 2, "║", tag="border")
        vert(RIGHT_BORDER_COL, 1, HEIGHT - 2, "║", tag="border")
        put(0, LEFT_BORDER_COL, "╔", tag="border")
        put(0, RIGHT_BORDER_COL, "╗", tag="border")
        put(HEIGHT - 1, LEFT_BORDER_COL, "╚", tag="border")
        put(HEIGHT - 1, RIGHT_BORDER_COL, "╝", tag="border")

        # Center column (draw everywhere; we'll override on header/footer rows later)
        vert(CENTER_BORDER_COL, 0, HEIGHT - 1, "║", tag="border")

        # Horizontal separators for frames
        sep_rows: Dict[int, List[GridFrameSpec]] = {}
        for spec in self.layout.frames:
            top_y = 2 * spec.row
            bottom_y = 2 * (spec.row + spec.rowspan)
            sep_rows.setdefault(top_y, []).append(spec)
            sep_rows.setdefault(bottom_y, []).append(spec)

        for y in sorted(set(sep_rows.keys())):
            if y <= 0 or y >= HEIGHT - 1:
                continue
            specs = sep_rows.get(y, [])
            spanning = any(s.colspan == 2 for s in specs)
            put(y, LEFT_BORDER_COL, "╠", tag="border")
            put(y, RIGHT_BORDER_COL, "╣", tag="border")
            if spanning:
                horiz(y, LEFT_BORDER_COL + 1, RIGHT_BORDER_COL - 1, "═", tag="border")
            else:
                put(y, CENTER_BORDER_COL, "╬", tag="border")
                horiz(y, LEFT_BORDER_COL + 1, CENTER_BORDER_COL - 1, "═", tag="border")
                horiz(y, CENTER_BORDER_COL + 1, RIGHT_BORDER_COL - 1, "═", tag="border")

        # Titles and content
        for spec in self.layout.frames:
            vm = self.vm_by_id.get(spec.id)
            if not vm:
                continue
            y_start = 2 * spec.row + 1
            y_end = 2 * (spec.row + spec.rowspan) - 1
            if y_start > y_end:
                continue

            if spec.colspan == 2:
                # header/footer line spanning both columns: suppress center divider
                put(y_start, CENTER_BORDER_COL, " ")
                text = vm.title[: (RIGHT_CONTENT_END - LEFT_CONTENT_START + 1)]
                x1 = LEFT_CONTENT_START
                for i, ch in enumerate(text):
                    put(y_start, x1 + i, ch, tag="title")
                continue

            x1 = LEFT_CONTENT_START if spec.col == 0 else RIGHT_CONTENT_START
            x2 = LEFT_CONTENT_END if spec.col == 0 else RIGHT_CONTENT_END

            title = f"[{vm.hotkey.upper()}] {vm.title}" if vm.hotkey else vm.title
            title = title[: (x2 - x1 + 1)]
            for i, ch in enumerate(title):
                tag = "hotkey" if vm.hotkey and 0 <= i <= 2 else "title"
                put(y_start, x1 + i, ch, tag=tag)

            content_lines = vm.lines[: max(0, (y_end - y_start))]
            for idx, line in enumerate(content_lines):
                y = y_start + 1 + idx
                if y > y_end:
                    break
                text = line[: (x2 - x1 + 1)].ljust(x2 - x1 + 1)
                for i, ch in enumerate(text):
                    put(y, x1 + i, ch)

        # Selection overlay
        sel = self.selection
        if sel.mode == "top":
            horiz(0, LEFT_BORDER_COL + 1, RIGHT_BORDER_COL - 1, "═", tag="border_sel")
            horiz(HEIGHT - 1, LEFT_BORDER_COL + 1, RIGHT_BORDER_COL - 1, "═", tag="border_sel")
            vert(LEFT_BORDER_COL, 1, HEIGHT - 2, "║", tag="border_sel")
            vert(RIGHT_BORDER_COL, 1, HEIGHT - 2, "║", tag="border_sel")
            put(0, LEFT_BORDER_COL, "╔", tag="border_sel")
            put(0, RIGHT_BORDER_COL, "╗", tag="border_sel")
            put(HEIGHT - 1, LEFT_BORDER_COL, "╚", tag="border_sel")
            put(HEIGHT - 1, RIGHT_BORDER_COL, "╝", tag="border_sel")
        elif sel.mode == "frame" and sel.frame_id in self.spec_by_id:
            spec = self.spec_by_id[sel.frame_id]
            top_y = 2 * spec.row
            bottom_y = 2 * (spec.row + spec.rowspan)
            left_x = LEFT_BORDER_COL if spec.col == 0 or spec.colspan == 2 else CENTER_BORDER_COL
            right_x = RIGHT_BORDER_COL if spec.colspan == 2 or spec.col == 1 else CENTER_BORDER_COL
            put(top_y, left_x, "╔", tag="border_sel")
            put(top_y, right_x, "╗", tag="border_sel")
            put(bottom_y, left_x, "╚", tag="border_sel")
            put(bottom_y, right_x, "╝", tag="border_sel")
            horiz(top_y, left_x + 1, right_x - 1, "═", tag="border_sel")
            horiz(bottom_y, left_x + 1, right_x - 1, "═", tag="border_sel")
            vert(left_x, top_y + 1, bottom_y - 1, "║", tag="border_sel")
            vert(right_x, top_y + 1, bottom_y - 1, "║", tag="border_sel")

        # Ensure outer top/bottom borders remain continuous (no center divider)
        put(0, CENTER_BORDER_COL, "═", tag="border")
        put(HEIGHT - 1, CENTER_BORDER_COL, "═", tag="border")

        lines = ["".join(row) for row in canvas]
        lines = [ln[:WIDTH].ljust(WIDTH) for ln in lines]
        return lines, tags
