from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import argparse

parser = argparse.ArgumentParser(description='Simple static server for post-improvement UI')
parser.add_argument('--port', type=int, default=8001)
args = parser.parse_args()

web_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

os.chdir(web_dir)

class CustomHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith('/data/') or path.startswith('data/'):
            rel_path = path.replace('/data/', '').lstrip('/')
            return os.path.join(data_dir, rel_path)
        return SimpleHTTPRequestHandler.translate_path(self, path)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        SimpleHTTPRequestHandler.end_headers(self)

if __name__ == '__main__':
    host = '127.0.0.1'
    httpd = HTTPServer((host, args.port), CustomHandler)
    print(f"Serving at http://{host}:{args.port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print('Server stopped')
