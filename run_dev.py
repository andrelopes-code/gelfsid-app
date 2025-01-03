import os
import subprocess
import sys

CERT_DIR = './certs'
CERT_KEY = os.path.join(CERT_DIR, 'gelfsid.key')
CERT_CRT = os.path.join(CERT_DIR, 'gelfsid.crt')


def run_command(command, check=True, shell=False):
    try:
        subprocess.run(command, check=check, shell=shell, text=True)

    except subprocess.CalledProcessError as e:
        print(f'Erro ao executar: {" ".join(command) if isinstance(command, list) else command}')
        sys.exit(e.returncode)


def main():
    if not os.path.isfile('.env'):
        print('.env não encontrado.')
        sys.exit(1)

    if not (os.path.isfile(CERT_CRT) and os.path.isfile(CERT_KEY)):
        print('Certificados não encontrados. Criando...')
        os.makedirs(CERT_DIR, exist_ok=True)

        run_command([
            'openssl',
            'req',
            '-x509',
            '-nodes',
            '-days',
            '365',
            '-newkey',
            'rsa:2048',
            '-keyout',
            CERT_KEY,
            '-out',
            CERT_CRT,
            '-subj',
            '/C=BR/ST=MG/L=Sete Lagoas/O=GELF/OU=.../CN=localhost',
        ])

        print(f'Certificados criados em {CERT_DIR}.')

    if not os.path.isdir('node_modules'):
        print('Instalando dependências do Node.js...')
        run_command(['npm', 'install'])

    else:
        print('Dependências do Node.js já instaladas.')

    print('Compilando os arquivos typescript...')
    run_command(['npm', 'run', 'build'])

    print('Subindo os containers com Docker Compose...')
    run_command(['docker-compose', '-f', 'docker-compose.dev.yml', 'build'])
    run_command(['docker-compose', 'up'])


if __name__ == '__main__':
    main()
