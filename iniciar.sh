#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#  Video Cutter — Launcher Linux / macOS
#  Detecta e instala Python automaticamente se necessário
#  Uso: ./iniciar.sh   ou   bash iniciar.sh
# ══════════════════════════════════════════════════════════

PORT=8765
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL="http://localhost:$PORT"
PID_FILE="$DIR/.server.pid"

# ── Cores ──────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
err()  { echo -e "${RED}❌ $*${NC}"; }

echo ""
echo "══════════════════════════════════════"
echo "  🎬  Video Cutter — Iniciando..."
echo "══════════════════════════════════════"
echo ""

# ── 1. Mata servidor antigo ────────────────────────────────
if [ -f "$PID_FILE" ]; then
  OLD=$(cat "$PID_FILE")
  kill "$OLD" 2>/dev/null && echo "Servidor anterior encerrado (PID $OLD)"
  rm -f "$PID_FILE"
fi
# Garante que a porta esteja livre
lsof -ti :"$PORT" | xargs kill -9 2>/dev/null || true

# ── 2. Detecta Python ──────────────────────────────────────
PYTHON=""
for cmd in python3 python python3.12 python3.11 python3.10; do
  if command -v "$cmd" &>/dev/null; then
    VER=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    MAJOR=$(echo "$VER" | cut -d. -f1)
    MINOR=$(echo "$VER" | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 7 ] 2>/dev/null; then
      PYTHON="$cmd"
      break
    fi
  fi
done

# ── 3. Instala Python se não encontrado ────────────────────
if [ -z "$PYTHON" ]; then
  warn "Python 3 não encontrado. Tentando instalar..."
  OS="$(uname -s)"

  if [ "$OS" = "Linux" ]; then
    if command -v apt-get &>/dev/null; then
      sudo apt-get update -qq && sudo apt-get install -y -qq python3
    elif command -v dnf &>/dev/null; then
      sudo dnf install -y python3
    elif command -v yum &>/dev/null; then
      sudo yum install -y python3
    elif command -v pacman &>/dev/null; then
      sudo pacman -Sy --noconfirm python
    else
      err "Gerenciador de pacotes não reconhecido."
      err "Instale Python 3 manualmente: https://python.org"
      read -p "Pressione Enter para sair..." && exit 1
    fi
  elif [ "$OS" = "Darwin" ]; then
    if command -v brew &>/dev/null; then
      brew install python3
    else
      warn "Homebrew não encontrado. Instalando Homebrew primeiro..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      brew install python3
    fi
  else
    err "Sistema não suportado: $OS"
    err "Instale Python 3: https://python.org"
    read -p "Pressione Enter para sair..." && exit 1
  fi

  # Re-detecta após instalação
  for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then PYTHON="$cmd"; break; fi
  done

  if [ -z "$PYTHON" ]; then
    err "Instalação falhou. Instale Python 3 manualmente: https://python.org"
    read -p "Pressione Enter para sair..." && exit 1
  fi
fi

ok "Python encontrado: $($PYTHON --version)"

# ── 4. Inicia servidor ────────────────────────────────────
"$PYTHON" - <<PYEOF &
import http.server, socketserver, os, sys
os.chdir(r"$DIR")
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", $PORT), H) as s:
    s.serve_forever()
PYEOF

SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"
sleep 1

# Verifica se subiu
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
  err "Servidor não iniciou. Verifique se a porta $PORT está disponível."
  exit 1
fi

ok "Servidor rodando em $URL (PID $SERVER_PID)"
echo ""

# ── 5. Abre navegador ─────────────────────────────────────
OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
  open "$URL"
elif [ "$OS" = "Linux" ]; then
  for browser in xdg-open google-chrome chromium-browser firefox sensible-browser; do
    if command -v "$browser" &>/dev/null; then
      "$browser" "$URL" &>/dev/null &
      break
    fi
  done
fi

echo "  Acesse: $URL"
echo "  Pressione Ctrl+C para encerrar o servidor"
echo ""

# ── 6. Aguarda encerramento ───────────────────────────────
cleanup() {
  echo ""
  kill "$SERVER_PID" 2>/dev/null
  rm -f "$PID_FILE"
  ok "Servidor encerrado."
  exit 0
}
trap cleanup INT TERM
wait "$SERVER_PID"
