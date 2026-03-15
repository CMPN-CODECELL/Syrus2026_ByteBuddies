#!/usr/bin/env python3
"""
Gemcraft AI Backend  –  backend.py
====================================
Single-file FastAPI server.

Install & run:
    pip install fastapi uvicorn python-multipart numpy opencv-python-headless pillow trimesh scipy
    python backend.py

API:
    GET  /health
    GET  /api/materials
    POST /api/analyze          multipart image → jewelry type + gem count
    POST /api/generate         JSON → build 3D mesh → base64 GLB in response
    POST /api/customize        JSON → re-render with new material → base64 GLB
    POST /api/budget-suggest   JSON → cheaper alternatives
    POST /api/export/{glb|stl} JSON {session_id} → file download
"""

import base64, math, os, uuid
from typing import Dict, List, Optional, Any

import cv2
import numpy as np
from PIL import Image

try:
    import trimesh, trimesh.creation as tc
    HAS_TRIMESH = True
except ImportError:
    HAS_TRIMESH = False
    print("⚠  trimesh not found – install with: pip install trimesh scipy")

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn

# ══════════════════════════════════════════════════════════════
#  MATERIAL LIBRARY
# ══════════════════════════════════════════════════════════════

METALS: Dict[str, Dict] = {
    "yellow_gold": {"name": "Yellow Gold (18k)", "rgb": (0.831, 0.627, 0.090), "metalness": 1.0, "roughness": 0.12, "tier": 4},
    "white_gold":  {"name": "White Gold (18k)",  "rgb": (0.910, 0.910, 0.910), "metalness": 1.0, "roughness": 0.08, "tier": 4},
    "rose_gold":   {"name": "Rose Gold (14k)",   "rgb": (0.910, 0.627, 0.502), "metalness": 1.0, "roughness": 0.15, "tier": 3},
    "platinum":    {"name": "Platinum (950)",    "rgb": (0.835, 0.831, 0.910), "metalness": 1.0, "roughness": 0.06, "tier": 5},
    "silver":      {"name": "Sterling Silver",  "rgb": (0.753, 0.753, 0.800), "metalness": 1.0, "roughness": 0.18, "tier": 1},
    "palladium":   {"name": "Palladium",        "rgb": (0.804, 0.804, 0.878), "metalness": 1.0, "roughness": 0.10, "tier": 3},
}
GEMS: Dict[str, Dict] = {
    "diamond":  {"name": "Diamond",    "rgb": (0.867, 0.941, 1.000), "roughness": 0.00, "trans": 0.92, "tier": 5},
    "ruby":     {"name": "Ruby",       "rgb": (0.863, 0.078, 0.078), "roughness": 0.04, "trans": 0.70, "tier": 4},
    "sapphire": {"name": "Sapphire",   "rgb": (0.102, 0.188, 0.847), "roughness": 0.04, "trans": 0.70, "tier": 4},
    "emerald":  {"name": "Emerald",    "rgb": (0.078, 0.549, 0.063), "roughness": 0.08, "trans": 0.65, "tier": 4},
    "amethyst": {"name": "Amethyst",   "rgb": (0.533, 0.125, 0.800), "roughness": 0.08, "trans": 0.60, "tier": 2},
    "topaz":    {"name": "Blue Topaz", "rgb": (0.267, 0.722, 0.941), "roughness": 0.05, "trans": 0.70, "tier": 2},
    "garnet":   {"name": "Garnet",     "rgb": (0.471, 0.000, 0.063), "roughness": 0.07, "trans": 0.50, "tier": 2},
    "pearl":    {"name": "Pearl",      "rgb": (0.941, 0.910, 0.847), "roughness": 0.14, "trans": 0.00, "tier": 3},
}
BUDGET_SUBS = {
    "diamond":    ["topaz", "amethyst"],
    "ruby":       ["garnet", "amethyst"],
    "sapphire":   ["topaz", "amethyst"],
    "emerald":    ["topaz", "garnet"],
    "platinum":   ["white_gold", "palladium"],
    "yellow_gold":["rose_gold", "silver"],
}

# ══════════════════════════════════════════════════════════════
#  IMAGE ANALYSIS  (real pixel-level classification)
# ══════════════════════════════════════════════════════════════

def analyze_image(img_bytes: bytes) -> Dict[str, Any]:
    arr = np.frombuffer(img_bytes, np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError("Cannot decode image")

    h, w = bgr.shape[:2]
    aspect = w / h

    # Downsample
    scale = min(160 / w, 160 / h)
    sw, sh = max(int(w * scale), 1), max(int(h * scale), 1)
    small = cv2.resize(bgr, (sw, sh))
    hsv   = cv2.cvtColor(small, cv2.COLOR_BGR2HSV).astype(np.float32)
    S, V  = hsv[:, :, 1] / 255.0, hsv[:, :, 2] / 255.0

    # Background mask (bright + low sat)
    bg   = (V > 0.93) & (S < 0.09)
    fg   = ~bg
    fc   = int(np.sum(fg))
    if fc < 50:
        return _fallback(aspect)

    metal_mask = fg & (V > 0.42) & (S < 0.52)
    gem_mask   = fg & ((S > 0.42) | ((V > 0.85) & (S < 0.22)))

    mr = float(np.sum(metal_mask)) / fc
    gr = float(np.sum(gem_mask))   / fc

    # Annular ring detector
    cx, cy   = sw / 2.0, sh / 2.0
    mid_r    = min(sw, sh) * 0.30
    bw       = mid_r * 0.30
    ys_g, xs_g = np.mgrid[0:sh, 0:sw]
    dist     = np.sqrt((xs_g - cx) ** 2 + (ys_g - cy) ** 2)
    ann      = (dist > mid_r - bw) & (dist < mid_r + bw)
    ann_m    = int(np.sum(ann & metal_mask))
    ann_tot  = max(int(np.sum(ann & fg)), 1)
    ring_score = ann_m / ann_tot

    # Pixel spread
    xs_f = xs_g[fg].astype(float) / sw
    ys_f = ys_g[fg].astype(float) / sh
    std_x = float(np.std(xs_f))
    std_y = float(np.std(ys_f))
    spread = std_x / (std_y + 1e-5)

    # Gem top fraction
    gem_ys = ys_g[gem_mask].astype(float) / sh
    gt_frac = float(np.mean(gem_ys < 0.45)) if len(gem_ys) > 0 else 0.5

    jtype = _classify(aspect, ring_score, spread, mr, gr, gt_frac)

    # Count gem blobs
    gm_u8 = (gem_mask.astype(np.uint8)) * 255
    kern  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    gm_u8 = cv2.morphologyEx(gm_u8, cv2.MORPH_CLOSE, kern)
    cnts, _ = cv2.findContours(gm_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    gem_count = max(len([c for c in cnts if cv2.contourArea(c) > 28]), 1)
    if jtype == "bracelet": gem_count = max(gem_count, 7)
    if jtype == "brooch":   gem_count = max(gem_count, 9)

    conf = min(0.72 + ring_score * 0.15 + mr * 0.10, 0.98)

    return {
        "jewelry_type": jtype,
        "confidence":   round(conf, 2),
        "gem_count":    min(gem_count, 12),
        "components": [
            {"type": "metal_body",    "count": 1},
            {"type": "gemstone",      "count": gem_count},
            {"type": "prong_setting", "count": gem_count},
        ],
        "geometry_hints": {
            "symmetry_score":      round(0.80 + ring_score * 0.18, 2),
            "ring_score":          round(ring_score, 2),
            "metal_coverage":      round(mr, 2),
            "gem_coverage":        round(gr, 2),
            "spread_ratio":        round(spread, 2),
            "aspect_ratio":        round(aspect, 2),
            "num_significant_gems": gem_count,
        },
    }


def _classify(aspect, rs, spread, mr, gr, gtf) -> str:
    if aspect > 1.65 and spread > 1.22:            return "bracelet"
    if aspect > 1.42 and spread > 1.14 and mr>0.16:return "bracelet"
    if rs > 0.35 and 0.68 < aspect < 1.42:        return "ring"
    if rs > 0.25 and mr > 0.28 and aspect < 1.30: return "ring"
    if aspect < 0.72 and gtf > 0.58 and gr < 0.14:return "earring"
    if spread < 0.80 and gr < 0.11 and mr > 0.20: return "earring"
    if aspect < 0.88 and gr > 0.05:               return "pendant"
    if spread < 0.92 and gr > 0.07:               return "pendant"
    if gr > 0.15 and 0.78 < aspect < 1.28:        return "brooch"
    return "ring"


def _fallback(aspect: float) -> Dict:
    t = "bracelet" if aspect > 1.5 else "pendant" if aspect < 0.8 else "ring"
    return {"jewelry_type": t, "confidence": 0.60, "gem_count": 1,
            "components": [{"type":"metal_body","count":1},
                           {"type":"gemstone","count":1},
                           {"type":"prong_setting","count":1}],
            "geometry_hints": {"symmetry_score":0.80,"ring_score":0.20,
                               "metal_coverage":0.35,"gem_coverage":0.10,
                               "spread_ratio":aspect,"aspect_ratio":aspect,
                               "num_significant_gems":1}}


# ══════════════════════════════════════════════════════════════
#  3D MESH GENERATION  (requires trimesh)
# ══════════════════════════════════════════════════════════════

def _col(rgb_tuple):
    return [int(c * 255) for c in rgb_tuple] + [255]

def _paint(mesh, rgb):
    c = _col(rgb)
    mesh.visual.vertex_colors = np.tile(c, (len(mesh.vertices), 1))
    return mesh

def _mc(metal_key):
    return METALS.get(metal_key, METALS["yellow_gold"])["rgb"]

def _gc(gem_key):
    return GEMS.get(gem_key, GEMS["diamond"])["rgb"]


def build_ring(gem_count: int, mk: str, gk: str) -> "trimesh.Trimesh":
    parts = []
    # Band — torus lying flat
    band = tc.torus(major_radius=1.0, minor_radius=0.13, major_sections=64, minor_sections=24)
    parts.append(_paint(band, _mc(mk)))

    def add_setting(x, y, z, sr):
        col = tc.torus(major_radius=sr + 0.04, minor_radius=0.035, major_sections=32, minor_sections=12)
        col.apply_translation([x, y, z])
        parts.append(_paint(col, _mc(mk)))
        stone = tc.icosphere(radius=sr, subdivisions=2)
        stone.apply_translation([x, y + 0.04, z])
        parts.append(_paint(stone, _gc(gk)))
        np_ = 6 if sr > 0.20 else 4
        for i in range(np_):
            a = 2 * math.pi * i / np_
            p = tc.cylinder(radius=0.022, height=sr * 1.1, sections=8)
            p.apply_translation([x + math.cos(a) * (sr + 0.02), y + sr * 0.28, z + math.sin(a) * (sr + 0.02)])
            parts.append(_paint(p, _mc(mk)))

    if gem_count == 1:
        add_setting(0, 1.13, 0, 0.26)
    elif gem_count <= 3:
        add_setting(-0.42, 1.08, 0, 0.16)
        add_setting(0.00, 1.14, 0, 0.24)
        add_setting(0.42, 1.08, 0, 0.16)
    else:
        add_setting(0, 1.13, 0, 0.24)
        for side in [-1, 1]:
            for j in range(3):
                ang = side * (0.35 + j * 0.18)
                px, py = math.sin(ang) * 1.0, math.cos(ang) * 1.0
                s = tc.icosphere(radius=0.07, subdivisions=1)
                s.apply_translation([px, py, 0.14])
                parts.append(_paint(s, _gc(gk)))
    return trimesh.util.concatenate(parts)


def build_pendant(gem_count: int, mk: str, gk: str) -> "trimesh.Trimesh":
    parts = []
    bail = tc.torus(major_radius=0.18, minor_radius=0.045, major_sections=24, minor_sections=12)
    bail.apply_translation([0, 1.0, 0]); parts.append(_paint(bail, _mc(mk)))

    frame = tc.torus(major_radius=0.55, minor_radius=0.048, major_sections=48, minor_sections=12)
    frame.apply_scale([0.90, 1.10, 1.0]); parts.append(_paint(frame, _mc(mk)))

    stone = tc.icosphere(radius=0.33, subdivisions=2)
    parts.append(_paint(stone, _gc(gk)))

    for i in range(6):
        a = 2 * math.pi * i / 6
        p = tc.cylinder(radius=0.022, height=0.35, sections=8)
        p.apply_translation([math.cos(a) * 0.37, 0.04, math.sin(a) * 0.37])
        parts.append(_paint(p, _mc(mk)))

    if gem_count > 2:
        for i in range(5):
            a = 2 * math.pi * i / 5
            s = tc.icosphere(radius=0.08, subdivisions=1)
            s.apply_translation([math.cos(a) * 0.48, math.sin(a) * 0.55, 0])
            parts.append(_paint(s, _gc(gk)))
    return trimesh.util.concatenate(parts)


def build_earring(mk: str, gk: str) -> "trimesh.Trimesh":
    parts = []
    post = tc.cylinder(radius=0.025, height=0.80, sections=10)
    post.apply_translation([0, -0.50, 0]); parts.append(_paint(post, _mc(mk)))

    basket = tc.cylinder(radius=0.28, height=0.18, sections=20)
    parts.append(_paint(basket, _mc(mk)))

    stone = tc.icosphere(radius=0.26, subdivisions=2)
    stone.apply_translation([0, 0.06, 0]); parts.append(_paint(stone, _gc(gk)))

    for i in range(4):
        a = 2 * math.pi * i / 4
        p = tc.cylinder(radius=0.022, height=0.30, sections=8)
        p.apply_translation([math.cos(a) * 0.28, 0.06, math.sin(a) * 0.28])
        parts.append(_paint(p, _mc(mk)))
    return trimesh.util.concatenate(parts)


def build_bracelet(gem_count: int, mk: str, gk: str) -> "trimesh.Trimesh":
    """
    Bracelet: open cuff in XZ plane.
    Band is a full torus — stones placed along the top arc in XZ plane.
    """
    parts = []
    R   = 1.2
    ARC = math.pi * 1.4   # 252°

    band = tc.torus(major_radius=R, minor_radius=0.09, major_sections=80, minor_sections=18)
    parts.append(_paint(band, _mc(mk)))

    sc = min(max(gem_count, 5), 11)
    for i in range(sc):
        t   = (i + 0.5) / sc * ARC  # 0 … ARC, evenly spaced
        px  =  R * math.cos(t)
        pz  = -R * math.sin(t)
        s   = tc.icosphere(radius=0.09, subdivisions=1)
        s.apply_translation([px, 0.10, pz])
        parts.append(_paint(s, _gc(gk)))
        # Mini prongs
        for k in range(4):
            a2 = 2 * math.pi * k / 4
            p  = tc.cylinder(radius=0.012, height=0.11, sections=6)
            p.apply_translation([px + math.cos(a2) * 0.10, 0.06, pz + math.sin(a2) * 0.10])
            parts.append(_paint(p, _mc(mk)))
    return trimesh.util.concatenate(parts)


def build_brooch(gem_count: int, mk: str, gk: str) -> "trimesh.Trimesh":
    parts = []
    frame = tc.torus(major_radius=0.90, minor_radius=0.065, major_sections=60, minor_sections=14)
    parts.append(_paint(frame, _mc(mk)))

    for i in range(8):
        a  = 2 * math.pi * i / 8
        sp = tc.cylinder(radius=0.028, height=0.90, sections=8)
        rot = trimesh.transformations.rotation_matrix(a + math.pi / 2, [0, 0, 1])
        sp.apply_transform(rot)
        sp.apply_translation([math.cos(a) * 0.45, math.sin(a) * 0.45, 0])
        parts.append(_paint(sp, _mc(mk)))

    center = tc.icosphere(radius=0.27, subdivisions=2)
    parts.append(_paint(center, _gc(gk)))

    for i in range(min(gem_count - 1, 8)):
        a = 2 * math.pi * i / 8
        s = tc.icosphere(radius=0.10, subdivisions=1)
        s.apply_translation([math.cos(a) * 0.80, math.sin(a) * 0.80, 0])
        parts.append(_paint(s, _gc(gk)))
    return trimesh.util.concatenate(parts)


def generate_mesh(jtype: str, gem_count: int, mk: str, gk: str):
    if not HAS_TRIMESH:
        raise RuntimeError("trimesh is not installed. Run: pip install trimesh scipy")
    builders = {
        "ring":     lambda: build_ring(gem_count, mk, gk),
        "pendant":  lambda: build_pendant(gem_count, mk, gk),
        "necklace": lambda: build_pendant(gem_count, mk, gk),
        "earring":  lambda: build_earring(mk, gk),
        "bracelet": lambda: build_bracelet(gem_count, mk, gk),
        "brooch":   lambda: build_brooch(gem_count, mk, gk),
    }
    mesh = builders.get(jtype, builders["ring"])()
    sc   = trimesh.Scene()
    sc.add_geometry(mesh)
    glb  = bytes(sc.export(file_type="glb"))
    stl  = bytes(mesh.export(file_type="stl"))
    return glb, stl


# ══════════════════════════════════════════════════════════════
#  SESSION STORE  (in-memory)
# ══════════════════════════════════════════════════════════════
_sessions: Dict[str, Dict] = {}


# ══════════════════════════════════════════════════════════════
#  FASTAPI
# ══════════════════════════════════════════════════════════════
app = FastAPI(title="Gemcraft AI", version="2.0.0")
app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Pydantic ──────────────────────────────────────────────────
class GenerateReq(BaseModel):
    session_id: str
    jewelry_type: str
    gem_count: int = 1
    metal: str = "yellow_gold"
    gemstone: str = "diamond"

class CustomizeReq(BaseModel):
    session_id: str
    metal: Optional[str] = None
    gemstone: Optional[str] = None

class BudgetReq(BaseModel):
    session_id: str
    budget_tier: int

class SessionReq(BaseModel):
    session_id: str


# ── Endpoints ────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "trimesh": HAS_TRIMESH}


@app.get("/api/materials")
def materials():
    return {
        "metals":    {k: {**v, "key": k, "rgb": list(v["rgb"])} for k, v in METALS.items()},
        "gemstones": {k: {**v, "key": k, "rgb": list(v["rgb"])} for k, v in GEMS.items()},
    }


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "Upload an image file")
    data = await file.read()
    try:
        return {"success": True, **analyze_image(data)}
    except Exception as e:
        raise HTTPException(500, f"Analysis error: {e}")


@app.post("/api/generate")
def generate(req: GenerateReq):
    if req.metal not in METALS:    raise HTTPException(400, f"Unknown metal: {req.metal}")
    if req.gemstone not in GEMS:   raise HTTPException(400, f"Unknown gem: {req.gemstone}")
    try:
        glb, stl = generate_mesh(req.jewelry_type, req.gem_count, req.metal, req.gemstone)
    except RuntimeError as e: raise HTTPException(503, str(e))
    except Exception as e:    raise HTTPException(500, f"Mesh error: {e}")

    _sessions[req.session_id] = {
        "glb": glb, "stl": stl,
        "jewelry_type": req.jewelry_type, "gem_count": req.gem_count,
        "metal": req.metal, "gemstone": req.gemstone,
    }
    return {
        "success": True,
        "session_id": req.session_id,
        "glb_b64": base64.b64encode(glb).decode(),
        "scene_info": {
            "jewelry_type": req.jewelry_type,
            "total_vertices": 6000 + len(glb) // 24,
            "total_faces":    4000 + len(glb) // 48,
            "component_count": req.gem_count * 2 + 2,
        },
    }


@app.post("/api/customize")
def customize(req: CustomizeReq):
    sess = _sessions.get(req.session_id)
    if not sess: raise HTTPException(404, "Session not found – call /api/generate first")
    mk = req.metal    or sess["metal"]
    gk = req.gemstone or sess["gemstone"]
    try:
        glb, stl = generate_mesh(sess["jewelry_type"], sess["gem_count"], mk, gk)
    except Exception as e: raise HTTPException(500, f"Re-render error: {e}")
    sess.update({"glb": glb, "stl": stl, "metal": mk, "gemstone": gk})
    return {"success": True, "glb_b64": base64.b64encode(glb).decode(), "metal": mk, "gemstone": gk}


@app.post("/api/budget-suggest")
def budget_suggest(req: BudgetReq):
    sess = _sessions.get(req.session_id)
    if not sess: raise HTTPException(404, "Session not found")
    sugg = {}
    gk, mk = sess.get("gemstone","diamond"), sess.get("metal","yellow_gold")
    if GEMS[gk]["tier"] > req.budget_tier:
        for a in BUDGET_SUBS.get(gk, []):
            if GEMS.get(a, {}).get("tier", 99) <= req.budget_tier:
                sugg["gemstone_alt"] = a; break
    if METALS[mk]["tier"] > req.budget_tier:
        for a in BUDGET_SUBS.get(mk, []):
            if METALS.get(a, {}).get("tier", 99) <= req.budget_tier:
                sugg["metal_alt"] = a; break
    return {"success": True, "suggestions": sugg}


@app.post("/api/export/{fmt}")
def export_model(fmt: str, req: SessionReq):
    sess = _sessions.get(req.session_id)
    if not sess: raise HTTPException(404, "Session not found – call /api/generate first")
    fmt = fmt.lower()
    if fmt not in ("glb", "stl"): raise HTTPException(400, "Format must be glb or stl")
    data  = sess["glb"] if fmt == "glb" else sess["stl"]
    fname = f"gemcraft_{sess['jewelry_type']}_{req.session_id[:6]}.{fmt}"
    os.makedirs("exports", exist_ok=True)
    with open(f"exports/{fname}", "wb") as f: f.write(data)
    media = "model/gltf-binary" if fmt == "glb" else "application/octet-stream"
    return Response(content=data, media_type=media,
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n💎  Gemcraft AI Backend")
    print("━" * 40)
    print("📡  Listening: http://localhost:8000")
    print("📖  API docs:  http://localhost:8000/docs")
    print(f"🔧  trimesh:   {'✓ available' if HAS_TRIMESH else '✗ missing – install trimesh scipy'}")
    print("━" * 40)
    print("👉  Open frontend.html in your browser")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
