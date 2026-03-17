#!/bin/bash
# ─────────────────────────────────────────────
#  Download Three.js scripts for offline use
#  Run: bash scripts/download_threejs.sh
#  Saves files to: frontend/libs/
# ─────────────────────────────────────────────

mkdir -p frontend/libs

echo "Downloading Three.js r128..."
curl -sL https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js \
     -o frontend/libs/three.min.js

echo "Downloading GLTFExporter..."
curl -sL https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/exporters/GLTFExporter.js \
     -o frontend/libs/GLTFExporter.js

echo "Downloading STLExporter..."
curl -sL https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/exporters/STLExporter.js \
     -o frontend/libs/STLExporter.js

echo ""
echo "✅  Three.js libs saved to frontend/libs/"
echo ""
echo "To use offline, update index.html script tags to:"
echo "  <script src=\"libs/three.min.js\"></script>"
echo "  <script src=\"libs/GLTFExporter.js\"></script>"
echo "  <script src=\"libs/STLExporter.js\"></script>"
