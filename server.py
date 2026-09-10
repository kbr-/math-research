#!/usr/bin/env python3
"""Serve the math notebook on localhost using only the Python standard library."""

import argparse
import hashlib
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent


def snapshot(root=ROOT):
    template = (root / "index.html").read_text(encoding="utf-8")
    notebook = (root / "notebook.html").read_text(encoding="utf-8")
    revision = hashlib.sha256(json.dumps([template, notebook]).encode()).hexdigest()
    return template, notebook, revision


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlsplit(self.path).path
        if route not in ("/", "/index.html", "/revision"):
            self.send_error(404)
            return
        try:
            template, notebook, revision = snapshot()
        except (OSError, UnicodeError):
            self.send_error(503, "Notebook is being saved; try again shortly")
            return
        if route == "/revision":
            body = json.dumps({"revision": revision}).encode()
            content_type = "application/json"
        else:
            body = template.replace("__REVISION__", revision).replace(
                "<!-- NOTEBOOK -->", notebook
            ).encode("utf-8")
            content_type = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        if args and str(args[0]).startswith("GET /revision "):
            return
        super().log_message(format, *args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as error:
        parser.exit(1, f"Could not start server: {error}\nTry another port: --port 8001\n")
    print(f"Math notebook: http://localhost:{args.port}", flush=True)
    print("Edit notebook.html; the browser refreshes automatically. Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
