"""
CLI Entrypoint for EnvMan
=========================

WHY: TECHNICAL_SPEC.md Phase 3 & Summary goals specify EnvMan as a standalone
     single-binary / CLI package. Developers run `envman` to launch the server
     and automatically open the UI in a browser without managing two separate
     dev servers.

WHAT:
    - Parses command-line arguments (--host, --port, --no-browser)
    - Starts the FastAPI server programmatically via uvicorn.run()
    - Opens a browser tab once the server is ready (unless --no-browser is set)
"""

import argparse
import threading
import time
import urllib.request
import webbrowser
import uvicorn
from app.main import app


def _open_browser_when_ready(url: str, timeout: float = 5.0) -> None:
    """Poll the health check endpoint, then open the browser."""
    health_url = f"{url}/health"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(health_url)
            with urllib.request.urlopen(req, timeout=0.5) as resp:
                if resp.status == 200:
                    break
        except Exception:
            pass
        time.sleep(0.1)

    webbrowser.open(url)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="envman",
        description="EnvMan — Deterministic Developer Environment Platform",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind the server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open browser automatically on start",
    )

    args = parser.parse_args()

    browser_host = "localhost" if args.host in ("0.0.0.0", "127.0.0.1") else args.host
    url = f"http://{browser_host}:{args.port}"

    if not args.no_browser:
        threading.Thread(
            target=_open_browser_when_ready,
            args=(url,),
            daemon=True,
        ).start()

    print(f"Starting EnvMan at {url} ...")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
