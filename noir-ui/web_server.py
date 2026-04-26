"""
NOIR OMNI-SOVEREIGN COMMANDER SERVER v14.0 COMMANDER
=========================================================
Unified Command Center with Multi-Menu Architecture.
Features: Live Vision, Camera Sensors, Media Loot, Neural Chat, Evolution Manifest.
"""

import os, json, time, sys, requests, httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env from root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Noir Sovereign ELITE v16.0.02")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- PROXY CONFIG (Unified Standard v17.5 Auto-Discovery) ---
_BASE_GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
VPS_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
FALLBACKS = [_BASE_GATEWAY, "http://127.0.0.1", "http://127.0.0.1:80", f"http://{VPS_IP}", f"http://{VPS_IP}:80", f"http://{VPS_IP}:8000", "http://127.0.0.1:8787"]

class DynamicGateway:
    _current = None
    @classmethod
    def get(cls):
        if cls._current: return cls._current
        for gw in FALLBACKS:
            try:
                if requests.get(f"{gw}/health", timeout=2).status_code == 200:
                    cls._current = gw
                    print(f"✅ Auto-Discovery: Gateway matched -> {gw}")
                    return gw
            except: pass
        return _BASE_GATEWAY

class _GatewayProxy:
    def __str__(self): return DynamicGateway.get()
    def __format__(self, format_spec): return format(str(self), format_spec)
    def rstrip(self, chars=None): return str(self).rstrip(chars)

CF_GATEWAY = _GatewayProxy()
CF_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")

CF_HEADERS = {"Authorization": f"Bearer {CF_KEY}", "Content-Type": "application/json"}

# --- EMERGENCY DIRECT VPS GATEWAY (Zero-Failure Fallback) ---
local_agent_state = {
    "online": False,
    "last_seen": 0,
    "commands": [],
    "logs": []
}

@app.get("/health")
def health():
    return {"status": "ok", "version": "17.5-AutoDiscovery"}

@app.get("/agent/poll")
def local_poll(device_id: str = "REDMI_NOTE_14", client_type: str = "main"):
    local_agent_state["online"] = True
    local_agent_state["last_seen"] = time.time()
    cmds = local_agent_state["commands"].copy()
    local_agent_state["commands"].clear()
    return {"commands": cmds, "status": "direct_vps_link_active"}

@app.post("/agent/log")
async def local_log(request: Request):
    try:
        data = await request.json()
        local_agent_state["logs"].append(data)
        if len(local_agent_state["logs"]) > 100:
            local_agent_state["logs"].pop(0)
        return {"success": True}
    except: return {"success": False}


@app.get("/api/status")
async def api_status():
    # If CF fails, fallback to local state
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{CF_GATEWAY}/agent/summary", headers=CF_HEADERS, timeout=5.0)
            return r.json()
    except Exception as e:
        is_online = (time.time() - local_agent_state["last_seen"]) < 60
        return {
            "online": is_online, 
            "agent": {"stats": {"cpu": "N/A (Direct Link)", "ram": "N/A"}},
            "connection": "DIRECT_VPS_FALLBACK"
        }

@app.get("/api/logs")
async def api_logs(device_id: str = "REDMI_NOTE_14"):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{CF_GATEWAY}/agent/logs?device_id={device_id}", headers=CF_HEADERS, timeout=20.0)
            return r.json()
    except Exception as e:
        return []

@app.post("/api/command")
async def api_command(request: Request):
    try:
        data = await request.json()
        payload = {
            "action": data.get("action", {}),
            "description": data.get("description", "Commander Action"),
            "target_device": "REDMI_NOTE_14"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(f"{CF_GATEWAY}/agent/command", headers=CF_HEADERS, json=payload, timeout=5.0)
                return r.json()
        except:
            # Fallback to local queue if CF is down
            local_agent_state["commands"].append({
                "command_id": f"cmd_{int(time.time())}",
                "action": payload["action"]
            })
            return {"status": "queued_locally", "warning": "CF Gateway unreachable, using Direct VPS Link"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/assets")
async def api_assets():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{CF_GATEWAY}/agent/assets", headers=CF_HEADERS, timeout=10.0)
            return r.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/asset/{key}")
async def proxy_asset(key: str):
    try:
        # Special case for "latest"
        target_key = key
        if key == "latest":
            async with httpx.AsyncClient() as client:
                try:
                    r = await client.get(f"{CF_GATEWAY}/agent/summary", headers=CF_HEADERS, timeout=5.0)
                    summary = r.json()
                    target_key = summary.get("agent", {}).get("last_screenshot")
                    if not target_key:
                        # Fallback: return a 1x1 transparent pixel or 404
                        return Response(status_code=404, content="No screenshot available")
                except:
                    return Response(status_code=404, content="Gateway unreachable")
        
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(f"{CF_GATEWAY}/agent/asset/{target_key}", headers=CF_HEADERS, timeout=15.0)
                if r.status_code != 200:
                    return Response(status_code=r.status_code, content="Asset not found")
                return Response(content=r.content, media_type=r.headers.get("content-type", "image/png"))
            except:
                return Response(status_code=502, content="Failed to fetch asset")
    except Exception as e:
        return {"error": str(e)}

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
    try:
        skill_path = os.path.join(os.path.dirname(BASE_DIR), "knowledge", "skill_library.json")
        if os.path.exists(skill_path):
            with open(skill_path, "r") as f:
                skills_data = json.load(f)
                return {
                    "active": list(skills_data.keys()),
                    "learning": ["Autonomous Bridge v16"],
                    "growth": "94.2%",
                    "proposal": "Sistem Elite v16 sedang mengoptimalkan jalur Shizuku."
                }
    except: pass
    
    return {
        "active": ["Vision Analysis", "Autonomous Research", "Camera Sensor Control", "Elite Persistence"],
        "learning": ["Recursive Optimization v15", "Shizuku Auto-Bridge"],
        "growth": "92.7%",
        "proposal": "Sistem 'Self-Healing Mirroring' telah diaktifkan."
    }

@app.get("/api/memory")
async def get_memory():
    try:
        # Path to memory file
        mem_path = os.path.join(os.path.dirname(BASE_DIR), "knowledge", "temporal_memory.json")
        if os.path.exists(mem_path):
            with open(mem_path, "r") as f:
                data = json.load(f)
                interactions = data.get("interactions", [])
                preferences = data.get("preferences", {})
                
                # Basic stats
                stats = {
                    "total_interactions": len(interactions),
                    "last_active": interactions[-1].get("timestamp") if interactions else "Never",
                    "top_preferences": list(preferences.keys())[:5],
                    "memory_size": f"{os.path.getsize(mem_path) / 1024:.2f} KB"
                }
                return {"success": True, "stats": stats, "preferences": preferences}
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Memory not initialized."}

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
    # v16.0.03: Smart-Port Dynamic Allocation
    ports = [80, 8000, 5000, 9090]
    for port in ports:
        try:
            print(f"[START] Attempting to start Noir Commander on Port {port}...")
            uvicorn.run(app, host="0.0.0.0", port=port)
            break
        except Exception as e:
            print(f"[WARN] Port {port} unavailable: {e}")
            if port == ports[-1]:
                print("[FATAL] No available ports found. Check VPS firewall.")
