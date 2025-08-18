from __future__ import annotations

"""Run a standalone desktop app: start FastAPI in-process and open a webview.

Prereqs:
  pip install -r requirements-server.txt
  pip install pywebview==5.2

Build UI first (optional during dev):
  cd web && npm run build
Then run:
  python tools/run_desktop.py
"""

import os
from pathlib import Path
import threading
import time
import urllib.request
import sys
import traceback
import queue
import subprocess
import atexit
import shutil


def start_server(exc_out: "queue.Queue[str]") -> None:
    try:
        # Add src to path for module imports
        repo_root = Path(__file__).resolve().parents[1]
        src_path = str(repo_root / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        import uvicorn  # type: ignore
        from server.app import app  # type: ignore

        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False, log_level="info")
    except Exception:
        exc_out.put(traceback.format_exc())


def wait_for_health(url: str, timeout: float = 15.0, exc_in: queue.Queue[str] | None = None) -> None:
    start = time.time()
    while time.time() - start < timeout:
        # If server thread reported an exception, surface immediately
        if exc_in is not None and not exc_in.empty():
            err = exc_in.get_nowait()
            raise RuntimeError("Server failed to start:\n" + err)
        try:
            with urllib.request.urlopen(url) as resp:
                if resp.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(
        "Server health check timed out. Ensure dependencies are installed:\n"
        " - VS Code: use the 'Desktop' launch (runs 'Build: Desktop' automatically)\n"
        " - Or run tasks: 'Setup: Server deps' and 'Setup: Desktop deps'\n"
        " - Optionally build web UI (or the app will open API docs): 'Web: build'"
    )

def health_ok() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def _choose_url_and_maybe_start_dev(web_dir: Path, web_dist: Path) -> tuple[str, str, subprocess.Popen[bytes] | None]:
    """Return (url, mode, dev_proc). mode in {build, dev, docs, override}."""
    url_env = os.environ.get("HEXI_URL")
    dev_proc: subprocess.Popen[bytes] | None = None
    if url_env:
        print(f"[Desktop] Using HEXI_URL override: {url_env}")
        return url_env, "override", None
    if web_dist.is_dir():
        print("[Desktop] Found built web/dist; serving SPA from FastAPI static mount.")
        base = "http://127.0.0.1:8000"
        # Preflight check to avoid blank window if root isn't immediately ready
        for path in ("/", "/index.html"):
            try:
                with urllib.request.urlopen(base + path, timeout=2) as resp:
                    if resp.status == 200:
                        print(f"[Desktop] Build preflight OK at {base+path}")
                        return base + path, "build", None
            except Exception:
                pass
        print("[Desktop] Build preflight failed; falling back to API docs for visibility.")
        return "http://127.0.0.1:8000/docs", "build", None
    # Try to start Vite dev server if tooling is available
    npm = shutil.which("npm")
    local_vite = None
    # Look for local vite binary as an alternative path, especially on Windows
    bin_dir = web_dir / "node_modules" / ".bin"
    for cand in ("vite", "vite.cmd", "vite.CMD", "vite.exe"):
        p = bin_dir / cand
        if p.exists():
            local_vite = str(p)
            break
    if (npm or local_vite) and web_dir.is_dir() and (web_dir / "package.json").is_file():
        try:
            print("[Desktop] web/dist not found. Starting React dev server via 'npm run dev'...")
            dev_env = os.environ.copy()
            dev_env["BROWSER"] = "none"
            # Optionally allow enabling experimental webcrypto via env opt-in (not default as some Node versions disallow it)
            if os.environ.get("HEXI_ENABLE_EXPERIMENTAL_WEBCRYPTO") == "1":
                existing_node_opts = dev_env.get("NODE_OPTIONS", "").strip()
                extra_flag = "--experimental-global-webcrypto"
                if extra_flag not in existing_node_opts:
                    dev_env["NODE_OPTIONS"] = (existing_node_opts + " " + extra_flag).strip()
            if npm:
                dev_cmd = [npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"]
            else:
                print("[Desktop] npm not found; attempting to run local vite binary directly.")
                dev_cmd = [local_vite, "--host", "127.0.0.1", "--port", "5173"]  # type: ignore[list-item]
            dev_proc = subprocess.Popen(dev_cmd, cwd=str(web_dir), env=dev_env)
            atexit.register(lambda: dev_proc and dev_proc.terminate())
            start = time.time()
            reachable = False
            while time.time() - start < 15.0:
                try:
                    with urllib.request.urlopen("http://127.0.0.1:5173/", timeout=1) as resp:
                        if resp.status == 200:
                            print("[Desktop] Dev server is up at http://127.0.0.1:5173")
                            reachable = True
                            break
                except Exception:
                    time.sleep(0.3)
                # If the dev process has already exited, abort early
                if dev_proc.poll() is not None and dev_proc.returncode not in (0, None):
                    print(f"[Desktop] Dev server process exited with code {dev_proc.returncode}; aborting dev mode.")
                    break
            if reachable:
                return "http://127.0.0.1:5173", "dev", dev_proc
            # Not reachable: terminate dev and attempt build fallback
            try:
                dev_proc.terminate()
            except Exception:
                pass
            print("[Desktop] Dev server did not start in time; attempting a quick production build...")
            # fall through to build logic below by raising to reuse existing path
            raise RuntimeError("dev server not reachable")
        except Exception:
            print("[Desktop] Failed to start dev server; attempting a quick production build...")
            # Try a quick build to get web/dist, with a bounded timeout
            try:
                build_timeout = float(os.environ.get("HEXI_WEB_BUILD_TIMEOUT", "120"))
            except Exception:
                build_timeout = 120.0
            try:
                if npm:
                    build_cmd = [npm, "run", "build"]
                elif local_vite:
                    build_cmd = [local_vite, "build"]
                else:
                    raise RuntimeError("No npm or vite available for build")
                print(f"[Desktop] Running build with timeout {int(build_timeout)}s...")
                proc = subprocess.Popen(build_cmd, cwd=str(web_dir))
                # Poll for completion or dist presence
                start = time.time()
                while time.time() - start < build_timeout:
                    if proc.poll() is not None:
                        break
                    if web_dist.is_dir() and (web_dist / "index.html").exists():
                        break
                    time.sleep(0.5)
                try:
                    proc.terminate()
                except Exception:
                    pass
                if web_dist.is_dir() and (web_dist / "index.html").exists():
                    print("[Desktop] Build produced web/dist; serving SPA from FastAPI.")
                    return "http://127.0.0.1:8000", "build", None
                else:
                    print("[Desktop] Build did not complete in time; falling back to API docs.")
                    return "http://127.0.0.1:8000/docs", "docs", None
            except Exception as be:
                print(f"[Desktop] Build failed: {be}; falling back to API docs.")
                return "http://127.0.0.1:8000/docs", "docs", None
    else:
        if not npm:
            print("[Desktop] npm not found in PATH; cannot start dev server.")
        else:
            print("[Desktop] web folder or package.json missing; cannot start dev server.")
        return "http://127.0.0.1:8000/docs", "docs", None


def main() -> None:
    # Start FastAPI in a thread
    exc_q: queue.Queue[str] = queue.Queue()
    # If server already running, don't start another
    if not health_ok():
        t = threading.Thread(target=start_server, args=(exc_q,), daemon=True)
        t.start()
        # Wait for server to be ready with optional timeout override
        try:
            timeout = float(os.environ.get("HEXI_HEALTH_TIMEOUT", "10"))
        except Exception:
            timeout = 10.0
        try:
            wait_for_health("http://127.0.0.1:8000/health", exc_in=exc_q, timeout=timeout)
        except Exception:
            # If health didn't come up, still open docs to show status
            pass

    # Open webview pointing at served SPA (or dev server during development)
    try:
        import webview  # type: ignore
    except Exception as e:
        raise SystemExit("pywebview is required: pip install pywebview==5.2") from e

    title = os.environ.get("HEXI_TITLE", "HexiRules")
    root = Path(__file__).resolve().parents[1]
    web_dir = root / "web"
    web_dist = web_dir / "dist"

    # Probe-only modes for CI/diagnostics
    if "--probe" in sys.argv or "--probe-start-dev" in sys.argv:
        url, mode, dev_proc = _choose_url_and_maybe_start_dev(web_dir, web_dist)
        print(f"[Desktop] Probe: mode={mode} url={url}")
        # If probe only, terminate dev server if we started it and the caller didn't request to keep it
        if dev_proc and "--probe-start-dev" not in sys.argv:
            try:
                dev_proc.terminate()
            except Exception:
                pass
        return

    url, _mode, dev_proc = _choose_url_and_maybe_start_dev(web_dir, web_dist)
    window = webview.create_window(title, url)
    webview.start()


if __name__ == "__main__":
    main()
