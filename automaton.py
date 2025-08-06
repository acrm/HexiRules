# Automaton logic separated from GUI for easier testing
from typing import Dict, Tuple, Iterable, Optional, Set
from hex_rules import HexAutomaton


class Automaton:
    """Hexagonal cellular automaton supporting both Conway-style and hex rule notation."""

    def __init__(self, radius: int = 8, rule: str = "B3/S23") -> None:
        self.radius = radius
        self.state: Dict[Tuple[int, int], int] = {}
        self.hex_automaton: Optional[HexAutomaton] = None
        self.use_hex_rules = False
        self.parse_rule(rule)

    def parse_rule(self, rule: str) -> None:
        """Parse a rule string - either Conway-style 'B3/S23' or hex notation."""
        rule = rule.strip()
        
        # Check if it's hex notation (contains '=>')
        if "=>" in rule:
            self.use_hex_rules = True
            self.hex_automaton = HexAutomaton(self.radius)
            
            # Split multiple rules by newlines or semicolons
            rule_lines = [r.strip() for r in rule.replace(';', '\n').split('\n') if r.strip()]
            self.hex_automaton.set_rules(rule_lines)
            self.rule = rule
            
            # Sync state from Conway format to hex format
            self._sync_to_hex()
        else:
            # Conway-style rule
            self.use_hex_rules = False
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

    def _sync_to_hex(self) -> None:
        """Sync Conway-style state to hex automaton."""
        if self.hex_automaton:
            self.hex_automaton.clear()
            for (q, r) in self.state:
                self.hex_automaton.set_cell(q, r, "a", 1)

    def _sync_from_hex(self) -> None:
        """Sync hex automaton state to Conway-style state."""
        if self.hex_automaton:
            self.state = {}
            active_cells = self.hex_automaton.get_active_cells()
            for pos in active_cells:
                self.state[pos] = 1

    def toggle_cell(self, q: int, r: int) -> None:
        """Toggle a cell between alive and dead."""
        if self.use_hex_rules and self.hex_automaton:
            self.hex_automaton.toggle_cell(q, r)
            self._sync_from_hex()
        else:
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
        if self.use_hex_rules and self.hex_automaton:
            self.hex_automaton.step()
            self._sync_from_hex()
        else:
            # Original Conway-style logic
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

    def get_cell_info(self, q: int, r: int) -> str:
        """Get detailed cell information for display."""
        if self.use_hex_rules and self.hex_automaton:
            cell = self.hex_automaton.get_cell(q, r)
            return str(cell)
        else:
            return "●" if (q, r) in self.state else "○"
    
    def get_cell_state(self, q: int, r: int) -> str:
        """Get cell state as string ('1' for alive, '0' for dead)."""
        if self.use_hex_rules and self.hex_automaton:
            cell = self.hex_automaton.get_cell(q, r)
            return "1" if cell.state != "_" else "0"
        else:
            return "1" if (q, r) in self.state else "0"
    
    def set_cell_state(self, q: int, r: int, state: str) -> None:
        """Set cell state from string ('1' for alive, '0' for dead)."""
        if self.use_hex_rules and self.hex_automaton:
            if state == "1":
                self.hex_automaton.set_cell(q, r, "a", 1)
            else:
                self.hex_automaton.set_cell(q, r, "_")
            self._sync_from_hex()
        else:
            key = (q, r)
            if state == "1":
                self.state[key] = 1
            elif key in self.state:
                del self.state[key]
    
    def clear(self) -> None:
        """Clear all cells."""
        if self.use_hex_rules and self.hex_automaton:
            self.hex_automaton.clear()
            self._sync_from_hex()
        else:
            self.state.clear()
    
    def set_rule(self, rule: str) -> None:
        """Set the rule for the automaton."""
        self.parse_rule(rule)
