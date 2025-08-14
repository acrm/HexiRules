from dataclasses import dataclass
from typing import Optional


class HexCell:
    """Represents a cell with state and optional direction."""

    def __init__(self, state: str = "_", direction: Optional[int] = None) -> None:
        self.state = state
        self.direction = direction

    def __str__(self) -> str:
        return self.state if self.direction is None else f"{self.state}{self.direction}"

    def __repr__(self) -> str:
        return f"HexCell({self.state!r}, {self.direction!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HexCell):
            return False
        return self.state == other.state and self.direction == other.direction


@dataclass
class Condition:
    state: str
    direction: Optional[int] = None
    pointing_direction: Optional[int] = None
    negated: bool = False
    random_dir: bool = False
