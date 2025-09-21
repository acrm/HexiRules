from __future__ import annotations

from typing import List

from domain.worlds.world import World


def render_world_to_text(
    world: World, history_index: int, width: int, height: int
) -> str:
    """Render a simple monospaced text frame of the hex world.

    Notes:
    - Hex axial coords (q, r). We render rows by r with indentation to hint hex layout.
    - "_" (empty) becomes "."; other states use their first character.
    - Width/height are soft limits; we clip lines to `width` and number of lines to `height`.
    - This is engine-agnostic and side-effect free (pure function).
    """
    R = int(getattr(world, "radius", 10))
    # Header lines
    active = sum(1 for cell in world.hex.grid.values() if cell.state != "_")
    header = [
        f"HexiOS  r={R}  active={active}  idx={history_index}",
        "-" * 40,
    ]

    lines: List[str] = []
    # Render axial rows; for readability, limit to height - len(header)
    max_rows = max(0, height - len(header)) if height else None
    # Choose a compact axial bounding box
    r_min, r_max = -R, R
    for r in range(r_min, r_max + 1):
        # Indent to approximate hex staggering
        indent = " " * (R - (r - r_min) // 2)
        row_chars: List[str] = []
        for q in range(-R, R + 1):
            if abs(q + r) <= R:
                cell = world.hex.grid.get((q, r))
                ch = "."
                if cell is not None and cell.state != "_":
                    s = str(cell.state)
                    ch = s[0] if s else "?"
                row_chars.append(ch)
            else:
                # Outside hex; add space to keep visual alignment
                row_chars.append(" ")
        line = indent + " ".join(row_chars)
        if width:
            line = line[:width]
        lines.append(line)
        if max_rows and len(lines) >= max_rows:
            break

    frame = header + lines
    if height:
        frame = frame[:height]
    return "\n".join(frame)
