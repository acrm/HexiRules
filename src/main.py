#!/usr/bin/env python3
"""
HexiRules - Hexagonal Cellular Automaton

Unified launcher for all run modes:
    - py-gui: Tk HexiScope + ASCII HexiOS (embedded controller)
    - react-desktop: Embedded browser window hosting the React HexiOS + Canvas HexiScope
                                     backed by the local FastAPI server
    - ascii-cli: ASCII HexiOS only (interactive), prints ASCII control panel and accepts commands
    - cli: pure CLI without any UI (existing commands-based shell)

Also exposes a minimal HexCanvas helper used by geometry-focused tests.
"""

import importlib
import os
import shutil
import subprocess
import math
from typing import Dict, Tuple, List, Any

try:
    import tkinter as tk  # Only needed when tests instantiate the canvas
except Exception:  # pragma: no cover - allow headless import
    tk = None  # type: ignore[assignment]


class HexCanvas:
    """A lightweight hex grid canvas providing geometry helpers for tests.

    This class is intentionally minimal and independent from the main GUI.
    Tests use it to validate coordinate conversions and hex polygon math.
    """

    def __init__(self, root: Any, radius: int = 3, cell_size: int = 20) -> None:
        if tk is None:
            raise RuntimeError("Tkinter not available")
        self.root = root
        self.radius = radius
        self.cell_size = cell_size

        # Compute a canvas size that safely fits a hex grid of the given radius
        grid_w = int((3 * self.cell_size / 2) * (2 * radius) + 2 * self.cell_size + 20)
        grid_h = int((math.sqrt(3) * self.cell_size) * (2 * radius + 1) + 20)
        self.center_x = grid_w // 2
        self.center_y = grid_h // 2

        self.canvas = tk.Canvas(root, width=grid_w, height=grid_h)

        # Precompute cell centers for axial coordinates within the radius
        self.cells: Dict[Tuple[int, int], Tuple[int, int]] = {}
        for q in range(-radius, radius + 1):
            r_min = max(-radius, -q - radius)
            r_max = min(radius, -q + radius)
            for r in range(r_min, r_max + 1):
                x, y = self.axial_to_pixel(q, r)
                self.cells[(q, r)] = (x, y)

    def axial_to_pixel(self, q: int, r: int) -> Tuple[int, int]:
        """Convert axial (q, r) to pixel coordinates (pointy-top grid structure)."""
        x = self.center_x + int(round(self.cell_size * (3 / 2) * q))
        y = self.center_y + int(round(self.cell_size * math.sqrt(3) * (r + q / 2)))
        return x, y

    def polygon_corners(self, cx: int, cy: int) -> List[int]:
        """Return the 6-point polygon around (cx, cy) as a flat list of 12 ints."""
        pts: List[int] = []
        # flat-top hexagon cells: start at 0 degrees and step by 60 degrees
        for i in range(6):
            angle_rad = math.radians(60 * i)
            x = cx + self.cell_size * math.cos(angle_rad)
            y = cy + self.cell_size * math.sin(angle_rad)
            pts.extend([int(round(x)), int(round(y))])
        return pts


def _run_py_gui() -> None:
    gui_mod = importlib.import_module("infrastructure.ui.hexiscope.tk.gui_app")
    gui = gui_mod.create_gui()
    gui.run()


def _run_react_desktop() -> None:
    """Launch FastAPI server and open a desktop window with the React UI.

    Requires server dependencies (fastapi/uvicorn) and pywebview for the desktop window.
    Falls back to opening a browser if pywebview is unavailable.
    """
    import threading
    import time
    import webbrowser
    import urllib.request
    import urllib.error

    def _ensure_web_build(force: bool = False) -> None:
        """Ensure the HexiOS web UI is built into dist/ before server start.

        - If npm is available, run `npm ci` and `npm run build` in the web folder when dist is missing or force is True.
        - If npm is not available, print guidance and continue (server can still run without UI).
        """
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        web_dir = os.path.join(repo_root, "infrastructure", "ui", "hexios", "web")
        dist_dir = os.path.join(web_dir, "dist")
        index_html = os.path.join(dist_dir, "index.html")

        if not os.path.isdir(web_dir):
            print("[react-desktop] Web folder not found; skipping web build.")
            return

        need_build = force or (not os.path.isfile(index_html))
        if not need_build:
            try:
                assets_dir = os.path.join(dist_dir, "assets")
                need_build = not (os.path.isdir(assets_dir) and os.listdir(assets_dir))
            except Exception:
                need_build = True

        if not need_build:
            return

        npm = shutil.which("npm") or shutil.which("npm.cmd")
        if not npm:
            print("[react-desktop] npm not found; cannot build React UI. Install Node.js LTS to enable auto-build.")
            print("[react-desktop] Continue without web UI, or prebuild at src/infrastructure/ui/hexios/web.")
            return

        print("[react-desktop] Building HexiOS web UI (npm ci && npm run build)…")
        try:
            subprocess.run([npm, "ci"], cwd=web_dir, check=True)
            subprocess.run([npm, "run", "build"], cwd=web_dir, check=True)
            print("[react-desktop] Web build complete.")
        except subprocess.CalledProcessError as e:
            print("[react-desktop] Web build failed:", e)
        except Exception as e:
            print("[react-desktop] Unexpected error during web build:", e)

    try:
        import uvicorn
        from infrastructure.server.app import app  # FastAPI application
    except Exception as ex:  # pragma: no cover - optional path
        print("React desktop requires server deps (fastapi/uvicorn).", ex)
        return

    def serve() -> None:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

    # Optionally force a rebuild via env var HEXIOS_REBUILD=1
    _ensure_web_build(force=os.getenv("HEXIOS_REBUILD") == "1")

    t = threading.Thread(target=serve, daemon=True)
    t.start()
    # Wait briefly for the server to start
    for _ in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=0.25):
                break
        except Exception:
            time.sleep(0.1)

    # Open HexiOS React app if present, otherwise root (which redirects suitably)
    url = "http://127.0.0.1:8000/hexios/"
    try:
        req = urllib.request.Request(url, method="GET")
        urllib.request.urlopen(req, timeout=0.5).close()
    except Exception:
        url = "http://127.0.0.1:8000/"
    print(f"[react-desktop] Opening URL: {url}")
    try:
        with urllib.request.urlopen(url, timeout=1.0) as r:
            print(
                "[react-desktop] Probe:", r.status, r.getheader("content-type")
            )
    except Exception as ex:
        print("[react-desktop] Probe error:", ex)

    try:
        import webview

        webview.create_window("HexiRules", url)
        webview.start()
    except Exception:
        print("pywebview not installed; opening in default browser.")
        webbrowser.open(url)


def _run_ascii_cli() -> None:
    from infrastructure.ui.hexios.desktop.ascii.facade import AsciiControlPanel
    from application.world_service import WorldService

    controller = WorldService()
    panel = AsciiControlPanel(controller, quit_callback=lambda: None)
    # Render once for immediate feedback, then accept commands from stdin
    print(panel.render())
    panel.run()


def _run_pure_cli(argv: List[str] | None = None) -> None:
    # Delegate to the existing CLI tool
    from cli import main as cli_main

    cli_main(argv)


def main(argv: List[str] | None = None) -> None:
    """Main entry point for HexiRules launcher."""
    import sys
    import os
    import argparse

    # Add current directory to path if not already there
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    parser = argparse.ArgumentParser(description="HexiRules unified launcher")
    parser.add_argument(
        "--mode",
        choices=["py-gui", "react-desktop", "ascii-cli", "cli"],
        default=os.getenv("HEXIRULES_MODE", "py-gui"),
        help="Run mode: Tk GUI, React desktop, ASCII CLI, or pure CLI",
    )
    # Pass-through arguments for pure CLI when selected
    parser.add_argument("cli_args", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)

    args = parser.parse_args(argv)

    if args.mode == "py-gui":
        _run_py_gui()
    elif args.mode == "react-desktop":
        _run_react_desktop()
    elif args.mode == "ascii-cli":
        _run_ascii_cli()
    elif args.mode == "cli":
        _run_pure_cli(args.cli_args)
    else:  # pragma: no cover - defensive default
        _run_py_gui()


if __name__ == "__main__":
    main()
