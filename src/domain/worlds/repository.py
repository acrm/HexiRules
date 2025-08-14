from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .world import World


class WorldRepository(Protocol):
    def save(self, world: World, path: Path) -> None: ...

    def load(self, path: Path) -> World: ...
