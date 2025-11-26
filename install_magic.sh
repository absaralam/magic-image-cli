#!/bin/bash

# ===========================================================================
#  🪄 Magick Installer for Linux / Raspberry Pi
# ===========================================================================
#  Installs Magick to /usr/local/share/magick
#  Creates a 'magic' command in /usr/local/bin
# ===========================================================================

set -e  # Exit on error

INSTALL_DIR="/usr/local/share/magick"
BIN_PATH="/usr/local/bin/magic"
REPO_URL="https://raw.githubusercontent.com/absaralam/magic-image-cli/main"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "======================================================="
echo "            🪄 MAGIC LINUX INSTALLER"
echo "======================================================="
echo -e "${NC}"

# 1. Check for Root/Sudo
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[ERROR] Please run as root (use sudo).${NC}"
  echo "Usage: sudo ./install_magic.sh"
  exit 1
fi

# 2. Install System Dependencies
echo "[1/5] Installing System Dependencies..."
apt-get update -qq
apt-get install -y imagemagick python3 python3-pip python3-venv curl

# 3. Setup Directory
echo "[2/5] Setting up Install Directory..."
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi
mkdir -p "$INSTALL_DIR"

# 4. Download Files
echo "[3/5] Downloading Source..."
curl -s -L -o "$INSTALL_DIR/magic.py" "$REPO_URL/magic.py"
curl -s -L -o "$INSTALL_DIR/requirements.txt" "$REPO_URL/requirements.txt"
curl -s -L -o "$INSTALL_DIR/version.txt" "$REPO_URL/version.txt"

# 5. Setup Python Environment
echo "[4/5] Creating Virtual Environment..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt"

# 6. Create Command Wrapper
echo "[5/5] Creating 'magic' command..."
cat > "$BIN_PATH" <<EOF
#!/bin/bash
"$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/magic.py" "\$@"
EOF

chmod +x "$BIN_PATH"

echo -e "${GREEN}"
echo "======================================================="
echo "🎉 INSTALLATION COMPLETE!"
echo "You can now use 'magic' from anywhere."
echo "Try typing: magic --help"
echo "======================================================="
echo -e "${NC}"
