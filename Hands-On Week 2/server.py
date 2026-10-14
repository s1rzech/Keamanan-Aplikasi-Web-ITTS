from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote
import html
import json
import time

HOST = "127.0.0.1"
PORT = 8080

USERS = {
    "alice": {"role": "user", "balance": 150000},
    "bob": {"role": "user", "balance": 90000},
    "admin": {"role": "admin", "balance": 0},
}

PRODUCTS = [
    {"id": 1, "name": "Notebook", "price": 25000},
    {"id": 2, "name": "USB Cable", "price": 35000},
    {"id": 3, "name": "Headset", "price": 120000},
]


def page(title, body):
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; line-height: 1.55; }}
code {{ background: #f1f5f9; padding: 2px 5px; border-radius: 4px; }}
.box {{ border: 1px solid #cbd5e1; padding: 16px; border-radius: 10px; margin: 12px 0; }}
.warn {{ border-left: 6px solid #ef4444; }}
.ok {{ border-left: 6px solid #0d9488; }}
a {{ color: #0f766e; }}
</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
{body}
</body>
</html>""".encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "Week2OWASPLab/1.0"

    def _send(self, status=200, content=b"", content_type="text/html; charset=utf-8", extra_headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(content)

    def _qs(self):
        return parse_qs(urlparse(self.path).query)

    def _cookie_user(self):
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            if part.strip().startswith("username="):
                return part.strip().split("=", 1)[1]
        return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = self._qs()

        if path == "/":
            body = """
<div class="box ok">
<p>MiniMart OWASP Lab berjalan di localhost. Gunakan hanya untuk praktik kelas.</p>
<p>Endpoint: <code>/login?user=alice</code>, <code>/admin</code>, <code>/debug</code>, <code>/search?q=...</code>, <code>/profile?id=1</code>, <code>/redirect?next=...</code>, <code>/fetch?url=...</code></p>
</div>
<p>Gunakan DevTools Network dan <code>curl -i</code> untuk mengumpulkan evidence.</p>
"""
            self._send(content=page("MiniMart OWASP Lab", body))

        elif path == "/login":
            user = qs.get("user", ["alice"])[0]
            if user not in USERS:
                self._send(401, page("Login gagal", "<p>User tidak dikenal.</p>"))
                return
            self._send(
                200,
                page("Login berhasil", f"<p>Anda login sebagai <b>{html.escape(user)}</b>.</p>"),
                extra_headers={"Set-Cookie": f"username={user}; Path=/"},
            )

        elif path == "/admin":
            body = """
<div class="box warn">
<p>Panel admin fiktif. Jika halaman ini tampil untuk user biasa, diskusikan A01 Broken Access Control.</p>
</div>
<pre>{"adminPanel": true, "users": ["alice", "bob", "admin"]}</pre>
"""
            self._send(content=page("Admin Panel", body))

        elif path == "/debug":
            data = {
                "debug": True,
                "server": self.server_version,
                "time": time.time(),
                "fake_db_host": "localhost",
                "fake_feature_flag": "SHOW_INTERNAL_ERRORS",
            }
            self._send(content=json.dumps(data, indent=2).encode("utf-8"), content_type="application/json")

        elif path == "/search":
            q = qs.get("q", [""])[0]
            body = f"""
<p>Hasil pencarian untuk: <b>{q}</b></p>
<p>Diskusikan: kategori apa jika input user dirender tanpa output encoding?</p>
"""
            self._send(content=page("Search", body))

        elif path == "/profile":
            pid = qs.get("id", ["1"])[0]
            profiles = {
                "1": "Profil Alice - email: alice@example.local",
                "2": "Profil Bob - email: bob@example.local",
                "3": "Profil Admin - email: admin@example.local",
            }
            body = f"<p>{html.escape(profiles.get(pid, 'Profil tidak ditemukan'))}</p>"
            self._send(content=page("Profile", body))

        elif path == "/redirect":
            nxt = qs.get("next", ["/"])[0]
            self.send_response(302)
            self.send_header("Location", unquote(nxt))
            self.end_headers()

        elif path == "/fetch":
            target = qs.get("url", [""])[0]
            body = f"""
<div class="box warn">
<p>Simulasi fitur fetch URL. Untuk keamanan kelas, endpoint ini tidak benar-benar mengambil URL.</p>
<p>URL yang diminta: <code>{html.escape(target)}</code></p>
<p>Diskusikan kapan fitur semacam ini dapat menjadi SSRF (A10).</p>
</div>
"""
            self._send(content=page("Fetch URL", body))

        else:
            self._send(404, page("404", "<p>Endpoint tidak ditemukan.</p>"))


if __name__ == "__main__":
    print(f"MiniMart OWASP Lab running at http://{HOST}:{PORT}")
    print("Stop with Ctrl+C")
    HTTPServer((HOST, PORT), Handler).serve_forever()
