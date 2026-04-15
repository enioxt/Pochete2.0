import http.server
import socketserver
import os

PORT = 8081
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def end_headers(self):
        # REQUIRED for SharedArrayBuffer to work in modern browsers (ffmpeg.wasm needs it)
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor de video rodando em http://localhost:{PORT}")
    print("Abra o link acima no seu navegador.")
    print("Pressione Ctrl+C para parar o servidor.")
    httpd.serve_forever()
