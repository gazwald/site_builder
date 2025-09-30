"""
Ripped from '__main__' in http.server
"""

import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from builder.constants import HTML_PATH


class DirectoryServer(ThreadingHTTPServer):
    def finish_request(self, request, client_address):
        self.RequestHandlerClass(
            request,
            client_address,
            self,
            directory=HTML_PATH,
        )


def run_httpd(
    HandlerClass=SimpleHTTPRequestHandler,
    ServerClass=DirectoryServer,
    host: str = "",
    port: int = 8000,
):
    with ServerClass((host, port), HandlerClass) as httpd:
        host, port = httpd.socket.getsockname()[:2]
        url_host = f"[{host}]" if ":" in host else host
        print(f"Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)


def blah():
    thread = Thread(target=run_httpd, daemon=True)
    thread.start()
