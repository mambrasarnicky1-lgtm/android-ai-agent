"""
NOIR SOVEREIGN COMMANDER SERVER v17.5 [OMEGA MESH]
=======================================================
Zero-Failure Gateway + Dashboard with Direct VPS Connection.
The server itself IS the fallback gateway — APK talks directly here.
"""

import os, json, time, sys, requests, httpx, asyncio
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Noir Sovereign ELITE v17.5 OMEGA-MESH")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BRAIN-01: Integrasi Jalur Otak AI
sys.path.append(os.path.join(BASE_DIR, "..", "noir-vps"))
try:
    from ai_router import AIRouter
    from catalyst import catalyst
    from temporal_memory import global_memory as memory
except ImportError:
    AIRouter = None # Fallback jika module belum siap

# --- PROXY CONFIG ---
CF_GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev").rstrip("/")
CF_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
CF_HEADERS = {"Authorization": f"Bearer {CF_KEY}", "Content-Type": "application/json"}

# --- LOCAL AGENT STATE (Direct VPS Mode) ---
# This dict persists in memory. When APK polls /agent/poll directly,
# we track it here and expose it via /api/status as a fallback.
import threading

local_state = {
    "agents": {},       # device_id -> {last_seen, stats, last_screenshot}
    "commands": [],     # pending commands
    "logs": [],         # recent logs
    "cf_online": None,  # Cloudflare reachability cache
    "cf_checked_at": 0
}
# VPS-04 FIX: Lock untuk mencegah race condition pada commands list
_commands_lock = threading.Lock()

def _cf_is_reachable():
    """VPS-02 FIX: Fungsi sync ini hanya dipanggil dari executor, bukan langsung dari async handler.
    Cache result 30s untuk mengurangi frekuensi cek."""
    if time.time() - local_state["cf_checked_at"] < 30:
        return local_state["cf_online"]
    try:
        r = requests.get(f"{CF_GATEWAY}/health", timeout=3)
        local_state["cf_online"] = r.status_code == 200
    except:
        local_state["cf_online"] = False
    local_state["cf_checked_at"] = time.time()
    return local_state["cf_online"]

async def _cf_reachable_async() -> bool:
    """VPS-02 FIX: Async wrapper — jalankan sync check di thread executor agar event loop tidak diblokir."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _cf_is_reachable)

def _agent_is_online(device_id="REDMI_NOTE_14"):
    """LINK-02: Threshold 90s sudah konsisten dengan Cloudflare (kini juga 90s)."""
    agent = local_state["agents"].get(device_id, {})
    last = agent.get("last_seen", 0)
    return (time.time() - last) < 90

def _verify_api_key(request: Request) -> bool:
    """VPS-05 FIX: Validasi API key pada endpoint agent langsung."""
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {CF_KEY}"

# =============================================================================
# HEALTH & DIRECT AGENT ENDPOINTS (For APK Direct Connection)
# =============================================================================

# --- NEURAL MESH PAIRING (v19.6) ---
@app.post("/mesh/pair")
async def mesh_pair(request: Request):
    """Autonomously pair an AI Agent device with the Dashboard mesh."""
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
    try:
        data = await request.json()
        did = data.get("device_id", "UNKNOWN")
        token = data.get("mesh_token", "NONE")
        
        if did not in local_state["agents"]:
            local_state["agents"][did] = {}
        
        local_state["agents"][did].update({
            "mesh_status": "PAIRED",
            "mesh_token": token,
            "capabilities": data.get("capabilities", []),
            "last_seen": time.time()
        })
        
        print(f"[MESH] Autonomous Pairing Success: {did} (Token: {token[:8]})")
        return {"status": "PAIRED", "mesh_link": "STABLE"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health():
    return {"status": "ok", "version": "21.0-AEGIS-SINGULARITY", "mode": "direct_vps", "mesh": "ACTIVE"}

@app.post("/agent/register")
async def agent_register(request: Request):
    # VPS-05 FIX: Validasi API key — tolak agen palsu
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
    try:
        data = await request.json()
        did = data.get("device_id", "REDMI_NOTE_14")
        if did not in local_state["agents"]:
            local_state["agents"][did] = {}
        local_state["agents"][did].update({
            "name": data.get("agent", did),
            "last_seen": time.time(),
            "stats": data.get("stats", {})
        })
        # Also forward to Cloudflare if reachable
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{CF_GATEWAY}/agent/register", headers=CF_HEADERS, json=data, timeout=3.0)
            except: pass
        return {"status": "ok", "mode": "registered_on_vps"}
    except Exception as e:
        return {"status": "ok", "error": str(e)}

@app.api_route("/agent/poll", methods=["GET", "POST"])
async def agent_poll(request: Request, device_id: str = "REDMI_NOTE_14", client_type: str = "main"):
    # VPS-05 FIX: Validasi API key sebelum update state agent
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
    # Update agent liveness
    if device_id not in local_state["agents"]:
        local_state["agents"][device_id] = {}
    local_state["agents"][device_id]["last_seen"] = time.time()
    try:
        if request.method == "POST":
            body = await request.json()
            local_state["agents"][device_id]["stats"] = body.get("stats", {})
    except: pass

    # VPS-04 FIX: Gunakan lock saat membaca dan memodifikasi commands list
    with _commands_lock:
        cmds = [c for c in local_state["commands"] if c.get("target", "REDMI_NOTE_14") == device_id]
        local_state["commands"] = [c for c in local_state["commands"] if c not in cmds]

    # Also try to forward to Cloudflare and merge commands
    if await _cf_reachable_async():
        try:
            stats = local_state["agents"][device_id].get("stats", {})
            async with httpx.AsyncClient() as client:
                r = await client.post(f"{CF_GATEWAY}/agent/poll?device_id={device_id}&client_type={client_type}",
                                  headers=CF_HEADERS, json={"stats": stats}, timeout=4.0)
                if r.status_code == 200:
                    cf_cmds = r.json().get("commands", [])
                    cmds.extend(cf_cmds)
        except: pass

    return {"status": "ok", "commands": cmds, "link": "DIRECT_VPS"}

@app.post("/agent/log")
async def agent_log(request: Request):
    try:
        data = await request.json()
        local_state["logs"].append({**data, "ts": time.time()})
        if len(local_state["logs"]) > 200:
            local_state["logs"] = local_state["logs"][-150:]
        # Forward to Cloudflare if reachable
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{CF_GATEWAY}/agent/log", headers=CF_HEADERS, json=data, timeout=3.0)
            except: pass
        return {"ok": True}
    except: return {"ok": False}

@app.post("/agent/result")
async def agent_result(request: Request):
    try:
        data = await request.json()
        # Store result locally
        cid = data.get("command_id", "unknown")
        for c in local_state["commands"]:
            if c.get("command_id") == cid:
                c["status"] = "done"
                c["result"] = data
        # Forward to Cloudflare
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{CF_GATEWAY}/agent/result", headers=CF_HEADERS, json=data, timeout=4.0)
            except: pass
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/agent/upload")
async def agent_upload(request: Request):
    """VPS-03 FIX: Proxy ke Cloudflare R2, atau simpan lokal sebagai fallback agar screenshot tidak hilang."""
    device_id = request.query_params.get("device_id", "REDMI_NOTE_14")
    body = await request.body()
    try:
        if await _cf_reachable_async():
            async with httpx.AsyncClient() as client:
                r = await client.post(f"{CF_GATEWAY}/agent/upload?device_id={device_id}",
                                      headers={"Authorization": f"Bearer {CF_KEY}"},
                                      content=body, timeout=20.0)
                result = r.json()
                if result.get("key"):
                    if device_id not in local_state["agents"]:
                        local_state["agents"][device_id] = {}
                    local_state["agents"][device_id]["last_screenshot"] = result["key"]
                return result
    except Exception as e:
        pass  # Fallthrough to local storage

    # VPS-03 FIX: Local fallback — simpan ke disk VPS
    try:
        ss_dir = os.path.join(BASE_DIR, "screenshots")
        os.makedirs(ss_dir, exist_ok=True)
        local_key = f"local_ss_{int(time.time())}.jpg"
        local_path = os.path.join(ss_dir, local_key)
        with open(local_path, "wb") as f:
            f.write(body)
        # Update agent state dengan local key
        if device_id not in local_state["agents"]:
            local_state["agents"][device_id] = {}
        local_state["agents"][device_id]["last_screenshot"] = f"local:{local_key}"
        local_state["agents"][device_id]["last_seen"] = time.time()
        return {"ok": True, "key": f"local:{local_key}", "mode": "local_fallback"}
    except Exception as e:
        return {"ok": False, "error": f"CF unreachable + local fallback failed: {e}"}

# =============================================================================
# DASHBOARD API ENDPOINTS
# =============================================================================

@app.get("/api/status")
async def api_status():
    """Smart status: Cloudflare primary, local state fallback."""
    cf_up = _cf_is_reachable()
    if cf_up:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{CF_GATEWAY}/agent/summary", headers=CF_HEADERS, timeout=5.0)
                d = r.json()
                # Merge with local: if CF says offline but local says online, trust local
                if not d.get("online") and _agent_is_online():
                    agent_data = local_state["agents"].get("REDMI_NOTE_14", {})
                    d["online"] = True
                    d["link_mode"] = "DIRECT_VPS_MERGED"
                    if not d.get("agent"):
                        d["agent"] = {"stats": agent_data.get("stats", {}), "last_screenshot": agent_data.get("last_screenshot")}
                return d
        except: pass

    # Full local fallback
    is_online = _agent_is_online()
    agent_data = local_state["agents"].get("REDMI_NOTE_14", {})
    return {
        "online": is_online,
        "link_mode": "DIRECT_VPS_ONLY",
        "cf_status": "UNREACHABLE",
        "agent": {
            "name": agent_data.get("name", "REDMI_NOTE_14"),
            "last_seen": agent_data.get("last_seen", 0),
            "stats": agent_data.get("stats", {}),
            "last_screenshot": agent_data.get("last_screenshot")
        } if is_online else None,
        "commands": []
    }

@app.get("/api/summary")
async def api_summary():
    """Unified endpoint for the new V20.1 UI."""
    status = await api_status()
    # Get recent logs (last 5)
    recent_logs = [l for l in local_state["logs"] if l.get("device_id") == "REDMI_NOTE_14"][-5:]
    # Clear logs after sending (since UI appends them)
    # Actually, better to keep them and let UI handle duplicates or use a timestamp
    
    return {
        **status,
        "logs": recent_logs,
        "server_time": time.time()
    }


@app.get("/api/logs")
async def api_logs(device_id: str = "REDMI_NOTE_14"):
    if await _cf_reachable_async():
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{CF_GATEWAY}/agent/logs?device_id={device_id}", headers=CF_HEADERS, timeout=5.0)
                return r.json()
        except: pass
    # Local fallback
    return [l for l in local_state["logs"] if l.get("device_id") == device_id][-50:]

@app.post("/api/command")
async def api_command(request: Request):
    try:
        data = await request.json()
        action = data.get("action", {})
        description = data.get("description", "Commander Action")
        target_device = data.get("target_device", "REDMI_NOTE_14")
        cmd_id = f"CMD_{int(time.time())}"
        payload = {"action": action, "description": description, "target_device": target_device}

        # Try Cloudflare first
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.post(f"{CF_GATEWAY}/agent/command", headers=CF_HEADERS, json=payload, timeout=5.0)
                    return r.json()
            except: pass

        # VPS-04 FIX: Gunakan lock saat menambahkan command baru
        with _commands_lock:
            local_state["commands"].append({
                "command_id": cmd_id,
                "action": action,
                "target": target_device,
                "queued_at": time.time()
            })
        return {"status": "queued_direct_vps", "command_id": cmd_id}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/assets")
async def api_assets():
    if await _cf_reachable_async():
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{CF_GATEWAY}/agent/assets", headers=CF_HEADERS, timeout=5.0)
                return r.json()
        except: pass
    return []

@app.get("/api/asset/{key}")
async def proxy_asset(key: str):
    target_key = key
    if key == "latest":
        agent = local_state["agents"].get("REDMI_NOTE_14", {})
        target_key = agent.get("last_screenshot")
        if not target_key:
            if await _cf_reachable_async():
                try:
                    async with httpx.AsyncClient() as client:
                        r = await client.get(f"{CF_GATEWAY}/agent/summary", headers=CF_HEADERS, timeout=5.0)
                        target_key = r.json().get("agent", {}).get("last_screenshot")
                except: pass
        if not target_key:
            return Response(status_code=404, content="No screenshot available")
    if await _cf_reachable_async():
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{CF_GATEWAY}/agent/asset/{target_key}", headers=CF_HEADERS, timeout=15.0)
                if r.status_code == 200:
                    return Response(content=r.content, media_type=r.headers.get("content-type", "image/png"))
        except: pass
    return Response(status_code=502, content="Asset unavailable")

@app.get("/api/memory")
async def get_memory():
    try:
        mem_path = os.path.join(os.path.dirname(BASE_DIR), "knowledge", "temporal_memory.json")
        if os.path.exists(mem_path):
            with open(mem_path, "r") as f:
                data = json.load(f)
            interactions = data.get("interactions", [])
            preferences = data.get("preferences", {})
            return {"success": True, "stats": {
                "total_interactions": len(interactions),
                "last_active": interactions[-1].get("timestamp") if interactions else "Never",
                "top_preferences": list(preferences.keys())[:5],
                "memory_size": f"{os.path.getsize(mem_path) / 1024:.2f} KB"
            }, "preferences": preferences}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return {"success": False, "error": "Memory not initialized."}

@app.get("/api/skills")
async def get_skills():
    """Neural Skill Matrix: Real-time capability visualization."""
    return {
        "active": [
            "🛡️ Aegis Interception v2.0",
            "👁️ Vision Sentinel v18.5",
            "🔊 Voice Link v19.5",
            "🧬 Neural Mesh Handshake v19.6",
            "🧩 Local AI Reasoning (TinyLlama)"
        ],
        "learning": ["Autonomous Multi-Device Orchestration"],
        "growth": "99.2%",
        "status": "ELITE_SOVEREIGN"
    }

@app.get("/api/agent-task")
async def get_agent_task():
    """Expose current AI agent auto-connection task status to dashboard."""
    cf_up = _cf_is_reachable()
    agent_online = _agent_is_online()
    agent_data = local_state["agents"].get("REDMI_NOTE_14", {})
    return {
        "task": "AUTO_CONNECTION_GUARDIAN",
        "status": "ONLINE" if agent_online else "SEARCHING",
        "cloudflare_up": cf_up,
        "vps_direct_link": agent_online,
        "last_seen_ago": round(time.time() - agent_data.get("last_seen", 0)) if agent_data else None,
        "active_route": "CLOUDFLARE" if (cf_up and agent_online) else ("DIRECT_VPS" if agent_online else "SEVERED")
    }

@app.get("/download-apk")
async def download_apk():
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
                apks.sort(key=os.path.getmtime, reverse=True)
                apk_path = apks[0]
                break
    if apk_path and os.path.exists(apk_path):
        from fastapi.responses import FileResponse
        return FileResponse(apk_path, media_type="application/vnd.android.package-archive", filename=os.path.basename(apk_path))
    return Response(content="⚠️ Build Artifact Not Ready.", status_code=404)

# =============================================================================
# NEURAL HUB & AI BRAIN ENDPOINTS
# =============================================================================

@app.post("/api/brain/chat")
async def brain_chat(request: Request):
    """Integrasi Neural Hub: Menerima perintah bahasa alami dan memprosesnya."""
    if not AIRouter:
        return {"response": "Brain Engine not found on VPS.", "status": "error"}
    
    try:
        data = await request.json()
        prompt = data.get("message", "")
        
        # 1. Tanya ke AI Router (Gemini/DeepSeek)
        response = AIRouter.smart_query(prompt)
        
        # 2. Analisis apakah perintah butuh aksi ke HP
        action = None
        if any(x in response.lower() for x in ["screenshot", "layar", "capture"]):
            action = {"type": "screenshot"}
        elif any(x in response.lower() for x in ["tekan", "click", "tap"]):
            pass
            
        if action:
             with _commands_lock:
                 local_state["commands"].append({
                     "id": hex(int(time.time()))[2:].upper(),
                     "action": action,
                     "status": "pending",
                     "target_device": "REDMI_NOTE_14"
                 })

        return {
            "response": response,
            "status": "success",
            "autonomous_action": action
        }
    except Exception as e:
        return {"response": f"Neural Link Error: {str(e)}", "status": "error"}

@app.get("/api/brain/status")
async def brain_status():
    return {
        "memory_size": 0,
        "skills": ["Aegis", "Vision", "Voice", "Mesh", "RAG"],
        "uptime": time.time()
    }

# ── NEW: Chat History & Relay ──────────────────────────
_chat_history = []

@app.post("/api/brain/chat")
async def brain_chat_v2(request: Request):
    """AI Chat Relay — Uses Gemini API with local fallback."""
    try:
        data = await request.json()
        prompt = data.get("message", "")
        device_id = data.get("device_id", "REDMI_NOTE_14")

        # Try Gemini API
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        response_text = None

        if gemini_key:
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
                        json={"contents": [{"parts": [{"text": f"You are Noir Sovereign AI Agent. Answer concisely in the same language as the user: {prompt}"}]}]},
                        timeout=15.0
                    )
                    if r.status_code == 200:
                        response_text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"[BRAIN] Gemini error: {e}")

        # Fallback response
        if not response_text:
            response_text = f"[Noir Sovereign — Local Mode] Perintah '{prompt}' diterima. Neural Brain sedang menganalisis. Pastikan GEMINI_API_KEY dikonfigurasi untuk respons AI penuh."

        # Store chat history
        _chat_history.append({"role": "user", "msg": prompt, "ts": time.strftime("%H:%M:%S")})
        _chat_history.append({"role": "ai", "msg": response_text, "ts": time.strftime("%H:%M:%S")})
        if len(_chat_history) > 200:
            _chat_history[:] = _chat_history[-200:]

        # Check if response implies device action
        action = None
        kw_map = {"screenshot": "screenshot", "capture": "screenshot", "lokasi": "location", "gps": "location",
                  "vibrate": "vibrate", "gallery": "gallery_sync", "audio": "audio_record"}
        for kw, atype in kw_map.items():
            if kw in prompt.lower():
                action = {"type": atype}
                with _commands_lock:
                    local_state["commands"].append({
                        "id": hex(int(time.time()))[2:].upper(),
                        "action": action, "status": "pending",
                        "target_device": device_id
                    })
                break

        return {"response": response_text, "status": "success", "autonomous_action": action}

    except Exception as e:
        return {"response": f"Error: {str(e)}", "status": "error"}

@app.get("/api/chat/history")
async def get_chat_history():
    return {"history": _chat_history[-50:]}

# ── NEW: Evolution Proposals ──────────────────────────
@app.get("/api/evolutions")
async def get_evolutions():
    """Return pending evolution proposals from commands queue."""
    evo = [c for c in local_state.get("commands", []) if "evolution" in str(c.get("description", "")).lower()]
    # Also check CF
    if await _cf_reachable_async():
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{CF_GATEWAY}/agent/summary", headers=CF_HEADERS, timeout=5.0)
                cf_cmds = r.json().get("commands", [])
                cf_evo = [c for c in cf_cmds if "evolution" in str(c.get("description","")).lower()]
                evo.extend(cf_evo)
        except: pass
    return {"evolutions": evo}

# ── NEW: Log Visibility Control ───────────────────────
_log_visibility = {"visible": True}

@app.post("/api/log-visibility")
async def set_log_visibility(request: Request):
    data = await request.json()
    _log_visibility["visible"] = data.get("visible", True)
    # Push command to APK to suppress UI log display
    with _commands_lock:
        local_state["commands"].append({
            "id": hex(int(time.time()))[2:].upper(),
            "action": {"type": "log_visibility", "visible": _log_visibility["visible"]},
            "status": "pending",
            "target_device": "REDMI_NOTE_14"
        })
    return {"ok": True, "visible": _log_visibility["visible"]}

@app.get("/api/log-visibility")
async def get_log_visibility():
    return _log_visibility

# ── Static File Serving ───────────────────────────────
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/css/{filename}")
async def serve_css(filename: str):
    path = os.path.join(BASE_DIR, "css", filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="text/css")
    return Response(status_code=404)

@app.get("/js/{filename}")
async def serve_js(filename: str):
    path = os.path.join(BASE_DIR, "js", filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="application/javascript")
    return Response(status_code=404)

@app.get("/")
async def get_index():
    path = os.path.join(BASE_DIR, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    ports = [80, 8000, 5000, 9090]
    for port in ports:
        try:
            print(f"[START] Noir Sovereign v21.0 AEGIS on Port {port}...")
            uvicorn.run(app, host="0.0.0.0", port=port)
            break
        except Exception as e:
            print(f"[WARN] Port {port} unavailable: {e}")
            if port == ports[-1]:
                print("[FATAL] No available ports found.")



                print("[FATAL] No available ports found.")

