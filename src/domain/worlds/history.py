from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class StepSnapshot:
    """Snapshot of a world's state at a specific step.

    Stores only active cells for compactness.
    """

    index: int
    active_count: int
    logs: List[str]
    # Each cell: (q, r, state, direction)
    cells: List[Tuple[int, int, str, Optional[int]]]
