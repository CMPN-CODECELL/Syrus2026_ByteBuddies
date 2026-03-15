# 💎 Gemcraft AI — 2D to 3D Jewelry Generator


## 🏆 SYRUS Hackathon Submission
**Team:** ByteBuddies

### Problem Statement
AI-powered platform that converts jewelry images into customizable interactive 3D models.

### Track
AI / 3D Web Visualization

### Demo Video
https://drive.google.com/file/d/1tSCHML2SaknSjjaa1DH81kzdrW9Fdl56/view?usp=sharing

### Presentation (PPT)
https://drive.google.com/file/d/1aYjvv4GWGsaqhD2WNSfsgAp1KlZJup8p/view?usp=sharing

## ✨ Features

- **AI Image Analysis** — Claude Vision (claude-opus-4-5) reads your photo and identifies jewelry type, gem count, metal color, and style
- **5 Jewelry Types** — Ring, Pendant, Earring, Bracelet, Brooch
- **Real-time 3D Viewer** — Three.js WebGL with orbit controls, auto-rotate, wireframe mode
- **Live Material Swap** — 6 metals × 8 gemstones with PBR rendering
- **Budget Tiers** — Smart material filtering from Budget to Ultra Luxury
- **Export** — GLB (Blender/Unity) and STL (3D printing) at 10× mm scale
- **Works Offline** — Canvas pixel classifier fallback when no API key
- **Zero Build Step** — Single HTML file, open in any browser

##  Quick Start

### Option A — Frontend only (no Python needed)

1. Open `frontend/index.html` in Chrome or Firefox
2. Get a free API key from [console.anthropic.com](https://console.anthropic.com)
3. Paste your key in the API Configuration box → click **Connect**
4. Upload a jewelry photo or click a Quick Demo button
5. Customize materials, export GLB/STL

### Option B — With Python backend (full mesh quality)

```bash
# Clone the repo
git clone https://github.com/yourusername/gemcraft-ai.git
cd gemcraft-ai

# Install and run
bash start.sh
```

Then open `frontend/index.html` in your browser. The backend runs on `http://localhost:8000`.

### Manual backend start

```bash
pip install -r requirements.txt
python backend/server.py
```

## 📁 Project Structure

```
gemcraft-ai/
│
├── frontend/
│   └── index.html          # Complete app — single file, zero build
│
├── backend/
│   └── server.py           # FastAPI backend (optional, enhances quality)
│
├── models/
│   └── README.md           # Exported GLB/STL files land here
│
├── scripts/
│   └── download_threejs.sh # Download Three.js for offline use
│
├── docs/
│   ├── API.md              # Full REST API reference
│   └── ARCHITECTURE.md     # System design decisions
│
├── requirements.txt        # Python dependencies
├── start.sh                # One-command startup script
├── .gitignore
└── README.md
```

## 🎮 How It Works

### 1. Upload
Drop any jewelry photo. Works with studio shots, phone photos, white backgrounds or dark — any angle.

### 2. AI Analysis
Claude's vision model reads the image and returns:
```json
{
  "jewelry_type": "ring",
  "gem_count": 1,
  "metal_guess": "yellow_gold",
  "gem_guess": "diamond",
  "confidence": 0.94,
  "style": "Classic"
}
```

### 3. 3D Generation
Parametric mesh builder constructs the jewelry in Three.js:
- `buildRing(gemCount)` — torus band + prong settings + gems
- `buildPendant(gemCount)` — bail loop + frame + center stone
- `buildEarring()` — post + basket + stud gem
- `buildBracelet(gemCount)` — arc band + tennis stones
- `buildBrooch(gemCount)` — starburst frame + center + accents

### 4. Customize
Click any metal swatch or gemstone — the 3D model updates live with correct PBR values:
- Metals: metalness=1.0, roughness varies per metal
- Gems: MeshPhysicalMaterial with transmission, IOR, clearcoat

### 5. Export
- **GLB** → `bakeMaterials()` embeds correct PBR data → GLTFExporter → base64 download
- **STL** → STLExporter → base64 download
- Both scaled ×10 (1 unit = 1 mm) for CAD accuracy

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5 · CSS3 · JavaScript ES2020 |
| 3D Engine | Three.js r128 (WebGL) |
| AI | Anthropic Claude API (claude-opus-4-5) |
| Materials | MeshStandardMaterial · MeshPhysicalMaterial |
| Export | GLTFExporter · STLExporter |
| Backend | FastAPI · uvicorn · trimesh · OpenCV |
| Fonts | Playfair Display · Outfit · Space Mono |

## ⚙️ Backend API

See [docs/API.md](docs/API.md) for full endpoint reference.

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Server ping |
| `/api/materials` | GET | All metals + gems |
| `/api/analyze` | POST | Image → jewelry analysis |
| `/api/generate` | POST | Build 3D mesh → GLB |
| `/api/customize` | POST | Swap materials on session |
| `/api/budget-suggest` | POST | Cheaper alternatives |
| `/api/export/{fmt}` | POST | Download GLB or STL |

---

## 🛡️ Performance Notes

| Technique | Why |
|---|---|
| `pixelRatio = 1` | Prevents GPU overload on 4K/retina screens |
| Single WebGL context | Browsers cap at 4–8 contexts; two caused `Context Lost` |
| CSS hero ring | Saves a full GPU context vs a second WebGL canvas |
| 40fps throttle | Halves GPU usage vs 60fps |
| Shadow maps disabled | Removes expensive shadow render passes |
| Context loss recovery | Auto-rebuilds scene if GPU is ever lost |

## 📦 Dependencies

**Frontend** (CDN, no install):
- Three.js r128 — `cdnjs.cloudflare.com`
- GLTFExporter — `cdn.jsdelivr.net`
- STLExporter — `cdn.jsdelivr.net`
- Google Fonts — `fonts.googleapis.com`

**Backend** (pip):
- `fastapi` · `uvicorn` · `python-multipart`
- `numpy` · `opencv-python-headless` · `pillow`
- `trimesh` · `scipy`


## 📄 License

MIT License — free to use, modify, and distribute.

## 🙏 Credits

- **Anthropic Claude** — AI vision and image analysis
- **Three.js** — WebGL 3D rendering engine
- **trimesh** — Server-side parametric mesh generation
- **OpenCV** — Server-side image processing


Built as a hackathon prototype. Single HTML file · No React · No Node.js · No Webpack.
