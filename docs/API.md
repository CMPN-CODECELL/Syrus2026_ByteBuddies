# Gemcraft AI — Backend API Reference

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

## Endpoints

### GET /health
Check if the server is running.

**Response**
```json
{ "status": "ok", "trimesh": true }
```

---

### GET /api/materials
Returns all available metals and gemstones.

**Response**
```json
{
  "metals": {
    "yellow_gold": { "name": "Yellow Gold (18k)", "rgb": [0.831, 0.627, 0.09], "metalness": 1.0, "roughness": 0.12, "tier": 4 }
  },
  "gemstones": {
    "diamond": { "name": "Diamond", "rgb": [0.867, 0.941, 1.0], "roughness": 0.0, "trans": 0.92, "tier": 5 }
  }
}
```

---

### POST /api/analyze
Analyze an uploaded jewelry image.

**Request** — multipart/form-data
```
file: <image file>
```

**Response**
```json
{
  "jewelry_type": "ring",
  "confidence": 0.91,
  "gem_count": 1,
  "components": [
    { "type": "metal_body", "count": 1 },
    { "type": "gemstone", "count": 1 },
    { "type": "prong_setting", "count": 1 }
  ],
  "geometry_hints": {
    "ring_score": 0.72,
    "metal_coverage": 0.38,
    "symmetry_score": 0.91
  }
}
```

---

### POST /api/generate
Generate a 3D mesh for a jewelry type and return base64 GLB.

**Request**
```json
{
  "session_id": "uuid-string",
  "jewelry_type": "ring",
  "gem_count": 1,
  "metal": "yellow_gold",
  "gemstone": "diamond"
}
```

**Response**
```json
{
  "success": true,
  "session_id": "uuid-string",
  "glb_b64": "base64-encoded-glb...",
  "scene_info": {
    "jewelry_type": "ring",
    "total_vertices": 8420,
    "total_faces": 6100,
    "component_count": 4
  }
}
```

---

### POST /api/customize
Update material on an existing session without rebuilding geometry.

**Request**
```json
{
  "session_id": "uuid-string",
  "metal": "platinum",
  "gemstone": "sapphire"
}
```

**Response**
```json
{
  "success": true,
  "glb_b64": "base64-encoded-glb...",
  "metal": "platinum",
  "gemstone": "sapphire"
}
```

---

### POST /api/budget-suggest
Get cheaper material alternatives for a budget tier.

**Request**
```json
{
  "session_id": "uuid-string",
  "budget_tier": 2
}
```

**Response**
```json
{
  "success": true,
  "suggestions": {
    "gemstone_alt": "topaz",
    "metal_alt": "silver"
  }
}
```

---

### POST /api/export/{fmt}
Download the model as a file. `fmt` = `glb` or `stl`.

**Request**
```json
{ "session_id": "uuid-string" }
```

**Response**
Binary file stream with `Content-Disposition: attachment` header.

---

## Jewelry Types Supported

| Value | Description |
|---|---|
| `ring` | Solitaire or multi-stone ring |
| `pendant` | Pendant with bail loop |
| `earring` | Stud earring |
| `bracelet` | Tennis bracelet |
| `brooch` | Starburst brooch |
| `necklace` | Same as pendant |

## Budget Tiers

| Tier | Label | Metals | Gems |
|---|---|---|---|
| 1 | Budget | Silver | Pearl, Garnet |
| 2 | Mid-Range | Silver, Rose Gold | Pearl, Garnet, Amethyst, Topaz |
| 3 | Premium | Rose Gold, Yellow Gold, Palladium | Amethyst, Topaz, Emerald |
| 4 | Luxury | Yellow Gold, White Gold, Palladium | Emerald, Ruby, Sapphire |
| 5 | Ultra Luxury | Yellow Gold, White Gold, Platinum | Ruby, Sapphire, Diamond |
