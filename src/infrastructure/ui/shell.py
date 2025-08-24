from __future__ import annotations
"""
Top-level UI shell for graphical launches (Infrastructure).

Modes:
- web: embed two web frames (HexiOS + HexiScope) via a local FastAPI server endpoints.
- desktop: render two Tk frames: desktop HexiOS (ASCII Text+keys) and desktop HexiScope (Canvas+mouse).
"""

import argparse
import os
import threading
import time
import webbrowser
from typing import Optional


def run_shell(mode: str = "desktop") -> None:
    if mode == "desktop":
        # Local imports to avoid Tk dependency when running in server-only mode
        import tkinter as tk
        from infrastructure.ui.hexiscope.desktop.tk_scope import run_hexiscope
        from infrastructure.ui.hexios.desktop.ascii_panel import run_hexios

        root = tk.Tk()
        root.title("HexiRules UI Shell (Desktop)")
        # Left: HexiOS (ASCII)
        left = tk.Frame(root)
        left.pack(side=tk.LEFT, fill=tk.Y)
        run_hexios(left)
        # Right: HexiScope (Canvas)
        right = tk.Frame(root)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        run_hexiscope(right)
        root.mainloop()
    elif mode == "web":
        # Start server if not running, then open browser to a simple HTML splitter page
        try:
            import uvicorn  # type: ignore
            from infrastructure.server.app import app
        except Exception:
            raise SystemExit("Web mode requires server dependencies (fastapi/uvicorn)")

        def serve() -> None:
            uvicorn.run(app, host=os.getenv("HEXI_HOST", "127.0.0.1"), port=int(os.getenv("HEXI_PORT", "8000")))

        t = threading.Thread(target=serve, daemon=True)
        t.start()
        time.sleep(0.6)
        # Open a basic split view page served by server or a fallback
        webbrowser.open(os.getenv("HEXI_URL", "http://127.0.0.1:8000"))
    else:
        raise SystemExit("Unknown mode for UI shell: " + mode)


def main(argv: Optional[list[str]] = None) -> None:
    p = argparse.ArgumentParser(description="HexiRules UI Shell")
    p.add_argument("--mode", choices=["desktop", "web"], default=os.getenv("HEXI_UI_MODE", "desktop"))
    args = p.parse_args(argv)
    run_shell(args.mode)


if __name__ == "__main__":
    main()
