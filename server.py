import http.server
import socketserver

PORT = 10000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serveur actif sur le port {PORT}")
    httpd.serve_forever()