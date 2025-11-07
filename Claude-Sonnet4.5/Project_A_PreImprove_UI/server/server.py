#!/usr/bin/env python3
"""
Simple HTTP server for Project A (Pre-Improvement UI)
Serves static files and handles CORS for testing
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path

class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP Request Handler with CORS support"""
    
    def __init__(self, *args, **kwargs):
        # Change to src directory to serve files
        src_dir = Path(__file__).parent.parent / 'src'
        os.chdir(src_dir)
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))


def run_server(port=8001):
    """Start the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    
    print(f"=" * 60)
    print(f"Project A (Pre-Improvement) Server Started")
    print(f"=" * 60)
    print(f"Server running on: http://localhost:{port}")
    print(f"Press Ctrl+C to stop the server")
    print(f"=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        httpd.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    run_server(port)
