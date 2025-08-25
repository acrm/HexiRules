from __future__ import annotations

import os
from typing import List, Tuple, Optional, cast

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from application.world_service import WorldService
from infrastructure.server.session_manager import SessionManager
from infrastructure.server.schemas import (
    HistoryItem,
    LoadWorldRequest,
    SaveWorldRequest,
    StepRequest,
    WorldCreate,
    WorldSummary,
    RandomRequest,
    CellSetRequest,
    RenameRequest,
)

app = FastAPI(title="HexiRules Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = SessionManager()

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
HEXIOS_WEB_DIST = os.path.join(
    ROOT, "src", "infrastructure", "ui", "hexios", "web", "dist"
)
HEXISCOPE_WEB_DIST = os.path.join(
    ROOT, "src", "infrastructure", "ui", "hexiscope", "web", "dist"
)


@app.post("/session")
@app.get("/session")
def create_session() -> dict:
    sid = sessions.create()
    svc = sessions.get(sid)
    if not svc.worlds:
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
        try:
            active = sum(1 for cell in w.hex.grid.values() if cell.state != "_")
        except Exception:
            active = 0
        items.append(WorldSummary(name=name, radius=w.radius, active_count=active))
    return items


@app.post("/world/select")
def select_world(session_id: str, name: str) -> dict:
    svc = sessions.get(session_id)
    svc.select_world(name)
    return {"ok": True}


@app.post("/world/rename")
def rename_world(session_id: str, req: RenameRequest) -> dict:
    svc = sessions.get(session_id)
    svc.rename_world(req.old_name, req.new_name)
    return {"ok": True}


@app.post("/world/delete")
def delete_world(session_id: str, name: str) -> dict:
    svc = sessions.get(session_id)
    if name in svc.worlds:
        svc.delete_world(name)
        if svc.worlds and svc.current_world is None:
            next_name = sorted(svc.worlds.keys())[0]
            try:
                svc.select_world(next_name)
            except Exception:
                pass
    return {"ok": True}


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


@app.post("/cells/clear")
def cells_clear(session_id: str) -> dict:
    svc = sessions.get(session_id)
    svc.clear()
    return {"ok": True}


@app.post("/cells/random")
def cells_random(session_id: str, req: RandomRequest) -> dict:
    svc = sessions.get(session_id)
    svc.randomize(req.states, req.p)
    return {"ok": True}


@app.post("/cells/set")
def cells_set(session_id: str, req: CellSetRequest) -> dict:
    svc = sessions.get(session_id)
    svc.set_cell(req.q, req.r, req.state, req.direction)
    return {"ok": True}


@app.get("/cells/current")
def cells_current(session_id: str) -> List[Tuple[int, int, str, Optional[int]]]:
    svc = sessions.get(session_id)
    w = svc.get_current_world()
    out: List[Tuple[int, int, str, Optional[int]]] = []
    for (q, r), cell in w.hex.grid.items():
        if cell.state != "_":
            out.append((q, r, cell.state, cell.direction))
    return out


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


api_router = APIRouter()
api_router.add_api_route("/session", create_session, methods=["POST", "GET"])
api_router.add_api_route("/health", health, methods=["GET"])
api_router.add_api_route("/worlds", list_worlds, methods=["GET"])
api_router.add_api_route("/world/select", select_world, methods=["POST"])
api_router.add_api_route("/world/rename", rename_world, methods=["POST"])
api_router.add_api_route("/world/delete", delete_world, methods=["POST"])
api_router.add_api_route("/world", create_world, methods=["POST"])
api_router.add_api_route("/world/load", load_world, methods=["POST"])
api_router.add_api_route("/world/save", save_world, methods=["POST"])
api_router.add_api_route("/cells/clear", cells_clear, methods=["POST"])
api_router.add_api_route("/cells/random", cells_random, methods=["POST"])
api_router.add_api_route("/cells/set", cells_set, methods=["POST"])
api_router.add_api_route("/cells/current", cells_current, methods=["GET"])
api_router.add_api_route("/history", get_history, methods=["GET"])
api_router.add_api_route("/history/logs", get_logs, methods=["GET"])
api_router.add_api_route("/history/cells", get_cells, methods=["GET"])
api_router.add_api_route("/history/go", go_to, methods=["POST"])
api_router.add_api_route("/history/prev", prev, methods=["POST"])
api_router.add_api_route("/history/next", next_, methods=["POST"])
api_router.add_api_route("/step", step, methods=["POST"])

app.include_router(api_router, prefix="/api")

if os.path.isdir(HEXIOS_WEB_DIST):
    app.mount(
        "/hexios", StaticFiles(directory=HEXIOS_WEB_DIST, html=True), name="hexios-web"
    )
if os.path.isdir(HEXISCOPE_WEB_DIST):
    app.mount(
        "/hexiscope",
        StaticFiles(directory=HEXISCOPE_WEB_DIST, html=True),
        name="hexiscope-web",
    )
