"""Call-status webhook receiver (CRM / n8n logging). Rejects bad tokens with 401
and maps transfer failures to a fallback action for the agent."""
import hmac, json, os
from http.server import BaseHTTPRequestHandler, HTTPServer

FAIL_STATUSES = {"failed", "busy", "timeout", "SIP_486_BUSY", "SIP_480_UNAVAILABLE"}
CALL_LOG = []  # stand-in for the CRM database


def token_ok(header_value: str) -> bool:
    expected = os.environ.get("WEBHOOK_TOKEN", "")
    supplied = (header_value or "").removeprefix("Bearer ").strip()
    return bool(expected) and hmac.compare_digest(supplied, expected)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/webhook/call-status":
            return self._send(404, {"error": "not found"})
        if not token_ok(self.headers.get("Authorization", "")):
            return self._send(401, {"error": "Unauthorized"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid json"})
        CALL_LOG.append(payload)
        status = payload.get("transfer_status", "")
        if status in FAIL_STATUSES:
            return self._send(200, {"action": "fallback",
                "say": "I'm sorry, our specialist lines are currently busy. Would you like to leave a voicemail or schedule a callback?",
                "options": ["voicemail", "callback"]})
        return self._send(200, {"action": "none", "logged": True})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), Handler).serve_forever()
