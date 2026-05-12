#!/bin/bash
# Configura instancia WhatsApp no Evolution API
# Uso: ./setup-whatsapp.sh

API_URL="http://localhost:8080"
API_KEY="changeme"
INSTANCE="hardmob"

echo "==> Aguardando Evolution API subir..."
until curl -s -o /dev/null -w "%{http_code}" "$API_URL" -H "apikey: $API_KEY" | grep -q "200\|404"; do
    sleep 2
done
echo "    OK"

echo ""
echo "==> Criando instancia '$INSTANCE'..."
curl -s -X POST "$API_URL/instance/create" \
    -H "apikey: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"instanceName\": \"$INSTANCE\", \"qrcode\": true, \"integration\": \"WHATSAPP-BAILEYS\"}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('  Status:', d.get('instance',{}).get('state','?'))"

echo ""
echo "==> Buscando QR Code..."
RESPONSE=$(curl -s "$API_URL/instance/connect/$INSTANCE" -H "apikey: $API_KEY")

# Salva QR como PNG
echo "$RESPONSE" | python3 - <<'PYEOF'
import sys, json, base64, os

data = json.loads(sys.stdin.read())
b64 = data.get("base64", "")

if not b64:
    print("  Erro: QR nao disponivel. A instancia pode ja estar conectada.")
    print("  Resposta:", data)
    sys.exit(1)

# Remove prefixo "data:image/png;base64,"
if "," in b64:
    b64 = b64.split(",", 1)[1]

img = base64.b64decode(b64)
path = "/tmp/hardmob-qr.png"
with open(path, "wb") as f:
    f.write(img)

print(f"  QR salvo em: {path}")
print()
print("  Abra o arquivo e escaneie com o WhatsApp:")
print(f"  - Windows/WSL: explorer.exe {path}")
print(f"  - Linux:       xdg-open {path}")
PYEOF

echo ""
echo "==> Verificando status da conexao (aguarde escanear o QR)..."
echo "    Execute quando conectado:"
echo "    curl $API_URL/instance/connectionState/$INSTANCE -H 'apikey: $API_KEY'"
