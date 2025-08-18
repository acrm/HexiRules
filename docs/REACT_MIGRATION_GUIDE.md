# React Migration Guide (Local Smooth Dev)

This guide shows how to rewrite the Tk UI in React and run it locally with a smooth dev workflow.

## 1) Keep Python core; expose a web API

- Use the optional FastAPI server in `src/server` (already added).
- If not installed yet:
  - `pip install -r requirements-server.txt`
  - `python tools/run_server.py` → starts http://127.0.0.1:8000

Endpoints are described in `docs/ARCHITECTURE_SERVER.md`.

## 2) Scaffold React app (Vite + TypeScript)

- Create a sibling folder `web/` at repo root (outside `src/`):
  - `npm create vite@latest web -- --template react-ts`
  - `cd web`
  - `npm install`

Optional libs:
- `zustand` (state management)
- `swr` or `react-query` (data fetching)
- `@mantine/core` or `mui` (UI components)

## 3) Dev proxy to Python API

Create `web/vite.config.ts` with a proxy so the React dev server transparently hits FastAPI:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/session': 'http://127.0.0.1:8000',
      '/world': 'http://127.0.0.1:8000',
      '/worlds': 'http://127.0.0.1:8000',
      '/history': 'http://127.0.0.1:8000',
      '/step': 'http://127.0.0.1:8000',
    },
  },
})
```

Now in dev you can run both:
- Terminal 1: `python tools/run_server.py`
- Terminal 2: `cd web && npm run dev`

## 4) Minimal React structure

- `src/api/client.ts`: fetch wrappers for the API
- `src/state/useSession.ts`: create session, hold session_id
- `src/features/Worlds`, `Rules`, `History`, `Canvas` components
- `Canvas`: draw hex grid; for a fast start, render squares then upgrade to hex math later.

Suggested API contract in client:
- getHistory(): GET /history
- getLogs(i): GET /history/logs?index=i
- step(rules?): POST /step
- go(i), prev(), next()
- createWorld(name, radius, rules), listWorlds()

## 5) Smooth UX tips

- Use React Query (tanstack) for caching/refetch.
- Add debounce for rules editor, only POST on button click.
- Keep WebSocket for later; you can poll history after step during initial phase.

## 6) Build and serve via FastAPI (optional)

- `cd web && npm run build` → outputs `web/dist`
- The FastAPI app auto-serves `web/dist` if present. Then you can:
  - `python tools/run_server.py`
  - Open http://127.0.0.1:8000

## 7) Desktop “all-in-one” (later)

- Add `pywebview` as an optional dependency and open a window to the local server.
- Package with PyInstaller.

## 8) Incremental porting checklist

- [ ] Worlds list + create/select
- [ ] Rules editor + Progress button (step)
- [ ] History list + logs view (kept in sync)
- [ ] Canvas: display active cells; click to change state/direction
- [ ] Save/Load JSON
- [ ] WebSocket for live updates

That’s enough to run the React UI smoothly locally while the Python engine stays untouched.
