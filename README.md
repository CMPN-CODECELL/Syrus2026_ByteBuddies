💎 Gemcraft AI — 2D to 3D Jewelry Generator

🏆 SYRUS Hackathon Submission

👥 Team Name

ByteBuddies

🧩 Problem Statement

An AI-powered platform that converts jewelry images into customizable, interactive 3D models and enables real-time virtual try-on directly in the browser.

🎯 Track

AI / 3D Web Visualization

🎥 Demo Video

https://drive.google.com/drive/u/0/folders/1begkYmHll2iO4WHiwjnxKuutIeA5CL9R

📊 Presentation (PPT)

https://drive.google.com/file/d/1PrBbww5K6BQ8iKsaO4xUdh-PmIPOukjb/view?usp=drivesdk

Summary Template

https://drive.google.com/file/d/1Mgf5wHx0JIXnsr9ANQYvSJA1iwqb77IR/view?usp=drivesdk

✨ Key Features
🧠 AI Image Analysis

Powered by Claude Vision (claude-opus-4-5)

Detects:

Jewelry type

Gem count

Metal type

Style

Works on real-world images (any angle/background)

💍 Multi-Jewelry Support

Supports 5 categories:

Ring

Pendant / Necklace

Earring

Bracelet

Brooch

🧍 Context-Aware Jewelry Detection (NEW 🔥)

Understands where jewelry is worn:

Finger (Ring)

Neck (Pendant)

Ear (Earring)

Wrist (Bracelet)

Improves:

Model accuracy

Proportions

Future AR compatibility

🕶️ Virtual Try-On (🔥 SHOWSTOPPER)

Experience jewelry live using your camera — no app required.

📷 Real-time camera integration

✋ Ring mode — detects palm center

📿 Pendant mode — detects neck position

👂 Earring mode — detects ear/cheek region

🎯 Live 3D overlay on body

🎚️ Adjustable scale for realistic fitting

🔒 100% browser-based (no data sent to server)

🌐 Real-Time 3D Viewer

Built with Three.js (WebGL)

Features:

Orbit controls

Auto-rotate

Wireframe mode

🎨 Live Material Customization

6 Metals × 8 Gemstones

Physically-Based Rendering (PBR):

Metals → realistic reflections

Gems → transmission, IOR, sparkle

💰 Budget-Based Smart Suggestions

Automatically suggests cheaper alternatives

Supports:

Budget → Premium → Luxury tiers

📦 Export Ready

Export formats:

GLB → Blender / Unity

STL → 3D Printing

Scaled for real-world use (1 unit = 1 mm)

⚡ Works Offline

Fallback pixel-based detection when API not available

Fully functional without backend

🧩 Zero Build Setup

Single HTML file

No React, No Node.js

Runs instantly in browser

🎮 How It Works
1️⃣ Upload Image

Upload any jewelry photo (phone/studio, any background)

2️⃣ AI Analysis

Returns structured data:

{
  "jewelry_type": "ring",
  "gem_count": 1,
  "metal_guess": "yellow_gold",
  "gem_guess": "diamond",
  "confidence": 0.94,
  "style": "Classic"
}
3️⃣ 3D Model Generation

Parametric builder creates models:

Ring → torus band + gem settings

Pendant → chain loop + frame

Earring → stud + basket

Bracelet → arc band + stones

Brooch → decorative structure

4️⃣ Customization

Change metal & gemstone instantly

Real-time visual updates

5️⃣ Virtual Try-On

Enable camera

Select mode (Ring / Pendant / Earring)

See jewelry on your body in real time

6️⃣ Export

Download model in GLB or STL format

🏗️ Architecture

Frontend (Browser)

HTML5 · CSS3 · JavaScript

Three.js (WebGL rendering)

AI Layer

Claude Vision API

Backend (Optional)

FastAPI · OpenCV · Trimesh

🔧 Tech Stack
Layer	Technology
Frontend	HTML5 · CSS3 · JavaScript
3D Engine	Three.js (WebGL)
AI	Claude Vision API
Backend	FastAPI · OpenCV · Trimesh
Export	GLTFExporter · STLExporter
🛡️ Performance Optimizations

pixelRatio = 1 → avoids GPU overload

Single WebGL context → prevents crashes

40 FPS throttle → reduces GPU usage

No shadow maps → faster rendering

Context recovery system

💥 Unique Selling Points (USP)
🔥 Browser-Based AR Try-On

Real-time jewelry try-on using webcam

No mobile app or AR SDK required

🧠 Context-Aware AI

Detects body placement (ear, neck, finger, wrist)

⚡ Zero Setup

Runs instantly — no installation

🎨 Full Customization + Export

From image → 3D → customization → export

🏆 Why This Stands Out

Gemcraft AI is not just a generator — it is a complete AI-powered jewelry platform that combines image understanding, 3D generation, and real-time AR try-on directly in the browser.

📁 Project Structure
gemcraft-ai/
├── frontend/
│   └── index.html
├── backend/
│   └── server.py
├── models/
├── docs/
├── scripts/
├── requirements.txt
└── README.md
📜 License

MIT License

🙏 Credits

Anthropic Claude (AI Vision)

Three.js (3D Rendering)

OpenCV (Image Processing)

Trimesh (Mesh Generation)

🚀 Final Note

Built as a hackathon prototype with a vision to revolutionize digital jewelry design, customization, and virtual try-on experiences.
