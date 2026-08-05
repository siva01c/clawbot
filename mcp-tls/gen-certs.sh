#!/bin/sh
# Generates the self-signed CA and server certificate for the internal MCP
# gateway TLS terminator.
#
# Run this BEFORE `docker compose build ironclaw` — the Dockerfile COPYs
# certs/ca.crt into the image's trust store, so the file has to exist.
#
#   sh clawbot/mcp-tls/gen-certs.sh
#
# Re-running regenerates everything; the ironclaw image must then be rebuilt
# so it trusts the new CA.
set -eu

HOSTNAME_ALIAS="mcp-gateway.clawbot.internal"
CERT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)/certs"

mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

echo "Generating CA..."
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
    -keyout ca.key -out ca.crt \
    -subj "/CN=clawbot internal MCP CA" \
    -addext "basicConstraints=critical,CA:TRUE,pathlen:0" \
    -addext "keyUsage=critical,keyCertSign,cRLSign"

echo "Generating server key and CSR for ${HOSTNAME_ALIAS}..."
openssl req -newkey rsa:2048 -sha256 -nodes \
    -keyout server.key -out server.csr \
    -subj "/CN=${HOSTNAME_ALIAS}"

echo "Signing server certificate..."
# rustls matches on the SAN, not the CN — the extension is what makes this work.
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days 3650 -sha256 \
    -extfile /dev/stdin <<EOF
subjectAltName = DNS:${HOSTNAME_ALIAS}
basicConstraints = critical,CA:FALSE
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth
EOF

rm -f server.csr ca.srl
chmod 600 ca.key server.key

echo
echo "Wrote to ${CERT_DIR}:"
ls -l "$CERT_DIR"
echo
echo "Next: docker compose build ironclaw && docker compose up -d"
