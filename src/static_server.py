import socket
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread


class LocalStaticServer:
    def __init__(self, directory, port=0):
        self.port = port
        self.directory = directory
        self.server = None

    def is_port_in_use(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', self.port))
                return result == 0
            except Exception:
                return False

    def start(self):
        if self.is_port_in_use():
            return

        print(f'Initializing static server on port {self.port}')
        handler = partial(SimpleHTTPRequestHandler, directory=self.directory)
        self.server = HTTPServer(('127.0.0.1', self.port), handler)
        self.port = self.server.server_port

        thread = Thread(target=self.server.serve_forever, daemon=True)
        thread.start()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()


docs_server = LocalStaticServer(r'C:\Users\André\Documents\Adobe', 9000)
