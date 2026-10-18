#!/usr/bin/env python3
"""Serve the Noemesis notebook on localhost using only the Python standard library."""

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"tools"))
from notebooks import PUBLIC, catalogue
from notebook_site import manifest, snapshot
from build_pages import SOURCE_URL, page

LIVE_SETTINGS = {'mode': 'live', 'revisionUrl': './revision', 'pollMs': 1000}


def render(root=ROOT, notebook_name="main", site_url=PUBLIC):
    """Render the published page content with localhost's live-reload transport settings."""
    return page(root, SOURCE_URL, notebook_name, site_url, LIVE_SETTINGS)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlsplit(self.path).path
        if route.startswith('/math-research/'):
            route=route[len('/math-research'):]
        try:
            items=catalogue(ROOT)
            name=None;leaf=None
            for item in items.values():
                prefix='/'+item['route']
                if route in (prefix,prefix+'index.html',prefix+'revision',prefix+'notebook-source.html'):
                    name=item['name'];leaf=route[len(prefix):];break
            if route=='/notebooks.json':
                body=json.dumps(manifest(ROOT)).encode();content_type='application/json'
            elif name is None:
                self.send_error(404);return
            else:
                rendered,notebook,revision=render(ROOT,name)
                if leaf=='revision':
                    body=json.dumps({'revision':revision}).encode();content_type='application/json'
                elif leaf=='notebook-source.html':
                    body=notebook.encode();content_type='text/html; charset=utf-8'
                else:
                    body=rendered.encode()
                    content_type='text/html; charset=utf-8'
        except (OSError,UnicodeError,ValueError):
            self.send_error(503,'Notebook is being saved or has invalid registration');return
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
    print(f"Noemesis notebook: http://localhost:{args.port}", flush=True)
    print("Edit notebook.html; the page offers a reload when it changes. Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
