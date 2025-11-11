#!/usr/bin/env python3
"""
Simple HTTP server for serving the pre-improvement UI demo.
Supports simulated network delays and custom test data.
"""

import http.server
import socketserver
import json
import os
import sys
import urllib.parse
import time
from pathlib import Path

PORT = 8000
BASE_DIR = Path(__file__).parent.parent

class TestDataHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, network_delay=0, test_data=None, **kwargs):
        self.network_delay = network_delay
        self.test_data = test_data or {}
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        # Simulate network delay
        if self.network_delay > 0:
            time.sleep(self.network_delay / 1000.0)
        
        # Serve test data endpoint
        if self.path == '/test-data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(self.test_data).encode())
            return
        
        # Serve static files
        return super().do_GET()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def create_handler(network_delay=0, test_data=None):
    def handler(*args, **kwargs):
        TestDataHandler(*args, network_delay=network_delay, test_data=test_data, **kwargs)
    return handler

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Serve pre-improvement UI')
    parser.add_argument('--port', type=int, default=8000, help='Port to serve on')
    parser.add_argument('--network-delay', type=int, default=0, help='Network delay in ms')
    parser.add_argument('--test-data', type=str, help='Path to test_data.json')
    args = parser.parse_args()
    
    # Load test data if provided
    test_data = {}
    if args.test_data and os.path.exists(args.test_data):
        with open(args.test_data, 'r') as f:
            full_test_data = json.load(f)
            # Extract tags, members, attachments from test cases for frontend
            test_cases = full_test_data.get('test_cases', [])
            if test_cases:
                # Use first test case's environment for data generation
                env = test_cases[0].get('environment', {})
                tags_count = env.get('tags_count', 15)
                members_count = env.get('members_count', 12)
                attachments_count = env.get('attachments_count', 20)
                
                test_data = {
                    'tags': [f'tag_{i+1}' for i in range(tags_count)],
                    'members': [f'Member {i+1}' for i in range(members_count)],
                    'attachments': [
                        {'name': f'attachment_{i+1}.pdf', 'size': 1000000 + i * 100000}
                        for i in range(attachments_count)
                    ]
                }
    
    os.chdir(BASE_DIR / 'src')
    
    handler = create_handler(network_delay=args.network_delay, test_data=test_data)
    
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        print(f"Serving on http://localhost:{args.port}")
        print(f"Network delay: {args.network_delay}ms")
        httpd.serve_forever()

if __name__ == '__main__':
    main()

