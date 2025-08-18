# HexiRules Client/Server Architecture (Draft)

This document proposes a path to enable:
- Local single-app mode: desktop GUI embedding both client and server (like Minecraft launcher).
- LAN/Internet multiplayer: multiple web clients connect to a shared server.
- Zero-install web: host a server; users access via browser.

## Layers

- Core engine (existing): domain + application layers in `src/domain` and `src/application`.
- Server (new, optional): FastAPI app in `src/server`. Stateless per-request + in-memory sessions.
- Clients: 
  - Web SPA (future): React/Vite app consuming the HTTP/WebSocket API.
  - Desktop (existing Tk): can be kept or replaced by a webview shell.

## Sessions and Worlds

- SessionManager: maps a session_id to a `WorldService` instance (in-memory).
- Each session can manage multiple `World`s; one is current.
- Persistence: existing JSON repository; server exposes load/save endpoints.

## HTTP Endpoints

- POST /session → { session_id }
- GET /worlds?session_id=... → [ { name, radius, active_count } ]
- POST /world { name, radius, rules_text } → create
- POST /world/load { path } → load and select
- POST /world/save { path, rules_text } → save
- GET /history?session_id=... → [ { index, active_count } ]
- GET /history/logs?session_id=...&index=n → [ "..." ]
- POST /history/go?session_id=...&index=n
- POST /history/prev
- POST /history/next
- POST /step { rules_text? } → returns logs and appends snapshot

WebSocket for streaming updates can be added later (e.g., `/ws?session_id=...`).

## Dev and Deployment

- Install server deps only when needed: `requirements-server.txt`.
- Run locally:
  - `python -m server.run_server`  # starts FastAPI on 127.0.0.1:8000
- Serve web SPA (future) either from a static folder (FastAPI StaticFiles) or via separate CDN.

## Multiplayer Considerations

- Shared world: server hosts a single `WorldService` for a room; clients join by room ID.
- Concurrency: serialize `step` calls per room to avoid conflicts; use locks.
- Auth: add simple tokens per room; optional.
- Persistence: autosave snapshots to disk per N steps to allow rewind.

## Next Steps

1) Wire minimal React SPA scaffold (Vite + TS) outside Python runtime; connect to these endpoints.
2) Add WebSocket for live push of history updates and logs.
3) For desktop offline bundle, embed SPA via `pywebview` and run FastAPI in-process.
