import re
from typing import List, Optional

from .models import Condition


class HexRule:
    """Represents a single hexagonal rule: source => target."""

    def __init__(self, rule_str: str):
        self.rule_str = rule_str
        self.source_state: str = ""
        self.source_direction: Optional[int] = None
        self.source_random_direction: bool = False
        self.target_state: str = ""
        self.target_direction: Optional[int] = None
        self.target_rotation: Optional[int] = None
        self.condition_direction: Optional[int] = None
        self.condition_state: str = ""
        self.condition_pointing_direction: Optional[int] = None
        self.condition_negated: bool = False
        self.condition_random_dir: bool = False
        self.conditions: List[List[Condition]] = []
        self.parse_rule(rule_str)

    def parse_rule(self, rule_str: str) -> None:
        try:
            source_part, target_part = rule_str.split("=>")
            source_part = source_part.strip()
            target_part = target_part.strip()
            self._parse_source(source_part)
            self._parse_target(target_part)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Invalid rule syntax: {rule_str}") from e

    def _parse_source(self, source: str) -> None:
        condition_parts = re.findall(r"\[([^\]]+)\]", source)
        if condition_parts:
            source = re.sub(r"\[[^\]]+\]", "", source)
            for part in condition_parts:
                options = [self._parse_condition(opt) for opt in part.split("|")]
                self.conditions.append(options)
        if len(self.conditions) == 1 and len(self.conditions[0]) == 1:
            c = self.conditions[0][0]
            self.condition_direction = c.direction
            self.condition_state = c.state
            self.condition_pointing_direction = c.pointing_direction
            self.condition_negated = c.negated
            self.condition_random_dir = c.random_dir
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
        if "%" in target:
            if target.endswith("%"):
                self.target_state = target[:-1]
                self.target_rotation = 0
            else:
                match = re.match(r"([a-z_]+)%(\d+)", target)
                if match:
                    self.target_state = match.group(1)
                    self.target_rotation = int(match.group(2))
        elif "." in target:
            match = re.match(r"([a-z_]+)\.(\d+)", target)
            if match:
                self.target_state = match.group(1)
                self.target_direction = int(match.group(2))
        else:
            match = re.match(r"([a-z_]+)(\d+)?", target)
            if match:
                self.target_state = match.group(1)
                if match.group(2):
                    self.target_direction = int(match.group(2))

    def _parse_condition(self, condition: str) -> Condition:
        negated = False
        if condition.startswith("-"):
            negated = True
            condition = condition[1:]
        random_dir = False
        if condition.endswith("%"):
            random_dir = True
            condition = condition[:-1]
        match = re.match(r"(\d+)?([a-z_]+)(\d+)?", condition)
        direction: Optional[int] = None
        state = ""
        pointing_direction: Optional[int] = None
        if match:
            if match.group(1):
                direction = int(match.group(1))
            state = match.group(2)
            if match.group(3):
                pointing_direction = int(match.group(3))
        return Condition(
            state=state,
            direction=direction,
            pointing_direction=pointing_direction,
            negated=negated,
            random_dir=random_dir,
        )
