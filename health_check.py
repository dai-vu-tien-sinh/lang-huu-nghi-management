
#!/usr/bin/env python3
"""
Health Check Service
Simple HTTP server for external monitoring services
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from datetime import datetime
from supabase_keepalive import SupabaseKeepAlive

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "Supabase Keep-Alive Health Check"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/keep-alive':
            try:
                keep_alive = SupabaseKeepAlive()
                success, messages = keep_alive.run_keep_alive()
                
                self.send_response(200 if success else 500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                    "messages": messages
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server(port=8080):
    """Start health check server in background"""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"🏥 Health check server started on port {port}")
    return server

if __name__ == "__main__":
    server = start_health_server()
    try:
        print("Health server running... Press Ctrl+C to stop")
        while True:
            pass
    except KeyboardInterrupt:
        server.shutdown()
