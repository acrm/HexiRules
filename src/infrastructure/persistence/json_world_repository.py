import json
from pathlib import Path

from domain.worlds.world import World
from domain.worlds.history import StepSnapshot
from domain.worlds.repository import WorldRepository


class JsonWorldRepository(WorldRepository):
    """File-based JSON repository for worlds."""

    def save(self, world: World, path: Path) -> None:
        data = {
            "name": world.name,
            "radius": world.radius,
            "rules_text": world.rules_text,
            "hex_cells": [
                {"q": q, "r": r, "s": cell.state, "d": cell.direction}
                for (q, r), cell in world.hex.grid.items()
                if cell.state != "_"
            ],
            "history": [
                {
                    "index": s.index,
                    "active_count": s.active_count,
                    "logs": s.logs,
                    "cells": [
                        {"q": q, "r": r, "s": st, "d": d} for (q, r, st, d) in s.cells
                    ],
                }
                for s in world.history
            ],
            "history_index": world.history_index,
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: Path) -> World:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        name = data.get("name") or path.stem
        radius = int(data.get("radius", 8))
        rules_text = str(data.get("rules_text", ""))
        world = World(name=name, radius=radius, rules_text=rules_text)
        world.hex.clear()
        for item in data.get("hex_cells", []):
            world.hex.set_cell(
                int(item["q"]), int(item["r"]), str(item["s"]), item.get("d")
            )
        # load history if present
        history: list[StepSnapshot] = []
        for s in data.get("history", []):
            cells: list[tuple[int, int, str, int | None]] = [
                (int(c["q"]), int(c["r"]), str(c["s"]), c.get("d"))
                for c in s.get("cells", [])
            ]
            history.append(
                StepSnapshot(
                    index=int(s.get("index", len(history))),
                    active_count=int(s.get("active_count", len(cells))),
                    logs=[str(x) for x in s.get("logs", [])],
                    cells=cells,
                )
            )
        if history:
            world.history = history
            world.history_index = int(data.get("history_index", len(history)))
        return world
