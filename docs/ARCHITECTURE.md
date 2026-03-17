# Gemcraft AI — Architecture

## Overview

Gemcraft AI converts 2D jewelry photos into interactive 3D models using Claude's vision API and Three.js WebGL rendering — delivered as a single HTML file with an optional Python backend.

## Flow

```
User uploads image
        │
        ▼
┌─────────────────────┐      ┌──────────────────────┐
│  Claude Vision API  │ ─OR─ │  Canvas Classifier   │
│  (claude-opus-4-5)  │      │  (offline fallback)  │
└─────────────────────┘      └──────────────────────┘
        │
        ▼
   Analysis JSON
   (type, gem_count, metal_guess, confidence)
        │
        ▼
   Parametric Mesh Builder (Three.js)
   buildRing / buildPendant / buildEarring
   buildBracelet / buildBrooch
        │
        ▼
   Single WebGL Renderer
   (40fps, pixelRatio=1, context-loss recovery)
        │
        ▼
   Interactive 3D Viewer ──── Material Studio
   (orbit, zoom, wireframe)   (6 metals, 8 gems)
        │
        ▼
   Export
   (GLB → Blender/Unity | STL → 3D printing)
```

## Frontend Architecture

- **Single HTML file** — `frontend/index.html`
- **No build step** — open directly in browser
- **Three.js r128** loaded from CDN
- **Claude API** called directly from browser using `anthropic-dangerous-direct-browser-access` header
- **Canvas Pixel Classifier** — offline fallback when no API key

## Backend Architecture (Optional)

- **FastAPI** single-file server — `backend/server.py`
- **trimesh** for server-side parametric 3D mesh generation
- **OpenCV** for server-side image analysis
- Sessions stored in-memory (dict)
- Exports saved to `exports/` directory

## Key Design Decisions

| Decision | Reason |
|---|---|
| Single HTML file | Zero install, zero setup, shareable |
| pixelRatio = 1 | Prevents GPU context loss on retina displays |
| Single WebGL context | Browser allows 4–8 max; two caused crashes |
| CSS hero ring | Saves a full WebGL context vs canvas ring |
| 40fps throttle | Halves GPU usage vs 60fps with no visible difference |
| base64 data URL export | Bypasses Claude sandbox `createObjectURL` restriction |
| bakeMaterials() | Ensures correct PBR values in exported GLB |
