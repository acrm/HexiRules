from __future__ import annotations

import uuid
from typing import Dict

from application.world_service import WorldService


class SessionManager:
    """Simple in-memory session -> WorldService map.

    Not intended for production persistence, but fine for a single-process server.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, WorldService] = {}
        # WS connections map kept by app, not here, to avoid FastAPI imports.

    def create(self) -> str:
        sid = uuid.uuid4().hex
        self._sessions[sid] = WorldService()
        return sid

    def get(self, sid: str) -> WorldService:
        if sid not in self._sessions:
            # Auto-create to keep UX simple (optional)
            self._sessions[sid] = WorldService()
        return self._sessions[sid]

    def destroy(self, sid: str) -> None:
        self._sessions.pop(sid, None)
