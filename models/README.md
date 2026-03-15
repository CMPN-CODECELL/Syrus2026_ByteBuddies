# models/

This folder stores exported 3D model files generated at runtime.

## Files generated here

| File | Description |
|---|---|
| `gemcraft_ring_<id>.glb` | Exported GLB binary (Blender, Unity, Sketchfab) |
| `gemcraft_ring_<id>.stl` | Exported STL binary (3D printing, CAD) |

## Notes

- Files are created when you click **Export GLB** or **Export STL** in the studio
- All models are scaled ×10 (1 unit = 1 mm) for CAD accuracy
- This folder is git-ignored — models are ephemeral session outputs
- The backend also saves exports to `exports/` at runtime

## Opening exported files

| Format | Recommended apps |
|---|---|
| `.glb` | Windows 3D Viewer, Blender, gltf-viewer.donmccurdy.com |
| `.stl` | Cura, PrusaSlicer, Meshmixer, Tinkercad, Fusion 360 |
