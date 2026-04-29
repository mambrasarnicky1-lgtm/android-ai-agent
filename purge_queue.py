"""
QUEUE PURGE SCRIPT — Force-complete all stale commands on Cloudflare Gateway
"""
import requests
import json

GATEWAY = "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev"
VPS_API = "http://8.215.23.17:80"
KEY     = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
DEVICE  = "REDMI_NOTE_14"

print("=== NOIR QUEUE PURGE ===\n")

# 1. Get all pending commands from VPS (which mirrors CF state)
r = requests.get(f"{VPS_API}/api/summary", headers=HEADERS, timeout=10)
data = r.json()
cmds = data.get("commands", [])
print(f"Commands found: {len(cmds)}")

# 2. Force-complete every pending command by submitting a 'done' result
purged = 0
for cmd in cmds:
    cid = cmd.get("id", "")
    if not cid:
        continue
    status = cmd.get("status", "")
    print(f"  Purging [{status}] {cid[:8]}... ", end="")

    # Post a forced-done result to both CF and VPS
    payload = {
        "command_id": cid,
        "device_id": DEVICE,
        "success": False,
        "output": "",
        "error": "PURGED_BY_HEALER",
        "telemetry": {"cpu": 0, "ram": 0, "bat": 0}
    }
    try:
        r2 = requests.post(f"{GATEWAY}/agent/result", headers=HEADERS, json=payload, timeout=8)
        print(f"CF:{r2.status_code}", end="  ")
    except Exception as e:
        print(f"CF:ERR({e})", end="  ")
    try:
        r3 = requests.post(f"{VPS_API}/agent/result", headers=HEADERS, json=payload, timeout=8)
        print(f"VPS:{r3.status_code}")
    except Exception as e:
        print(f"VPS:ERR({e})")
    purged += 1

print(f"\nTotal purged: {purged} commands")

# 3. Verify
r = requests.get(f"{VPS_API}/api/summary", headers=HEADERS, timeout=10)
remaining = len(r.json().get("commands", []))
print(f"Commands remaining after purge: {remaining}")
if remaining == 0:
    print("✅ Queue is CLEAN. APK will receive only fresh commands.")
else:
    print(f"⚠️  {remaining} commands still in queue. May need manual CF KV clear.")
