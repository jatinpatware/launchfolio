#!/usr/bin/env bash
# LaunchFolio — one-command setup for Mac / Linux
set -e

echo ""
echo "  LaunchFolio — Setup"
echo "  ─────────────────────────────────────────"
echo ""

# 1. Check Python 3
if ! command -v python3 &>/dev/null; then
  echo "  ERROR: Python 3 is not installed."
  echo ""
  echo "  Mac:   Download from https://www.python.org/downloads/"
  echo "  Linux: sudo apt install python3 python3-pip"
  echo ""
  exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "  Python: $PYTHON_VERSION"

# 2. Install dependencies
echo "  Installing dependencies..."
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
  -r backend/requirements.txt --quiet

echo "  Dependencies installed."

# 3. Optional: Ollama (free local AI — no API key needed)
echo ""
echo "  ─────────────────────────────────────────"
echo "  Optional: Ollama (free local AI, no API key needed)"
echo ""

OLLAMA_BIN=""
if command -v ollama &>/dev/null; then
  OLLAMA_BIN="ollama"
elif [ -f "$HOME/bin/ollama" ]; then
  OLLAMA_BIN="$HOME/bin/ollama"
fi

if [ -n "$OLLAMA_BIN" ]; then
  echo "  Ollama is already installed."
  if "$OLLAMA_BIN" list 2>/dev/null | grep -qi "llama"; then
    echo "  A model is already available — ready to use."
  else
    read -r -p "  Pull llama3.2 model (~2 GB, recommended)? [y/N]: " pull_model
    if [[ "$pull_model" =~ ^[Yy]$ ]]; then
      "$OLLAMA_BIN" pull llama3.2
    fi
  fi
else
  echo "  Ollama is not installed."
  echo "  It lets you run AI parsing 100% locally — no account or API key needed."
  echo ""
  read -r -p "  Install Ollama now? [y/N]: " install_ollama
  if [[ "$install_ollama" =~ ^[Yy]$ ]]; then
    curl -fsSL https://ollama.com/install.sh | sh || true
    # macOS: binary lives inside the app bundle
    if [ -f /Applications/Ollama.app/Contents/Resources/ollama ]; then
      mkdir -p "$HOME/bin"
      ln -sf /Applications/Ollama.app/Contents/Resources/ollama "$HOME/bin/ollama"
      export PATH="$HOME/bin:$PATH"
      OLLAMA_BIN="$HOME/bin/ollama"
      echo ""
      echo "  Add this to ~/.zshrc so 'ollama' is always on PATH:"
      echo "    export PATH=\"\$HOME/bin:\$PATH\""
    fi
    if [ -n "$OLLAMA_BIN" ]; then
      "$OLLAMA_BIN" serve &>/tmp/ollama.log &
      sleep 2
      read -r -p "  Pull llama3.2 model (~2 GB, recommended)? [y/N]: " pull_model
      if [[ "$pull_model" =~ ^[Yy]$ ]]; then
        "$OLLAMA_BIN" pull llama3.2
      fi
    fi
  else
    echo "  Skipped. You can install it later — see Step 3 in the browser form."
  fi
fi

echo ""
echo "  ─────────────────────────────────────────"
echo "  Starting LaunchFolio at http://localhost:5000"
echo "  Press Ctrl+C to stop."
echo "  ─────────────────────────────────────────"
echo ""

# 4. Start the server
python3 backend/generate.py --serve
