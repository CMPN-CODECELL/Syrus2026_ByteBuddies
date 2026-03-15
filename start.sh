#!/bin/bash
# ─────────────────────────────────────────────
#  Gemcraft AI — Quick Start Script
#  Usage: bash start.sh
# ─────────────────────────────────────────────

echo ""
echo "💎  Gemcraft AI — 2D to 3D Jewelry Generator"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌  Python 3 not found. Install from https://python.org"
  exit 1
fi

echo "📦  Installing Python dependencies..."
pip install -r requirements.txt -q

echo ""
echo "🚀  Starting backend server on http://localhost:8000"
echo "📖  API docs:  http://localhost:8000/docs"
echo ""
echo "👉  Open frontend/index.html in your browser"
echo "    (Just double-click — no build step needed)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 backend/server.py
