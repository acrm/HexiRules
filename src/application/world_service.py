from __future__ import annotations

from pathlib import Path
import os
import shutil
from typing import Dict, Iterable, List, Optional, Tuple

from typing import cast

from domain.hexidirect.rule_engine import HexAutomaton
from domain.worlds.world import World
from infrastructure.persistence.json_world_repository import JsonWorldRepository
from domain.worlds.repository import WorldRepository
from domain.worlds.history import StepSnapshot


class WorldService:
    """Encapsulates world management and rule application logic."""

    def __init__(self, repository: Optional[WorldRepository] = None) -> None:
        self.repository: WorldRepository = repository or JsonWorldRepository()
        self.worlds: Dict[str, World] = {}
        self.current_world: Optional[str] = None
        # persistent data root (default: ./data). Worlds and state live here.
        # persistent worlds directory now under server data dir (default: ./data/worlds)
        data_root = Path(os.environ.get("HEXI_DATA_DIR", "data"))
        self.data_root: Path = data_root
        self.worlds_dir: Path = data_root / "worlds"
        self.worlds_dir.mkdir(parents=True, exist_ok=True)
        # app-level persistence file inside data dir
        self.state_file: Path = self.data_root / ".hexi_state.json"
        # migrate any legacy .hexi_worlds content if present
        self._maybe_migrate_legacy_worlds()
        # migrate legacy state file if present
        self._maybe_migrate_legacy_state()
        # Load any existing worlds from the persistence directory; if none, proceed to last_state load
        self._load_worlds_dir()
        self._load_last_state()

    # Worlds
    def create_world(
        self, name: str, radius: int, _is_hex: bool, rules_text: str
    ) -> None:
        world = World(name=name, radius=radius, rules_text=rules_text)
        self.worlds[name] = world
        # initialize history with initial state snapshot
        world.history.clear()
        world.history_index = 0
        init_snap = world.snapshot(["Initial state created"])  # index 0
        world.history.append(init_snap)
        world.history_index = 1
        self._persist_world(world)

    def select_world(self, name: str) -> World:
        if name not in self.worlds:
            raise KeyError(f"Unknown world: {name}")
        self.current_world = name
        self._save_last_state()
        return self.worlds[name]

    def get_current_world(self) -> World:
        if not self.current_world or self.current_world not in self.worlds:
            raise RuntimeError("No current world selected")
        return self.worlds[self.current_world]

    def current_automaton(self) -> HexAutomaton:
        return self.get_current_world().hex

    # Persistence
    def save_world_to_file(
        self, path: str, is_hexidirect: bool, rules_text: str
    ) -> None:
        world = self.get_current_world()
        world.rules_text = rules_text
        self.repository.save(world, Path(path))
        # remember last opened world path
        self._save_last_state(Path(path))

    def load_world_from_file(self, path: str) -> str:
        world = cast(World, self.repository.load(Path(path)))
        name = cast(str, world.name)
        self.worlds[name] = world
        # initialize history if empty
        if not world.history:
            init_snap = world.snapshot(["Loaded world"])  # index 0
            world.history = [init_snap]
            world.history_index = 1
        self.select_world(name)
        self._save_last_state(Path(path))
        return name

    # Rename world
    def rename_world(self, old_name: str, new_name: str) -> None:
        if not new_name or new_name in self.worlds:
            raise ValueError("Invalid or duplicate world name")
        if old_name not in self.worlds:
            raise KeyError(f"Unknown world: {old_name}")
        world = self.worlds.pop(old_name)
        world.rename(new_name)
        self.worlds[new_name] = world
        if self.current_world == old_name:
            self.current_world = new_name
        self._save_last_state()
        # rename on disk: delete old file if present, save new
        old_path = self.worlds_dir / f"{old_name}.json"
        try:
            if old_path.exists():
                old_path.unlink()
        except Exception:
            pass
        self._persist_world(world)
    
    def delete_world(self, name: str) -> None:
        if name in self.worlds:
            self.worlds.pop(name)
            try:
                (self.worlds_dir / f"{name}.json").unlink(missing_ok=True)  # type: ignore[arg-type]
            except Exception:
                pass
            if self.current_world == name:
                self.current_world = None
            self._save_last_state()

    # History APIs
    def history_add(self, logs: List[str]) -> StepSnapshot:
        w = self.get_current_world()
        idx = w.history_index
        snap = w.snapshot(logs, index=idx)
        # If we're not at the end, truncate forward history
        if idx < len(w.history):
            w.history = w.history[:idx]
        w.history.append(snap)
        w.history_index = idx + 1
        return snap

    def history_list(self) -> List[Tuple[int, int]]:
        """Return list of (index, active_count)."""
        w = self.get_current_world()
        return [(s.index, s.active_count) for s in w.history]

    def history_get_logs(self, index: int) -> List[str]:
        w = self.get_current_world()
        return list(w.history[index].logs) if 0 <= index < len(w.history) else []

    def history_get_cells(
        self, index: int
    ) -> List[Tuple[int, int, str, Optional[int]]]:
        w = self.get_current_world()
        if 0 <= index < len(w.history):
            return list(w.history[index].cells)
        return []

    def history_go(self, index: int) -> None:
        w = self.get_current_world()
        if not (0 <= index < len(w.history)):
            return
        snap = w.history[index]
        w.restore_snapshot(snap)
        w.history_index = index + 1

    def history_prev(self) -> None:
        w = self.get_current_world()
        target = max(0, w.history_index - 2)
        if w.history:
            self.history_go(target)

    def history_next(self) -> None:
        w = self.get_current_world()
        if w.history_index < len(w.history):
            self.history_go(w.history_index)

    def history_current_index(self) -> int:
        """Return the index of the currently active snapshot (selection).
        Internally, history_index points to the next insertion position, so the
        current selection is history_index - 1 clamped into [0, len-1].
        """
        w = self.get_current_world()
        if len(w.history) == 0:
            return -1
        # Ensure arithmetic stays in int domain for mypy clarity
        length: int = len(w.history)
        insertion: int = int(w.history_index)
        idx: int = max(0, min(length - 1, insertion - 1))
        return int(idx)

    # Internal state persistence
    def _load_last_state(self) -> None:
        try:
            if self.state_file.exists():
                import json

                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                # Restore by last opened file if present
                last_path = data.get("last_path")
                if last_path and Path(last_path).exists():
                    try:
                        name = self.load_world_from_file(last_path)
                        self.select_world(name)
                    except Exception:
                        pass
                # Otherwise, prefer selecting by last known world name if available
                last_world = data.get("last_world")
                if last_world and last_world in self.worlds:
                    try:
                        self.select_world(last_world)
                    except Exception:
                        pass
        except Exception:
            # best-effort only
            pass

    def _save_last_state(self, path: Optional[Path] = None) -> None:
        try:
            import json

            data = {"last_world": self.current_world}
            if path is not None:
                data["last_path"] = str(path)
            self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    # Editing and execution
    def clear(self) -> None:
        self.get_current_world().hex.clear()
        # persist change
        try:
            self._persist_world(self.get_current_world())
        except Exception:
            pass

    def randomize(self, states: Iterable[str], p: float = 0.3) -> None:
        import random

        w = self.get_current_world()
        R = int(w.radius)
        pool = [s for s in states if s != "_"]
        for q in range(-R // 2, R // 2 + 1):
            for r in range(-R // 2, R // 2 + 1):
                if abs(q + r) <= R // 2 and random.random() < p:
                    state = random.choice(pool) if pool else "a"
                    direction = random.choice([None, 1, 2, 3, 4, 5, 6])
                    w.hex.set_cell(q, r, state, direction)
        # persist change
        try:
            self._persist_world(w)
        except Exception:
            pass

    def set_cell(self, q: int, r: int, state: str, direction: Optional[int]) -> None:
        w = self.get_current_world()
        w.hex.set_cell(q, r, state, direction)
        try:
            self._persist_world(w)
        except Exception:
            pass

    def step(self, rules_text: str) -> List[str]:
        """Apply a single simulation step and return log messages."""
        logs: List[str] = []
        if not rules_text:
            return logs
        logs.append("=" * 50)
        logs.append("STEP: Starting new simulation step")

        w = self.get_current_world()
        rules: List[str] = []
        for line in rules_text.split("\n"):
            rules.extend([r.strip() for r in line.split(",") if r.strip()])
        if rules:
            w.rules_text = "\n".join(rules_text.split("\n"))
            logs.append(f"Rules: {rules}")
            w.hex.set_rules(rules)
            logs.append("Expanded rules:")
            for i, rule in enumerate(w.hex.rules, 1):
                logs.append(f"  {i}: {rule.rule_str}")
            active_cells = [
                f"({q},{r}):{cell}"
                for (q, r), cell in w.hex.grid.items()
                if cell.state != "_"
            ]
            logs.append(f"Active cells before step: {len(active_cells)}")
            for cell_info in active_cells[:10]:
                logs.append(f"  {cell_info}")
            if len(active_cells) > 10:
                logs.append(f"  ... and {len(active_cells) - 10} more")
            checked_count = 0
            match_count = 0
            hex_world = w.hex
            prev_active_set = {
                pos for pos, cell in hex_world.grid.items() if cell.state != "_"
            }
            for (q, r), cell in hex_world.grid.items():
                for rule in hex_world.rules:
                    checked_count += 1
                    if rule.source_state == cell.state and hex_world.matches_condition(
                        cell, q, r, rule
                    ):
                        match_count += 1
            logs.append(
                f"Checked {checked_count} rule-cell combinations, found {match_count} matches"
            )
            logs.append(
                "Note: When multiple rules from same macro match, one is chosen randomly"
            )
            # Before stepping, capture pre-step info if needed
            w.hex.step()
            new_active = [
                f"({q},{r}):{cell}"
                for (q, r), cell in w.hex.grid.items()
                if cell.state != "_"
            ]
            logs.append(f"Active cells after step: {len(new_active)}")
            for cell_info in new_active[:10]:
                logs.append(f"  {cell_info}")
            if len(new_active) > 10:
                logs.append(f"  ... and {len(new_active) - 10} more")
            new_active_set = {
                pos for pos, cell in w.hex.grid.items() if cell.state != "_"
            }
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
        # Add to history after step and return the same logs
        self.history_add(logs)
        return logs

    # Utilities
    def active_count(self) -> int:
        return len(self.get_current_world().hex.get_active_cells())

    # Persistence helpers
    def _persist_world(self, world: World) -> None:
        path = self.worlds_dir / f"{world.name}.json"
        self.repository.save(world, path)

    def _load_worlds_dir(self) -> None:
        try:
            for p in sorted(self.worlds_dir.glob("*.json")):
                try:
                    w = cast(World, self.repository.load(p))
                    self.worlds[w.name] = w
                except Exception:
                    pass
            # select any world if none selected
            if self.worlds and not self.current_world:
                self.current_world = sorted(self.worlds.keys())[0]
        except Exception:
            pass

    def _maybe_migrate_legacy_worlds(self) -> None:
        """Move worlds from legacy .hexi_worlds into data/worlds if needed.
        Only migrates when the new directory has no .json worlds yet.
        """
        try:
            legacy = Path(".hexi_worlds")
            if not legacy.exists() or not legacy.is_dir():
                return
            # If new dir already has worlds, do not migrate
            has_new = any((self.worlds_dir).glob("*.json"))
            if has_new:
                return
            for p in legacy.glob("*.json"):
                try:
                    shutil.move(str(p), str(self.worlds_dir / p.name))
                except Exception:
                    pass
            # Try to remove legacy dir if empty
            try:
                if not any(legacy.iterdir()):
                    legacy.rmdir()
            except Exception:
                pass
        except Exception:
            # best-effort migration
            pass

    def _maybe_migrate_legacy_state(self) -> None:
        """Move .hexi_state.json from project root into data directory if needed."""
        try:
            legacy = Path(".hexi_state.json")
            target = self.state_file
            if legacy.exists() and not target.exists():
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(legacy), str(target))
                except Exception:
                    pass
        except Exception:
            pass
