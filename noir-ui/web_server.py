"""
NOIR OMNI-SOVEREIGN COMMANDER SERVER v14.0 COMMANDER
=========================================================
Unified Command Center with Multi-Menu Architecture.
Features: Live Vision, Camera Sensors, Media Loot, Neural Chat, Evolution Manifest.
"""

import os, json, time, sys, requests
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env from root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Noir Sovereign ELITE v16.0.00")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- PROXY CONFIG (Unified Standard v15) ---
CF_GATEWAY = os.environ.get("NOIR_GATEWAY_URL")
CF_KEY     = os.environ.get("NOIR_API_KEY")

if not CF_GATEWAY or not CF_KEY:
    print("❌ FATAL: NOIR_GATEWAY_URL or NOIR_API_KEY not found in environment.")
    sys.exit(1)

CF_GATEWAY = CF_GATEWAY.rstrip("/")
CF_HEADERS = {"Authorization": f"Bearer {CF_KEY}", "Content-Type": "application/json"}

@app.get("/api/status")
def api_status():
    try:
        r = requests.get(f"{CF_GATEWAY}/agent/summary", headers=CF_HEADERS, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e), "online": False}

@app.get("/api/logs")
def api_logs(device_id: str = "REDMI_NOTE_14_ELITE_V16"):
    try:
        r = requests.get(f"{CF_GATEWAY}/agent/logs?device_id={device_id}", headers=CF_HEADERS, timeout=10)
        return r.json()
    except Exception as e:
        return []

@app.post("/api/command")
async def api_command(request: Request):
    try:
        data = await request.json()
        payload = {
            "action": data.get("action", {}),
            "description": data.get("description", "Commander Action")
        }
        # Run blocking request in a way that doesn't block event loop is complex here because of await request.json()
        # Better: use asyncio.to_thread
        import asyncio
        r = await asyncio.to_thread(requests.post, f"{CF_GATEWAY}/agent/command", headers=CF_HEADERS, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/assets")
def api_assets():
    try:
        r = requests.get(f"{CF_GATEWAY}/agent/assets", headers=CF_HEADERS, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/asset/{key}")
def proxy_asset(key: str):
    try:
        r = requests.get(f"{CF_GATEWAY}/agent/asset/{key}", headers=CF_HEADERS, stream=True)
        return StreamingResponse(r.iter_content(chunk_size=1024), media_type=r.headers.get("content-type"))
    except Exception as e:
        return Response(content=str(e), status_code=500)

@app.get("/api/chat")
async def get_chat():
    return {
        "messages": [
            {"role": "agent", "text": "Protokol v16.0 ELITE Aktif. Jalur Neural Terisolasi.", "time": time.time() - 3600},
            {"role": "system", "text": "Neural Link: REDMI_NOTE_14_ELITE_V16 Connected.", "time": time.time() - 1800},
            {"role": "agent", "text": "Memulai orkestrasi otonom fase puncak.", "time": time.time() - 300}
        ]
    }

@app.get("/api/skills")
async def get_skills():
    # Fetch from catalyst if possible, but for now we'll simulate the growth
    return {
        "active": ["Vision Analysis", "Autonomous Research", "Camera Sensor Control", "Social Media Priority", "Linguistic Synthesis", "Elite Persistence"],
        "learning": ["Recursive Optimization v15", "Shizuku Auto-Bridge"],
        "growth": "92.7%",
        "proposal": "Sistem 'Self-Healing Mirroring' telah diaktifkan."
    }

@app.get("/api/loot")
def get_loot():
    # Fetch latest media from R2
    try:
        r = requests.get(f"{CF_GATEWAY}/agent/assets", headers=CF_HEADERS, timeout=10)
        return r.json()
    except:
        return []

@app.get("/download-apk")
async def download_apk():
    # Primary path: specific release name
    # Base dir is /app/noir-ui, we look in /app/bin or /app/mobile_app/bin
    search_dirs = [
        os.path.join(os.path.dirname(BASE_DIR), "bin"),
        os.path.join(os.path.dirname(BASE_DIR), "mobile_app", "bin"),
        os.path.join(BASE_DIR, "bin")
    ]
    
    apk_path = None
    for d in search_dirs:
        if os.path.exists(d):
            import glob
            apks = glob.glob(os.path.join(d, "*.apk"))
            if apks:
                # Sort by newest
                apks.sort(key=os.path.getmtime, reverse=True)
                apk_path = apks[0]
                break
    
    if apk_path and os.path.exists(apk_path):
        from fastapi.responses import FileResponse
        return FileResponse(apk_path, media_type="application/vnd.android.package-archive", filename=os.path.basename(apk_path))
    
    return Response(content="⚠️ Build Artifact Not Ready. Please trigger a new build on the VPS.", status_code=404)

@app.get("/")
async def get_index():
    # Force read latest index.html
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
