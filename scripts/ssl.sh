#!/bin/bash
set -euo pipefail


DOMAIN=${1:-api.local}
EMAIL=${2:-admin@example.com}
CERTS_DIR=${CERTS_DIR:-certs}


mkdir -p "$CERTS_DIR"


# Dev self-signed
if [[ "$DOMAIN" == "api.local" || "$DOMAIN" == "localhost" ]]; then
echo "Generating self-signed cert for $DOMAIN..."
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
-keyout "$CERTS_DIR/privkey.pem" \
-out "$CERTS_DIR/fullchain.pem" \
-subj "/CN=$DOMAIN"
exit 0
fi


# Prod via certbot (requires DNS or HTTP challenge readiness)
if command -v certbot >/dev/null 2>&1; then
sudo certbot certonly --standalone -d "$DOMAIN" -m "$EMAIL" --agree-tos --non-interactive
sudo cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem "$CERTS_DIR/fullchain.pem"
sudo cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem "$CERTS_DIR/privkey.pem"
else
echo "certbot not installed; install it or use reverse-proxy with TLS termination"
fi