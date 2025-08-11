"""
Hexagonal Rule Notation Parser and Engine
Implements the custom rule notation for hexagonal cellular automata
"""

import random
import re
from typing import Dict, List, Optional, Set, Tuple


class HexCell:
    """Represents a cell with state and optional direction."""

    def __init__(self, state: str = "_", direction: Optional[int] = None):
        self.state = state
        self.direction = direction

    def __str__(self) -> str:
        if self.direction is None:
            return self.state
        return f"{self.state}{self.direction}"

    def __repr__(self) -> str:
        return f"HexCell({self.state!r}, {self.direction!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HexCell):
            return False
        return self.state == other.state and self.direction == other.direction


class HexRule:
    """Represents a single hexagonal rule: source => target."""

    def __init__(self, rule_str: str):
        self.rule_str = rule_str
        self.source_state: str = ""
        # Source direction can be a specific int, with a separate flag for random direction.
        self.source_direction: Optional[int] = None
        self.source_random_direction: bool = False
        self.target_state: str = ""
        self.target_direction: Optional[int] = None
        self.target_rotation: Optional[int] = None
        self.condition_direction: Optional[int] = None
        self.condition_state: str = ""
        self.condition_pointing_direction: Optional[int] = None
        self.condition_negated: bool = False
        self.condition_pointing: bool = False
        self.condition_random_dir: bool = False
        self.parse_rule(rule_str)

    def parse_rule(self, rule_str: str) -> None:
        """Parse a rule string like 'a[1x] => b' or 'x% => y%5'."""
        try:
            source_part, target_part = rule_str.split("=>")
            source_part = source_part.strip()
            target_part = target_part.strip()

            # Parse source
            self._parse_source(source_part)

            # Parse target
            self._parse_target(target_part)

        except Exception as e:
            raise ValueError(f"Invalid rule syntax: {rule_str}") from e

    def _parse_source(self, source: str) -> None:
        """Parse source part like 'a3[1x]' or 'x%[y.]'."""
        # Check for condition block
        condition_match = re.search(r"\[([^\]]+)\]", source)
        if condition_match:
            condition = condition_match.group(1)
            source = source.replace(condition_match.group(0), "")
            self._parse_condition(condition)

        # Parse state and direction
        if source.endswith("%"):
            self.source_state = source[:-1]
            self.source_random_direction = True
        else:
            match = re.match(r"([a-z_]+)(\d+)?", source)
            if match:
                self.source_state = match.group(1)
                if match.group(2):
                    self.source_direction = int(match.group(2))

    def _parse_target(self, target: str) -> None:
        """Parse target part like 'b', 'y%5', or 'z.3'."""
        if "%" in target:
            # Handle rotation syntax like 'y%5'
            if target.endswith("%"):
                self.target_state = target[:-1]
                self.target_rotation = 0  # Same direction
            else:
                match = re.match(r"([a-z_]+)%(\d+)", target)
                if match:
                    self.target_state = match.group(1)
                    self.target_rotation = int(match.group(2))
        elif "." in target:
            # Handle incoming direction syntax like 'z.3'
            match = re.match(r"([a-z_]+)\.(\d+)", target)
            if match:
                self.target_state = match.group(1)
                self.target_direction = int(match.group(2))
        else:
            # Simple target like 'b' or 'b3'
            match = re.match(r"([a-z_]+)(\d+)?", target)
            if match:
                self.target_state = match.group(1)
                if match.group(2):
                    self.target_direction = int(match.group(2))

    def _parse_condition(self, condition: str) -> None:
        """Parse condition like '1x', '-a', 'y.', '1y4'."""
        # Check for negation
        if condition.startswith("-"):
            self.condition_negated = True
            condition = condition[1:]

        # Check for pointing marker
        if condition.endswith("."):
            self.condition_pointing = True
            condition = condition[:-1]
        elif condition.endswith("%"):
            self.condition_random_dir = True
            condition = condition[:-1]

        # Parse direction and state
        match = re.match(r"(\d+)?([a-z_]+)(\d+)?", condition)
        if match:
            if match.group(1):
                self.condition_direction = int(match.group(1))
            self.condition_state = match.group(2)
            if match.group(3):
                # Neighbor has specific pointing direction (like 1t4 - t points to direction 4)
                self.condition_pointing_direction = int(match.group(3))


class HexAutomaton:
    """Advanced hexagonal cellular automaton with custom rule notation."""

    def __init__(self, radius: int = 8):
        self.radius = radius
        self.grid: Dict[Tuple[int, int], HexCell] = {}
        self.rules: List[HexRule] = []
        self._init_empty_grid()

    def _init_empty_grid(self) -> None:
        """Initialize grid with empty cells."""
        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                if abs(q + r) <= self.radius:
                    self.grid[(q, r)] = HexCell("_")

    def set_rules(self, rule_strings: List[str]) -> None:
        """Set the rules for the automaton."""
        self.rules = []
        for rule_str in rule_strings:
            try:
                # Expand macros first
                expanded_rules = self._expand_macros(rule_str)
                for expanded_rule in expanded_rules:
                    self.rules.append(HexRule(expanded_rule))
            except ValueError as e:
                print(f"Warning: Skipping invalid rule '{rule_str}': {e}")

    def _expand_macros(self, rule_str: str) -> List[str]:
        """Expand macro rules like 'x%' and '[y.]' into individual rules."""
        rules = [rule_str]

        if "=>" in rule_str:
            source_part, target_part = rule_str.split("=>", 1)
            source_part = source_part.strip()
            target_part = target_part.strip()

            # Expand source % (any specified direction; do not include directionless)
            if re.search(r"([a-z_]+)%", source_part):
                # If both source and target have %, keep as-is for now
                if re.search(r"([a-z_]+)%", target_part):
                    pass
                else:
                    expanded_src: List[str] = []
                    for direction in range(1, 7):

                        new_source = re.sub(
                            r"([a-z_]+)%", 
                            lambda m, d=direction: f"{m.group(1)}{d}", 
                            source_part
                        )
                        expanded_src.append(f"{new_source} => {target_part}")
                    rules = expanded_src

        # Expand target at end
        final_rules: List[str] = []
        for rule in rules:
            src_part, tgt_part = [p.strip() for p in rule.split("=>", 1)]
            # Case 1: target ends with % => expand to 6 directions
            if re.search(r"^([a-z_]+)%$", tgt_part):
                base = tgt_part[:-1]
                for direction in range(1, 7):
                    final_rules.append(f"{src_part} => {base}{direction}")
                continue

            # Case 2: target has %N rotation
            m_rot = re.match(r"^([a-z_]+)%(\d+)$", tgt_part)
            if m_rot:
                target_state = m_rot.group(1)
                rot = int(m_rot.group(2)) % 6
                # Detect explicit source direction
                m_src = re.match(r"^([a-z_]+)(\d+)$", src_part)
                if m_src:
                    src_dir = int(m_src.group(2))
                    new_dir = ((src_dir + rot - 1) % 6) + 1
                    final_rules.append(f"{src_part} => {target_state}{new_dir}")
                else:
                    # No explicit source direction: branch to 6 variants
                    for d in range(1, 7):
                        final_rules.append(f"{src_part} => {target_state}{d}")
                continue

            # Otherwise leave as-is
            final_rules.append(rule)

        # Expand pointing conditions [state.] into six directional checks
        if re.search(r"\[[a-z_]+\.\]", rule_str):
            expanded_pointing: List[str] = []
            for rule in final_rules:
                pointing_match = re.search(r"\[([a-z_]+)\.\]", rule)
                if pointing_match:
                    state = pointing_match.group(1)
                    for direction in range(1, 7):
                        opposite_dir = ((direction + 3 - 1) % 6) + 1
                        new_rule = rule.replace(
                            f"[{state}.]", f"[{direction}{state}{opposite_dir}]"
                        )
                        expanded_pointing.append(new_rule)
                else:
                    expanded_pointing.append(rule)
            final_rules = expanded_pointing

        return final_rules

    def get_cell(self, q: int, r: int) -> HexCell:
        """Get cell at coordinates, return empty cell if out of bounds."""
        return self.grid.get((q, r), HexCell("_"))

    def set_cell(
        self, q: int, r: int, state: str, direction: Optional[int] = None
    ) -> None:
        """Set cell state and direction."""
        self.grid[(q, r)] = HexCell(state, direction)

    def toggle_cell(self, q: int, r: int) -> None:
        """Toggle cell between empty and active state."""
        cell = self.get_cell(q, r)
        if cell.state == "_":
            self.set_cell(q, r, "a", 1)  # Default active state with direction
        else:
            self.set_cell(q, r, "_")

    @staticmethod
    def get_neighbors(q: int, r: int) -> List[Tuple[int, int]]:
        """Get neighbor coordinates in clockwise order starting from upper-right."""
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [(q + dq, r + dr) for dq, dr in directions]

    def matches_condition(self, cell: HexCell, q: int, r: int, rule: HexRule) -> bool:
        """Check if a cell matches the rule's condition."""
        if not rule.condition_state:
            return True  # No condition

        neighbors = self.get_neighbors(q, r)

        if rule.condition_direction is not None:
            # Check specific direction
            direction_idx = rule.condition_direction - 1
            if 0 <= direction_idx < len(neighbors):
                neighbor_pos = neighbors[direction_idx]
                neighbor_cell = self.get_cell(*neighbor_pos)

                # Check if neighbor has the required state
                state_matches = neighbor_cell.state == rule.condition_state

                # If the condition specifies a pointing direction, check it
                if rule.condition_pointing_direction is not None:
                    # The neighbor must point in the specified direction
                    pointing_matches = (
                        neighbor_cell.direction == rule.condition_pointing_direction
                    )
                    if rule.condition_negated:
                        return not (state_matches and pointing_matches)
                    else:
                        return state_matches and pointing_matches
                else:
                    # No pointing direction specified, just check state
                    if rule.condition_negated:
                        return not state_matches
                    else:
                        return state_matches
            # If the specified direction is out of range, treat as missing neighbor
            # For a negated condition, missing neighbor satisfies the negation; otherwise, it fails
            return rule.condition_negated
        else:
            # Check any neighbor
            for neighbor_pos in neighbors:
                neighbor_cell = self.get_cell(*neighbor_pos)
                state_matches = neighbor_cell.state == rule.condition_state

                if rule.condition_pointing_direction is not None:
                    # The neighbor must point in the specified direction
                    pointing_matches = (
                        neighbor_cell.direction == rule.condition_pointing_direction
                    )
                    if state_matches and pointing_matches:
                        if rule.condition_negated:
                            return False
                        else:
                            return True
                else:
                    # No pointing direction specified, just check state
                    if state_matches:
                        if rule.condition_negated:
                            return False
                        else:
                            return True

            return rule.condition_negated

    def apply_rule(
        self, cell: HexCell, q: int, r: int, rule: HexRule
    ) -> Optional[HexCell]:
        """Apply a rule to a cell and return the new cell state."""
        # Check if source matches
        if rule.source_state != cell.state:
            return None

        # Handle source direction matching
        if not self._matches_source_direction(cell, rule):
            return None

        # Check condition
        if not self.matches_condition(cell, q, r, rule):
            return None

        # Apply transformation
        new_state = rule.target_state
        new_direction = None

        if rule.target_direction is not None:
            new_direction = rule.target_direction
        elif rule.target_rotation is not None:
            if cell.direction is not None:
                new_direction = ((cell.direction + rule.target_rotation - 1) % 6) + 1
            else:
                # Option A: if source has no direction, rotation keeps None
                new_direction = None
        # If neither target_direction nor target_rotation is specified,
        # new_direction stays None (removes direction)

        return HexCell(new_state, new_direction)

    def select_applicable_rules(
        self,
    ) -> Dict[Tuple[int, int], List[Tuple[HexRule, HexCell]]]:
        """Select expanded rules that apply to each cell."""
        selections: Dict[Tuple[int, int], List[Tuple[HexRule, HexCell]]] = {}
        for (q, r), cell in self.grid.items():
            for rule in self.rules:
                result = self.apply_rule(cell, q, r, rule)
                if result is not None:
                    selections.setdefault((q, r), []).append((rule, result))
        return selections

    def apply_random_rules(
        self, selections: Dict[Tuple[int, int], List[Tuple[HexRule, HexCell]]]
    ) -> None:
        """Apply one randomly chosen rule from selections to each cell."""
        new_grid: Dict[Tuple[int, int], HexCell] = {}
        for (q, r), cell in self.grid.items():
            candidates = selections.get((q, r), [])
            new_cell = cell
            if candidates:
                _, chosen_result = random.choice(candidates)
                new_cell = chosen_result
            new_grid[(q, r)] = new_cell
        self.grid = new_grid

    def step(self) -> None:
        """Advance the automaton by one generation."""
        selections = self.select_applicable_rules()
        self.apply_random_rules(selections)

    def _get_base_pattern(self, rule: HexRule) -> str:
        """Get the base pattern of a rule before macro expansion."""
        import re

        # Remove specific directions to get the base pattern
        pattern = rule.rule_str

        # Replace specific directions with % to identify base patterns
        # t1[-a] => t2 becomes t%[-a] => t%
        pattern = re.sub(r"([a-z_]+)\d+", r"\1%", pattern)
        # _[1t4] => a becomes _[%t%] => a
        pattern = re.sub(r"\[(\d+)([a-z_]+)(\d+)\]", r"[\2.]", pattern)

        return pattern

    def get_active_cells(self) -> Set[Tuple[int, int]]:
        """Get coordinates of all non-empty cells."""
        return {pos for pos, cell in self.grid.items() if cell.state != "_"}

    def clear(self) -> None:
        """Clear all cells to empty state."""
        for pos in self.grid:
            self.grid[pos] = HexCell("_")

    def _matches_source_direction(self, cell: HexCell, rule: HexRule) -> bool:
        """Check if the cell matches the rule's source direction requirements.

        Semantics:
        - source_random_direction (e.g., 'a%') matches any specified direction (1..6), not None.
        - source_direction (e.g., 'a3') matches only that specific direction.
        - no direction specified (e.g., 'a') matches only cells without a direction (None).
        """
        if rule.source_random_direction:
            return cell.direction is not None
        if rule.source_direction is not None:
            return cell.direction == rule.source_direction
        # No source direction specified
        return cell.direction is None
