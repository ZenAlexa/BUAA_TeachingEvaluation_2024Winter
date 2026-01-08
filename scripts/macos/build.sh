#!/bin/bash
# Build script for macOS
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
echo "  BUAA Evaluation - macOS Build"
echo "========================================"
echo ""

# Clean previous builds
if [ "$CLEAN" = true ]; then
    echo "[1/4] Cleaning previous builds..."
    rm -rf "$PROJECT_ROOT/dist"
    rm -rf "$PROJECT_ROOT/build"
    rm -rf "$PROJECT_ROOT/backend/web"
fi

# Install Python dependencies
echo "[2/4] Installing Python dependencies..."
pip install -q pywebview pyinstaller requests beautifulsoup4 pyobjc

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

# Build application bundle
echo "[4/4] Building application..."
cd "$PROJECT_ROOT"

pyinstaller \
    --name "BUAA-Evaluation" \
    --onedir \
    --windowed \
    --add-data "backend/web:web" \
    --add-data "backend/evaluator.py:." \
    --hidden-import webview \
    --hidden-import webview.platforms.cocoa \
    --osx-bundle-identifier "com.buaa.evaluation" \
    --icon "assets/icons/icon.icns" \
    --clean \
    --noconfirm \
    backend/main.py

# Create .app bundle
echo ""
echo "========================================"
echo "  Build complete!"
echo "  Output: dist/BUAA-Evaluation.app"
echo "========================================"
