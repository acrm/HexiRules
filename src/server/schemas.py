from __future__ import annotations

from typing import List, Optional, Tuple
from pydantic import BaseModel


class CellModel(BaseModel):
    q: int
    r: int
    state: str
    direction: Optional[int] = None


class SnapshotModel(BaseModel):
    index: int
    active_count: int
    logs: List[str]
    cells: List[Tuple[int, int, str, Optional[int]]]


class WorldCreate(BaseModel):
    name: str
    radius: int
    rules_text: str = ""


class StepRequest(BaseModel):
    rules_text: Optional[str] = None


class WorldSummary(BaseModel):
    name: str
    radius: int
    active_count: int


class HistoryItem(BaseModel):
    index: int
    active_count: int


class LoadWorldRequest(BaseModel):
    path: str


class SaveWorldRequest(BaseModel):
    path: str
    rules_text: str
