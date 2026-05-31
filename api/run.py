import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        auth = self.headers.get("Authorization", "")
        secret = os.environ.get("CRON_SECRET", "")

        if not secret or auth != f"Bearer {secret}":
            self._respond(401, {"error": "Unauthorized"})
            return

        try:
            from main import run_agent
            run_agent()
            self._respond(200, {"status": "ok"})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def _respond(self, status: int, body: dict):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, format, *args):
        pass
