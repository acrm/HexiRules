from __future__ import annotations

import time
import uuid
from typing import Dict, Tuple

from application.world_service import WorldService


class SessionManager:
    """Simple in-memory session -> WorldService map with expiry."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._sessions: Dict[str, Tuple[WorldService, float]] = {}
        self._ttl = float(ttl_seconds)

    def create(self) -> str:
        sid = uuid.uuid4().hex
        self._sessions[sid] = (WorldService(), time.time())
        self.prune()
        return sid

    def get(self, sid: str) -> WorldService:
        self.prune()
        if sid not in self._sessions:
            self._sessions[sid] = (WorldService(), time.time())
        svc, _ = self._sessions[sid]
        self._sessions[sid] = (svc, time.time())
        return svc

    def destroy(self, sid: str) -> None:
        self._sessions.pop(sid, None)

    def prune(self) -> None:
        cutoff = time.time() - self._ttl
        stale = [sid for sid, (_, ts) in self._sessions.items() if ts < cutoff]
        for sid in stale:
            self._sessions.pop(sid, None)
