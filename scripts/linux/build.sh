#!/bin/bash
# Build script for Linux
# Requires: Python 3.8+, Node.js 18+

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

SKIP_FRONTEND=false
CLEAN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo "========================================"
echo "  BUAA Evaluation - Linux Build"
echo "========================================"
echo ""

# Check system dependencies
echo "[0/4] Checking system dependencies..."
if ! command -v pkg-config &> /dev/null; then
    echo "Warning: pkg-config not found. Install with: sudo apt install pkg-config"
fi

# Clean previous builds
if [ "$CLEAN" = true ]; then
    echo "[1/4] Cleaning previous builds..."
    rm -rf "$PROJECT_ROOT/dist"
    rm -rf "$PROJECT_ROOT/build"
    rm -rf "$PROJECT_ROOT/backend/web"
fi

# Install Python dependencies
echo "[2/4] Installing Python dependencies..."
pip install -q pywebview pyinstaller requests beautifulsoup4

# Check for GTK or QT
if python -c "import gi" 2>/dev/null; then
    echo "    Using GTK backend"
elif python -c "import PyQt5" 2>/dev/null; then
    echo "    Using QT backend"
else
    echo "Warning: Neither GTK nor QT found. Install: sudo apt install python3-gi gir1.2-webkit2-4.0"
fi

# Build frontend
if [ "$SKIP_FRONTEND" = false ]; then
    echo "[3/4] Building frontend..."
    cd "$PROJECT_ROOT/frontend"

    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run build

    cd "$PROJECT_ROOT"
fi

# Build executable
echo "[4/4] Building executable..."
cd "$PROJECT_ROOT"

pyinstaller \
    --name "buaa-evaluation" \
    --onefile \
    --windowed \
    --add-data "backend/web:web" \
    --add-data "backend/evaluator.py:." \
    --add-data "assets/icons/icon.png:icons" \
    --hidden-import webview \
    --hidden-import webview.platforms.gtk \
    --hidden-import webview.platforms.qt \
    --clean \
    --noconfirm \
    backend/main.py

echo ""
echo "========================================"
echo "  Build complete!"
echo "  Output: dist/buaa-evaluation"
echo "========================================"
