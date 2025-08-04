# Automaton logic separated from GUI for easier testing
from typing import Dict, Tuple, Iterable


class Automaton:
    """Hexagonal cellular automaton following rules like B3/S23."""

    def __init__(self, rule: str = "B3/S23") -> None:
        self.state: Dict[Tuple[int, int], int] = {}
        self.parse_rule(rule)

    def parse_rule(self, rule: str) -> None:
        """Parse a rule string like "B3/S23" into birth and survive lists."""
        try:
            birth, survive = rule.split("/")
            self.birth = [int(n) for n in birth[1:]]
            self.survive = [int(n) for n in survive[1:]]
            self.rule = rule
        except Exception:
            # Fallback to classic Game of Life on hex grid
            self.birth = [3]
            self.survive = [2, 3]
            self.rule = "B3/S23"

    def toggle_cell(self, q: int, r: int) -> None:
        """Toggle a cell between alive and dead."""
        key = (q, r)
        if key in self.state:
            del self.state[key]
        else:
            self.state[key] = 1

    @staticmethod
    def neighbors(q: int, r: int) -> Iterable[Tuple[int, int]]:
        """Yield axial coordinates of neighboring cells."""
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        for dq, dr in directions:
            yield q + dq, r + dr

    def step(self) -> None:
        """Advance the automaton by one generation."""
        counts: Dict[Tuple[int, int], int] = {}
        for q, r in self.state:
            for nq, nr in self.neighbors(q, r):
                counts[(nq, nr)] = counts.get((nq, nr), 0) + 1
        new_state: Dict[Tuple[int, int], int] = {}
        for cell, count in counts.items():
            if cell in self.state:
                if count in self.survive:
                    new_state[cell] = 1
            else:
                if count in self.birth:
                    new_state[cell] = 1
        self.state = new_state
