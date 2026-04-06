#!/bin/bash
# Script para iniciar tunnel localhost.run e capturar URL

echo "🚀 Iniciando tunnel localhost.run..."
echo "Dashboard local: http://localhost:8502"

# Iniciar tunnel e capturar output
ssh -R 80:localhost:8502 nokey@localhost.run 2>&1 | tee /tmp/tunnel.log | while read line; do
    if echo "$line" | grep -q "https://"; then
        URL=$(echo "$line" | grep -o "https://[^ ]*")
        echo "✅ URL HTTPS PÚBLICO: $URL"
        echo "URL: $URL" > /tmp/tunnel_url.txt
    fi
done