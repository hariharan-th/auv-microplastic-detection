from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

log = logging.getLogger(__name__)
WEB_ROOT = Path(__file__).with_name("dashboard")


def read_samples(db_path: str, limit: int = 100) -> list[dict]:
    """Read recent logger rows without taking ownership of the logger database."""
    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        return []
    uri = f"{path.as_uri()}?mode=ro"
    try:
        with closing(sqlite3.connect(uri, uri=True, timeout=2)) as conn:
            rows = conn.execute(
                "SELECT data_json FROM measurements ORDER BY id DESC LIMIT ?",
                (max(1, min(limit, 500)),),
            ).fetchall()
        return [json.loads(row[0]) for row in reversed(rows)]
    except (sqlite3.Error, json.JSONDecodeError):
        log.exception("Unable to read dashboard samples from %s", path)
        return []


def make_handler(db_path: str):
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            route = urlparse(self.path).path
            if route == "/api/samples":
                try:
                    limit = int(parse_qs(urlparse(self.path).query).get("limit", [100])[0])
                except ValueError:
                    limit = 100
                samples = read_samples(db_path, limit)
                return self._json({"samples": samples, "count": len(samples)})
            if route == "/api/status":
                return self._json({"ok": True, "source": "local_logger_database"})
            relative = "index.html" if route == "/" else route.lstrip("/")
            file_path = (WEB_ROOT / relative).resolve()
            if WEB_ROOT.resolve() not in file_path.parents or not file_path.is_file():
                return self.send_error(404)
            content_type = "image/png" if file_path.suffix == ".png" else "text/html; charset=utf-8"
            body = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, payload: dict):
            body = json.dumps(payload, allow_nan=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            log.info("dashboard %s - %s", self.address_string(), fmt % args)

    return DashboardHandler


def serve_dashboard(db_path: str, host: str = "127.0.0.1", port: int = 8080):
    server = ThreadingHTTPServer((host, port), make_handler(db_path))
    log.info("Dashboard listening at http://%s:%d", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("stopping dashboard")
    finally:
        server.server_close()
