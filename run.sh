#!/bin/bash


set -e

CERT_DIR="./certs"
CERT_KEY="$CERT_DIR/gelfsid.key"
CERT_CRT="$CERT_DIR/gelfsid.crt"

if [ ! -f .env ]; then
    echo ".env file not found"
    exit 1
fi

if [ ! -f "$CERT_CRT" ] || [ ! -f "$CERT_KEY" ]; then
    echo "Certificados não encontrados. Criando..."
    mkdir -p "$CERT_DIR"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$CERT_KEY" -out "$CERT_CRT" \
        -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"
    echo "Certificados criados em $CERT_DIR."
fi

if [ ! -d node_modules ]; then
    echo "Instalando dependências do Node.js..."
    npm install
else
    echo "Dependências do Node.js já instaladas."
fi

echo "Construindo o projeto..."
npm run build

echo "Construindo imagens Docker..."
docker-compose build

echo "Subindo os containers com Docker Compose..."
docker-compose up
