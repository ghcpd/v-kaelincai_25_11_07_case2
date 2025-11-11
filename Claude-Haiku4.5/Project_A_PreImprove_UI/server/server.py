#!/usr/bin/env python3
"""
Simple HTTP server for serving the pre-improvement UI static files.
Includes API endpoints for test data and simulated network conditions.
"""

import http.server
import socketserver
import json
import os
import sys
import threading
import time
import urllib.parse
from pathlib import Path

class TaskManagerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        directory = str(Path(__file__).parent.parent / 'src')
        super().__init__(*args, directory=directory, **kwargs)
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/test-data':
            self.handle_test_data()
        elif parsed_path.path == '/api/health':
            self.handle_health()
        else:
            # Serve static files
            super().do_GET()
    
    def handle_test_data(self):
        """Serve test data with simulated network delay"""
        # Get network latency from query parameters
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        latency = int(query.get('latency', [200])[0])  # Default 200ms
        
        # Simulate network delay
        time.sleep(latency / 1000.0)
        
        # Load test data
        test_data_path = Path(__file__).parent.parent.parent / 'test_data.json'
        try:
            with open(test_data_path, 'r') as f:
                test_data = json.load(f)
                
            shared_data = test_data.get('shared_data', {})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(shared_data).encode())
            
        except Exception as e:
            self.send_error(500, f"Error loading test data: {str(e)}")
    
    def handle_health(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        health_data = {
            "status": "healthy",
            "version": "pre-improvement",
            "timestamp": time.time()
        }
        
        self.wfile.write(json.dumps(health_data).encode())
    
    def do_POST(self):
        if self.path == '/api/tasks':
            self.handle_create_task()
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_create_task(self):
        """Handle task creation with simulated processing time"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            task_data = json.loads(post_data)
            
            # Simulate processing time
            time.sleep(1)
            
            # Basic validation
            required_fields = ['title', 'priority', 'dueDate']
            for field in required_fields:
                if field not in task_data or not task_data[field]:
                    self.send_error(400, f"Missing required field: {field}")
                    return
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "id": f"task_{int(time.time())}",
                "status": "created",
                "data": task_data
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON data")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def start_server(port=8000):
    """Start the HTTP server"""
    try:
        with socketserver.TCPServer(("", port), TaskManagerHandler) as httpd:
            print(f"Starting pre-improvement server on port {port}")
            print(f"Server URL: http://localhost:{port}")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Port {port} is already in use. Try a different port.")
            return False
        else:
            print(f"Error starting server: {e}")
            return False
    return True

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8000.")
    
    success = start_server(port)
    sys.exit(0 if success else 1)