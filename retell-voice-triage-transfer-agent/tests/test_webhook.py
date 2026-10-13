import json, os, threading, unittest, urllib.request, urllib.error
os.environ["WEBHOOK_TOKEN"] = "secret123"
from http.server import HTTPServer
from src.webhook_server import Handler, CALL_LOG

def post(url, body, token=None):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    if token: req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read())

class T(unittest.TestCase):
    @classmethod
    def setUpClass(c):
        c.srv = HTTPServer(("127.0.0.1", 0), Handler)
        c.url = f"http://127.0.0.1:{c.srv.server_port}/webhook/call-status"
        threading.Thread(target=c.srv.serve_forever, daemon=True).start()
    @classmethod
    def tearDownClass(c): c.srv.shutdown()

    def test_tc005_invalid_token_401(self):                      # TC-005
        n = len(CALL_LOG)
        code, _ = post(self.url, {"transfer_status": "completed"}, "wrong")
        self.assertEqual(code, 401); self.assertEqual(len(CALL_LOG), n)
    def test_missing_token_401(self):
        self.assertEqual(post(self.url, {})[0], 401)
    def test_tc004_busy_triggers_fallback(self):                 # TC-004
        code, body = post(self.url, {"transfer_status": "SIP_486_BUSY"}, "secret123")
        self.assertEqual(code, 200); self.assertEqual(body["action"], "fallback")
        self.assertIn("voicemail", body["options"])
    def test_success_logged(self):
        code, body = post(self.url, {"transfer_status": "completed"}, "secret123")
        self.assertEqual((code, body["action"]), (200, "none"))

if __name__ == "__main__": unittest.main()
