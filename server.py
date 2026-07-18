#!/usr/bin/env python3
"""HTML Portal Server - Entry point for browsing local HTML pages."""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json
import mimetypes
from pathlib import Path

PORT = 8080
BASE_DIR = Path(__file__).parent
PAGES_DIR = BASE_DIR / "pages"
PAGE_EXTENSIONS = {'.html', '.htm'}

os.makedirs(PAGES_DIR, exist_ok=True)


class PortalHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # API: list all directories
        if self.path == '/api/directories':
            self._send_json(self._list_directories())
            return
        
        # API: list pages in a directory
        if self.path.startswith('/api/pages/'):
            dir_name = self.path[len('/api/pages/'):]
            self._send_json(self._list_pages(dir_name))
            return
        
        # API: get raw HTML file content
        if self.path.startswith('/api/content/'):
            rel_path = self.path[len('/api/content/'):]
            self._serve_content(rel_path)
            return
        
        # Serve the SPA shell for all other paths
        if self.path == '/' or self.path == '':
            self._serve_file(BASE_DIR / 'index.html')
            return
        
        # Fall through to default static file serving
        super().do_GET()

    def _list_directories(self):
        dirs = []
        if PAGES_DIR.exists():
            for entry in sorted(PAGES_DIR.iterdir()):
                if entry.is_dir():
                    has_pages = any(
                        f.suffix.lower() in PAGE_EXTENSIONS 
                        for f in entry.iterdir() if f.is_file()
                    )
                    if has_pages:
                        dirs.append({
                            'name': entry.name,
                            'path': entry.name,
                        })
        return {'directories': dirs}

    def _list_pages(self, dir_name):
        safe_dir = PAGES_DIR / dir_name
        # Prevent path traversal
        try:
            safe_dir.resolve().relative_to(PAGES_DIR.resolve())
        except ValueError:
            return {'error': 'Invalid directory', 'pages': []}
        
        pages = []
        if safe_dir.exists() and safe_dir.is_dir():
            for f in sorted(safe_dir.iterdir()):
                if f.is_file() and f.suffix.lower() in PAGE_EXTENSIONS:
                    pages.append({
                        'name': f.stem,
                        'filename': f.name,
                        'path': f'{dir_name}/{f.name}',
                    })
        return {'directory': dir_name, 'pages': pages}

    def _serve_content(self, rel_path):
        safe_path = PAGES_DIR / rel_path
        try:
            safe_path.resolve().relative_to(PAGES_DIR.resolve())
        except ValueError:
            self._send_json({'error': 'Invalid path'}, status=404)
            return
        
        if not safe_path.exists() or not safe_path.is_file():
            self._send_json({'error': 'Not found'}, status=404)
            return
        
        content = safe_path.read_text(encoding='utf-8')
        self._send_json({'content': content, 'path': rel_path})

    def _serve_file(self, path):
        if not path.exists():
            self.send_error(404, 'File not found')
            return
        content = path.read_bytes()
        ext = path.suffix.lower()
        ct = mimetypes.guess_type(str(path))[0] or 'text/html'
        self.send_response(200)
        self.send_header('Content-Type', ct + '; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, data, status=200):
        payload = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        # Quieter logs
        if self.path.startswith('/api/'):
            return
        super().log_message(format, *args)


def main():
    server = HTTPServer(('127.0.0.1', PORT), PortalHandler)
    print(f'\n📂 HTML Portal running at http://127.0.0.1:{PORT}')
    print(f'   Pages directory: {PAGES_DIR}')
    print(f'   Create subdirectories inside pages/ with .html files inside them.')
    print(f'   Press Ctrl+C to stop.\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down.')
        server.server_close()


if __name__ == '__main__':
    main()
