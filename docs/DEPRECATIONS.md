# Deprecations and Redundancies

This document lists observed obsolete or redundant structures and the recommended canonical locations.

## Summary
- Duplicate UI trees (hexiscope/hexios) under both `src/ui` and `src/infrastructure/ui`.
- Two separate web frontends:
  - Canonical HexiOS web app (with Vite) at `src/infrastructure/ui/hexios/web`.
  - Another `web/` at repo root containing `src/` mirror but no build config.
- Empty directories left over from prior refactors: `src/ui/react/`, `src/ui/ascii/`, `src/ui/hexiscope/desktop/`.
- Committed artifacts: `server.log`, nested `dist/` and `node_modules/`.

## Recommendations
1. Canonicalize UI paths
   - Keep infrastructure-backed UI under `src/infrastructure/ui/` only.
   - Deprecate duplicates under `src/ui/*` for hexiscope/hexios. Migrate any live code to `src/infrastructure/ui/*` then remove empty folders.
   - Keep `src/infrastructure/ui/hexios/web` as the only web app. Deprecate top-level `web/` unless it serves a distinct purpose and is actively used by tasks.

2. Remove empty or dead folders
   - `src/ui/react/` (empty)
   - `src/ui/ascii/` (empty)
   - `src/ui/hexiscope/desktop/` (empty)

3. Strengthen ignore rules
   - Ignore nested `dist/`, `.vite/`, `coverage/`, `build/` and `server.log`.

4. Keep server code canonical
   - Use `src/infrastructure/server/` as the server implementation; the thin shim `src/server/run_server.py` can be retained temporarily but should reference the canonical server package.

## Proposed Cleanup Steps (non-destructive)
- Phase 1 (safe)
  - Update `.gitignore` for web artifacts and `server.log`. (Done)
  - Add this deprecation note. (Done)
- Phase 2 (after verification)
  - Delete empty folders listed above.
  - Archive or remove top-level `web/` once parity is confirmed with `src/infrastructure/ui/hexios/web` and tasks don’t depend on it.
  - Consolidate `src/ui/*` duplicates into `src/infrastructure/ui/*`.

## Notes
- Tests and tools currently pass; these changes target repo hygiene and do not alter runtime behavior.
- Before removals, search for imports or task references to any to-be-removed paths.
