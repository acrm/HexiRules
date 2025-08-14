#!/usr/bin/env python3
"""
Application controller for HexiRules.
Separates application/world logic from the Tkinter view.
"""

from typing import Any, Dict, List, Optional, Tuple, Iterable
import json
import os
from hex_rules import HexAutomaton


class HexiController:
    """Encapsulates world management and rule application logic."""

    def __init__(self) -> None:
        self.worlds: Dict[str, Dict[str, Any]] = {}
        self.current_world: Optional[str] = None

    # Worlds
    def create_world(self, name: str, radius: int, _is_hex: bool, rules_text: str) -> None:
        # _is_hex is ignored for backward compatibility; HexiDirect-only now.
        world: Dict[str, Any] = {
            "name": name,
            "radius": radius,
            "rules_text": rules_text,
            "hex": HexAutomaton(radius=radius),
        }
        if rules_text:
            rules = [
                r.strip()
                for r in rules_text.replace(";", "\n").split("\n")
                if r.strip()
            ]
            world["hex"].set_rules(rules)
        self.worlds[name] = world

    def select_world(self, name: str) -> Dict[str, Any]:
        if name not in self.worlds:
            raise KeyError(f"Unknown world: {name}")
        self.current_world = name
        return self.worlds[name]

    def get_current_world(self) -> Dict[str, Any]:
        if not self.current_world or self.current_world not in self.worlds:
            raise RuntimeError("No current world selected")
        return self.worlds[self.current_world]

    def current_automaton(self) -> HexAutomaton:
        w = self.get_current_world()
        return w["hex"]

    # Persistence
    def save_world_to_file(self, path: str, is_hexidirect: bool, rules_text: str) -> None:
        world = self.get_current_world()
        world["rules_text"] = rules_text
        data: Dict[str, Any] = {
            "name": world["name"],
            "radius": world["radius"],
            "is_hex": True,  # kept for backward compatibility
            "rules_text": world["rules_text"],
            "hex_cells": [
                {"q": q, "r": r, "s": cell.state, "d": cell.direction}
                for (q, r), cell in world["hex"].grid.items()
                if cell.state != "_"
            ],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_world_from_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        name = data.get("name") or os.path.splitext(os.path.basename(path))[0]
        radius = int(data.get("radius", 8))
        # Accept old files; ignore Conway fields
        rules_text = str(data.get("rules_text", ""))
        self.create_world(name, radius, True, rules_text)
        world = self.worlds[name]
        # populate
        world["hex"].clear()
        for item in data.get("hex_cells", []):
            world["hex"].set_cell(
                int(item["q"]), int(item["r"]), str(item["s"]), item.get("d")
            )
        self.select_world(name)
        return name

    # Editing and execution
    def clear(self) -> None:
        w = self.get_current_world()
        w["hex"].clear()

    def randomize(self, states: Iterable[str], p: float = 0.3) -> None:
        import random

        w = self.get_current_world()
        R = int(w.get("radius", 8))
        pool = [s for s in states if s != "_"]
        for q in range(-R // 2, R // 2 + 1):
            for r in range(-R // 2, R // 2 + 1):
                if abs(q + r) <= R // 2 and random.random() < p:
                    state = random.choice(pool) if pool else "a"
                    direction = random.choice([None, 1, 2, 3, 4, 5, 6])
                    w["hex"].set_cell(q, r, state, direction)

    def step(self, rules_text: str) -> List[str]:
        """Apply a single simulation step and return log messages to display."""
        logs: List[str] = []
        if not rules_text:
            return logs
        logs.append("=" * 50)
        logs.append("STEP: Starting new simulation step")

        w = self.get_current_world()
        # Parse rules
        rules: List[str] = []
        for line in rules_text.split("\n"):
            rules.extend([r.strip() for r in line.split(",") if r.strip()])
        if rules:
            # Persist
            w["rules_text"] = "\n".join(rules_text.split("\n"))
            logs.append(f"Rules: {rules}")
            w["hex"].set_rules(rules)
            logs.append("Expanded rules:")
            for i, rule in enumerate(w["hex"].rules, 1):
                logs.append(f"  {i}: {rule.rule_str}")
            active_cells = [
                f"({q},{r}):{cell}"
                for (q, r), cell in w["hex"].grid.items()
                if cell.state != "_"
            ]
            logs.append(f"Active cells before step: {len(active_cells)}")
            for cell_info in active_cells[:10]:
                logs.append(f"  {cell_info}")
            if len(active_cells) > 10:
                logs.append(f"  ... and {len(active_cells) - 10} more")
            # Analyze rule applications (summary only)
            checked_count = 0
            match_count = 0
            hex_world = w["hex"]
            prev_active_set = {pos for pos, cell in hex_world.grid.items() if cell.state != "_"}
            for (q, r), cell in hex_world.grid.items():
                for rule in hex_world.rules:
                    checked_count += 1
                    if (
                        rule.source_state == cell.state
                        and hex_world.matches_condition(cell, q, r, rule)
                    ):
                        match_count += 1
            logs.append(
                f"Checked {checked_count} rule-cell combinations, found {match_count} matches"
            )
            logs.append(
                "Note: When multiple rules from same macro match, one is chosen randomly"
            )
            w["hex"].step()
            new_active = [
                f"({q},{r}):{cell}"
                for (q, r), cell in w["hex"].grid.items()
                if cell.state != "_"
            ]
            logs.append(f"Active cells after step: {len(new_active)}")
            for cell_info in new_active[:10]:
                logs.append(f"  {cell_info}")
            if len(new_active) > 10:
                logs.append(f"  ... and {len(new_active) - 10} more")
            # Delta summary (HexiDirect)
            new_active_set = {pos for pos, cell in w["hex"].grid.items() if cell.state != "_"}
            births = new_active_set - prev_active_set
            survivals = new_active_set & prev_active_set
            deaths = prev_active_set - new_active_set
            logs.append(
                f"Summary: births={len(births)}, survivals={len(survivals)}, deaths={len(deaths)}"
            )
            if births:
                logs.append("Births (sample):")
                for pos in list(births)[:10]:
                    logs.append(f"  + ({pos[0]},{pos[1]})")
                if len(births) > 10:
                    logs.append(f"  ... and {len(births) - 10} more")
            if deaths:
                logs.append("Deaths (sample):")
                for pos in list(deaths)[:10]:
                    logs.append(f"  - ({pos[0]},{pos[1]})")
                if len(deaths) > 10:
                    logs.append(f"  ... and {len(deaths) - 10} more")

        logs.append("STEP: Completed")
        return logs

    # Utilities
    def active_count(self) -> int:
        w = self.get_current_world()
        return len(w["hex"].get_active_cells())
