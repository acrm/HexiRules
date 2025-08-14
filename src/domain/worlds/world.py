from dataclasses import dataclass, field
from typing import List

from domain.hexidirect.rule_engine import HexAutomaton


@dataclass
class World:
    name: str
    radius: int
    rules_text: str = ""
    hex: HexAutomaton = field(init=False)

    def __post_init__(self) -> None:
        self.hex = HexAutomaton(radius=self.radius)
        if self.rules_text:
            rules: List[str] = [
                r.strip()
                for r in self.rules_text.replace(";", "\n").splitlines()
                if r.strip()
            ]
            self.hex.set_rules(rules)
