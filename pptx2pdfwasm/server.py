import http.server
import socketserver
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).parent / "static"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()

handler = CustomHTTPRequestHandler
handler.directory = str(DIRECTORY)

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"🚀 Servidor HTTP en ejecución en http://localhost:{PORT}")
    httpd.serve_forever()