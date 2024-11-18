import os
import subprocess
import sys
from threading import Thread

ADDRESS = '0.0.0.0'

servers = [
    (r'H:\DEMAT\Público\10 - DOCUMENTAÇÃO - CLIENTES E FORNECEDORES', 9000),
    (r'H:\DEMAT\Público', 9001),
]


def start_server(directory, port):
    command = [
        sys.executable,
        '-m',
        'http.server',
        str(port),
        '--directory',
        os.path.abspath(directory),
    ]

    print(f'Starting server at {ADDRESS}:{port} serving {directory}')
    subprocess.run(command, check=True)


def main():
    threads = [Thread(target=start_server, args=(directory, port)) for directory, port in servers]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
