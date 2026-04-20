"""
NOIR DIRECT BRIDGE SERVER v12.0
===============================
Self-Contained Gateway and Dashboard for Sovereign AI.
Eliminates middleman dependencies (Cloudflare) for maximum reliability.
"""

import os, json, time, sys, sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Noir Sovereign v12.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE SETUP (Local SQLite) ---
DB_PATH = "noir_sovereign.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS commands 
                 (id TEXT PRIMARY KEY, action TEXT, description TEXT, status TEXT, result TEXT, updated_at DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS agents 
                 (device_id TEXT PRIMARY KEY, name TEXT, last_seen DATETIME, stats TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- AGENT ENDPOINTS (Direct from Redmi Note 14) ---

@app.post("/agent/register")
async def agent_register(request: Request):
    data = await request.json()
    device_id = data.get("device_id")
    name = data.get("agent", "Unknown Agent")
    stats = json.dumps(data.get("stats", {}))
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO agents (device_id, name, last_seen, stats) VALUES (?, ?, CURRENT_TIMESTAMP, ?)", 
              (device_id, name, stats))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/agent/poll")
async def agent_poll(device_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, action FROM commands WHERE status = 'pending' LIMIT 5")
    rows = c.fetchall()
    
    cmds = []
    for row in rows:
        cmds.append({"command_id": row[0], "action": json.loads(row[1])})
        c.execute("UPDATE commands SET status = 'sent' WHERE id = ?", (row[0],))
    
    conn.commit()
    conn.close()
    return {"commands": cmds}

@app.post("/agent/result")
async def agent_result(request: Request):
    data = await request.json()
    cid = data.get("command_id")
    res = json.dumps(data)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE commands SET status = 'done', result = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (res, cid))
    conn.commit()
    conn.close()
    return {"status": "ok"}

# --- DASHBOARD ENDPOINTS ---

@app.get("/api/status")
async def api_status():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, last_seen, stats FROM agents ORDER BY last_seen DESC LIMIT 1")
    agent = c.fetchone()
    
    is_online = False
    agent_data = None
    if agent:
        # Check if seen in last 2 minutes
        ts = agent[1] # e.g. "2026-04-20 12:00:00"
        # Simplistic online check
        is_online = True 

        agent_data = {
            "name": agent[0],
            "last_seen": agent[1],
            "stats": json.loads(agent[2]) if agent[2] else {}
        }
    
    c.execute("SELECT id, description, status, updated_at FROM commands ORDER BY updated_at DESC LIMIT 10")
    rows = c.fetchall()
    commands = [{"id": r[0], "desc": r[1], "status": r[2], "ts": r[3]} for r in rows]
    
    conn.close()
    return {"online": is_online, "agent": agent_data, "commands": commands}

@app.post("/api/command")
async def api_command(request: Request):
    data = await request.json()
    action = json.dumps(data.get("action", {}))
    desc = data.get("description", "Manual Control")
    cid = os.urandom(4).hex().upper()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO commands (id, action, description, status, updated_at) VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)", 
              (cid, action, desc))
    conn.commit()
    conn.close()
    return {"status": "queued", "command_id": cid}

@app.get("/")
async def get_index():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("index.html not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
