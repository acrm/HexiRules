"""Hexagonal rule engine for HexiDirect rules."""

import random
import re
from typing import Dict, List, Match, Optional, Set, Tuple

from .models import HexCell, Condition
from .rule_parser import HexRule


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
        processed: List[str] = []
        for rule_str in rule_strings:
            processed.extend(self._expand_presets(rule_str))
        for rule_str in processed:
            try:
                # Expand macros first
                expanded_rules = self._expand_macros(rule_str)
            except ValueError as e:
                print(f"Warning: Skipping invalid rule '{rule_str}': {e}")
                continue
            for expanded_rule in expanded_rules:
                try:
                    self.rules.append(HexRule(expanded_rule))
                except ValueError as e:
                    print(
                        f"Warning: Skipping invalid expanded rule '{expanded_rule}': {e}"
                    )

    @staticmethod
    def _expand_presets(rule_str: str) -> List[str]:
        """Return preset HexiDirect rules or passthrough."""
        presets: Dict[str, List[str]] = {
            "B3/S23": [
                "_[a]3[_]3 => a",
                "a[a]2[a|_][_]3 => a",
                "a[_|a][_]5 | a[a]4[_|a][_|a] => _",
            ]
        }
        key = rule_str.strip().upper()
        if key in presets:
            return presets[key]
        return [rule_str]

    def _expand_macros(self, rule_str: str) -> List[str]:
        """Expand macro rules like 'x%' and '[y.]' into individual rules."""
        rules = [rule_str]

        if "=>" in rule_str:
            source_part, target_part = rule_str.split("=>", 1)
            source_part = source_part.strip()
            target_part = target_part.strip()

            # Normalize empty neighbor slots: replace [] with [_]
            # This helps users who type blank brackets to represent empty cells.
            source_part = source_part.replace("[]", "[_]")
            # Guard: if source is missing state and starts with a condition block, assume directionless '_'
            if source_part.startswith("["):
                source_part = "_" + source_part

            def expand_repeats(src: str) -> str:
                def repl(m: Match[str]) -> str:
                    block = m.group(1)
                    count = int(m.group(2))
                    return "".join(f"[{block}]" for _ in range(count))

                return re.sub(r"\[([^\]]+)\](\d+)", repl, src)

            source_part = expand_repeats(source_part)

            # First: expand top-level OR in the source, e.g.,
            #   "patternA | patternB => target" -> two separate rules
            # We must ignore '|' inside condition brackets [...].
            def split_top_level_or(src: str) -> List[str]:
                parts: List[str] = []
                buf: List[str] = []
                depth = 0
                i = 0
                while i < len(src):
                    ch = src[i]
                    if ch == "[":
                        depth += 1
                        buf.append(ch)
                    elif ch == "]":
                        depth = max(0, depth - 1)
                        buf.append(ch)
                    elif ch == "|" and depth == 0:
                        parts.append("".join(buf).strip())
                        buf = []
                    else:
                        buf.append(ch)
                    i += 1
                if buf:
                    parts.append("".join(buf).strip())
                # Filter out empty segments if any accidental doubles
                return [p for p in parts if p]

            src_options = split_top_level_or(source_part)
            if len(src_options) > 1:
                rules = [f"{opt} => {target_part}" for opt in src_options]
            else:
                rules = [f"{source_part} => {target_part}"]

            # Expand source % (any specified direction; do not include directionless)
            expanded_src: List[str] = []
            for base in rules:
                base_src, base_tgt = [p.strip() for p in base.split("=>", 1)]
                if re.search(r"([a-z_]+)%", base_src) and not re.search(
                    r"([a-z_]+)%", base_tgt
                ):
                    for direction in range(1, 7):

                        def _repl(m: Match[str], d: int = direction) -> str:
                            return f"{m.group(1)}{d}"

                        new_source = re.sub(
                            r"([a-z_]+)%",
                            _repl,
                            base_src,
                        )
                        expanded_src.append(f"{new_source} => {base_tgt}")
                else:
                    expanded_src.append(base)
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
        """Check if a cell matches the rule's condition groups."""
        if not rule.conditions:
            return True

        neighbors = self.get_neighbors(q, r)
        neighbor_cells = [self.get_cell(*pos) for pos in neighbors]

        def condition_matches(ncell: HexCell, cond: Condition) -> bool:
            state_ok = ncell.state == cond.state
            if cond.pointing_direction is not None:
                state_ok = state_ok and ncell.direction == cond.pointing_direction
            return not state_ok if cond.negated else state_ok

        used: Set[int] = set()

        def backtrack(index: int) -> bool:
            if index == len(rule.conditions):
                return True
            group = rule.conditions[index]
            for option in group:
                if option.direction is not None:
                    idx = option.direction - 1
                    if idx in used and not option.negated:
                        continue
                    ncell = neighbor_cells[idx]
                    if condition_matches(ncell, option):
                        if option.negated:
                            if backtrack(index + 1):
                                return True
                        else:
                            used.add(idx)
                            if backtrack(index + 1):
                                return True
                            used.remove(idx)
                else:
                    if option.negated:
                        if all(condition_matches(nc, option) for nc in neighbor_cells):
                            if backtrack(index + 1):
                                return True
                    else:
                        for idx, ncell in enumerate(neighbor_cells):
                            if idx in used:
                                continue
                            if condition_matches(ncell, option):
                                used.add(idx)
                                if backtrack(index + 1):
                                    return True
                                used.remove(idx)
            return False

        return backtrack(0)

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
