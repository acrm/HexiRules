from __future__ import annotations

from typing import List, Tuple, Optional, cast

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from application.world_service import WorldService
from server.session_manager import SessionManager
from server.schemas import (
    HistoryItem,
    LoadWorldRequest,
    SaveWorldRequest,
    StepRequest,
    WorldCreate,
    WorldSummary,
)

app = FastAPI(title="HexiRules Server", version="0.1.0")

# CORS for local dev and simple hosting; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = SessionManager()


# Optionally serve built web client (Vite build) from web/dist
WEB_DIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "web", "dist"
)
if os.path.isdir(WEB_DIST):
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="static")


@app.post("/session")
def create_session() -> dict:
    sid = sessions.create()
    # seed a default world to simplify usage
    svc = sessions.get(sid)
    svc.create_world(name="World", radius=20, _is_hex=True, rules_text="")
    svc.select_world("World")
    return {"session_id": sid}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/worlds", response_model=List[WorldSummary])
def list_worlds(session_id: str) -> List[WorldSummary]:
    svc = sessions.get(session_id)
    items: List[WorldSummary] = []
    for name, w in svc.worlds.items():
        items.append(
            WorldSummary(name=name, radius=w.radius, active_count=svc.active_count())
        )
    return items


@app.post("/world")
def create_world(session_id: str, req: WorldCreate) -> dict:
    svc = sessions.get(session_id)
    if req.name in svc.worlds:
        raise HTTPException(status_code=400, detail="World already exists")
    svc.create_world(req.name, req.radius, _is_hex=True, rules_text=req.rules_text)
    return {"ok": True}


@app.post("/world/load")
def load_world(session_id: str, req: LoadWorldRequest) -> dict:
    svc = sessions.get(session_id)
    name = svc.load_world_from_file(req.path)
    svc.select_world(name)
    return {"name": name}


@app.post("/world/save")
def save_world(session_id: str, req: SaveWorldRequest) -> dict:
    svc = sessions.get(session_id)
    svc.save_world_to_file(req.path, is_hexidirect=True, rules_text=req.rules_text)
    return {"ok": True}


@app.get("/history", response_model=List[HistoryItem])
def get_history(session_id: str) -> List[HistoryItem]:
    svc = sessions.get(session_id)
    return [HistoryItem(index=i, active_count=c) for i, c in svc.history_list()]


@app.get("/history/logs")
def get_logs(session_id: str, index: int) -> List[str]:
    svc = sessions.get(session_id)
    logs: List[str] = svc.history_get_logs(index)
    return logs


@app.get("/history/cells")
def get_cells(session_id: str, index: int) -> List[Tuple[int, int, str, Optional[int]]]:
    svc = sessions.get(session_id)
    # Service returns List[Tuple[int,int,str,Optional[int]]]
    cells = cast(
        List[Tuple[int, int, str, Optional[int]]], svc.history_get_cells(index)
    )
    return cells


@app.post("/history/go")
def go_to(session_id: str, index: int) -> dict:
    svc = sessions.get(session_id)
    svc.history_go(index)
    return {"ok": True}


@app.post("/history/prev")
def prev(session_id: str) -> dict:
    svc = sessions.get(session_id)
    svc.history_prev()
    return {"ok": True}


@app.post("/history/next")
def next_(session_id: str) -> dict:
    svc = sessions.get(session_id)
    svc.history_next()
    return {"ok": True}


@app.post("/step")
def step(session_id: str, req: StepRequest) -> List[str]:
    svc = sessions.get(session_id)
    w = svc.get_current_world()
    rules_text = req.rules_text if req.rules_text is not None else w.rules_text
    return cast(List[str], svc.step(rules_text))
