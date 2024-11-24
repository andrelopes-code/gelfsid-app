# !/bin/bash

if [ ! -f .env ]; then
    echo ".env file not found"
fi

CERT_DIR="./certs"

if [ ! -f "$CERT_DIR/gelfsid.crt" ] || [ ! -f "$CERT_DIR/gelfsid.key" ]; then
    sudo mkdir -p $CERT_DIR
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout $CERT_DIR//gelfsid.key -out $CERT_DIR//gelfsid.crt
fi
