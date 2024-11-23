from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread


class LocalStaticServer:
    """Server for serving static files locally"""

    def __init__(self, directory, port=0):
        self.port = port
        self.directory = directory
        self.server = None

    def start(self):
        handler = partial(SimpleHTTPRequestHandler, directory=self.directory)
        self.server = HTTPServer(('127.0.0.1', self.port), handler)
        self.port = self.server.server_port

        thread = Thread(target=self.server.serve_forever, daemon=True)
        thread.start()

    def get_url(self, path):
        return f'http://127.0.0.1:{self.port}/{path}'

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()


docs_server = LocalStaticServer(r'C:\Users\André\Documents\Adobe', 9000)
