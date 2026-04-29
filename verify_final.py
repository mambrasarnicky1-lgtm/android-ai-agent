"""
FINAL VERIFICATION — Noir Sovereign V21.0 AEGIS
"""
import requests

GATEWAY = "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev"
VPS_API = "http://8.215.23.17:80"
KEY     = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

print("=" * 60)
print("  FINAL STATE VERIFICATION — V21.0 AEGIS")
print("=" * 60)

# 1. VPS Health
r = requests.get(f"{VPS_API}/health", headers=HEADERS, timeout=8)
d = r.json()
print(f"\n[VPS]     Status : HTTP {r.status_code}")
print(f"[VPS]     Version: {d.get('version','?')}")
print(f"[VPS]     Mode   : {d.get('mode','?')}")

# 2. CF Gateway Health  
r = requests.get(f"{GATEWAY}/health", timeout=8)
d = r.json()
print(f"\n[CF GW]   Status : HTTP {r.status_code}")
print(f"[CF GW]   Version: {d.get('version','?')}")

# 3. Agent Live State
r = requests.get(f"{VPS_API}/api/summary", headers=HEADERS, timeout=10)
d = r.json()
agent = d.get("agent") or {}
pending = [c for c in d.get("commands", []) if c.get("status") == "pending"]
print(f"\n[AGENT]   Online : {d.get('online', False)}")
print(f"[AGENT]   Name   : {agent.get('name', 'N/A')}")
stats = agent.get("stats", {})
print(f"[AGENT]   Version: {stats.get('version', 'N/A')}")
print(f"[AGENT]   Shizuku: {stats.get('shizuku', 'N/A')}")

# 4. CF Direct Agent State
r2 = requests.get(f"{GATEWAY}/agent/summary", headers=HEADERS, timeout=10)
d2 = r2.json()
cf_pending = [c for c in d2.get("commands", []) if c.get("status") == "pending"]
print(f"\n[CF QUEUE] Pending Commands: {len(cf_pending)}")

print(f"\n[LOCAL QUEUE] Pending Commands: {len(pending)}")

print("\n" + "=" * 60)
if len(pending) == 0 and len(cf_pending) == 0:
    print("  STATUS: QUEUE CLEAN - APK READY TO CONNECT")
else:
    print(f"  STATUS: {len(cf_pending)} CF + {len(pending)} VPS commands still pending")
print("=" * 60)

print("""
BUILD DOWNLOAD LINK:
  -> https://github.com/mambrasarnicky1-lgtm/android-ai-agent/actions
  -> Klik workflow 'Noir Sovereign V21.0 AEGIS Build' yang terbaru
  -> Download artifact: Noir-Sovereign-V21.0-AEGIS-APK
  -> Extract .zip -> install .apk pada Redmi Note 14
""")
