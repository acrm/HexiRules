from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from domain.hexidirect.rule_engine import HexAutomaton
from .history import StepSnapshot


@dataclass
class World:
    name: str
    radius: int
    rules_text: str = ""
    hex: HexAutomaton = field(init=False)
    # History management
    history: List[StepSnapshot] = field(default_factory=list)
    history_index: int = 0

    def __post_init__(self) -> None:
        self.hex = HexAutomaton(radius=self.radius)
        if self.rules_text:
            rules: List[str] = [
                r.strip()
                for r in self.rules_text.replace(";", "\n").splitlines()
                if r.strip()
            ]
            self.hex.set_rules(rules)

    def rename(self, new_name: str) -> None:
        self.name = new_name

    def snapshot(self, logs: List[str], index: Optional[int] = None) -> StepSnapshot:
        """Create a snapshot of current active cells with logs.

        If index is None, uses current history length.
        """
        active_cells: List[Tuple[int, int, str, Optional[int]]] = []
        for (q, r), cell in self.hex.grid.items():
            if cell.state != "_":
                active_cells.append((q, r, cell.state, cell.direction))
        snap = StepSnapshot(
            index=index if index is not None else len(self.history),
            active_count=len(active_cells),
            logs=list(logs),
            cells=active_cells,
        )
        return snap

    def restore_snapshot(self, snap: StepSnapshot) -> None:
        """Restore grid from snapshot cells."""
        self.hex.clear()
        for q, r, s, d in snap.cells:
            self.hex.set_cell(q, r, s, d)
