import os
import sys
import threading
import time
import urllib.request
import urllib.error


def main() -> int:
    # Ensure src/ is on sys.path
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_path = os.path.join(repo_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    try:
        from infrastructure.server.app import app, HEXIOS_WEB_DIST, HEXISCOPE_WEB_DIST
    except Exception as ex:
        print("Import error: cannot load FastAPI app:", ex)
        return 2

    print("HEXIOS_WEB_DIST:", HEXIOS_WEB_DIST, "exists:", os.path.isdir(HEXIOS_WEB_DIST))
    print(
        "HEXISCOPE_WEB_DIST:",
        HEXISCOPE_WEB_DIST,
        "exists:",
        os.path.isdir(HEXISCOPE_WEB_DIST),
    )

    try:
        import uvicorn
    except Exception as ex:
        print("Uvicorn not available:", ex)
        return 3

    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="debug")
    server = uvicorn.Server(config)

    t = threading.Thread(target=server.run, daemon=True)
    t.start()

    # Wait for server readiness
    base = "http://127.0.0.1:8000"
    for _ in range(50):
        try:
            with urllib.request.urlopen(base + "/api/health", timeout=0.2) as r:
                if r.status == 200:
                    break
        except Exception:
            time.sleep(0.1)

    paths = [
        "/",
        "/hexios/",
        "/hexios/index.html",
        "/hexiscope/",
        "/api/health",
        "/health",
    ]
    for p in paths:
        try:
            with urllib.request.urlopen(base + p, timeout=2) as r:
                ct = r.getheader("content-type")
                body = r.read(96)
                print(f"GET {p:18s} -> {r.status} {ct} sample={body[:72]!r}")
        except urllib.error.HTTPError as he:
            print(f"GET {p:18s} -> HTTP {he.code}")
        except Exception as e:
            print(f"GET {p:18s} -> ERROR {e}")

    # Shutdown
    server.should_exit = True
    for _ in range(20):
        if not t.is_alive():
            break
        time.sleep(0.1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
