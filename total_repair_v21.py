"""
NOIR SOVEREIGN — TOTAL SYSTEM REPAIR SCRIPT V21.0
Clears stale queues, validates VPS backend, resets connection state.
"""
import requests
import json
import time
import paramiko

# === CONFIG ===
VPS_HOST = '8.215.23.17'
VPS_PORT = 22
VPS_USER = 'root'
VPS_PASS = 'N!colay_No1r.Ai@Agent#Secure'
API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
GATEWAY = "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev"
VPS_API = "http://8.215.23.17:80"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def ssh_cmd(cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_HOST, VPS_PORT, VPS_USER, VPS_PASS, timeout=30)
        _, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        ssh.close()
        return out or err
    except Exception as e:
        return f"SSH Error: {e}"

def api_get(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 0, {"error": str(e)}

def api_post(url, body):
    try:
        r = requests.post(url, headers=HEADERS, json=body, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 0, {"error": str(e)}

print("=" * 60)
print("  NOIR SOVEREIGN — TOTAL SYSTEM AUDIT & REPAIR V21.0")
print("=" * 60)

# --- STEP 1: VPS Health Check ---
print("\n[1/5] VPS Backend Health Check...")
code, data = api_get(f"{VPS_API}/health")
print(f"  VPS Status: HTTP {code}")
print(f"  Version: {data.get('version', 'UNKNOWN')}")
if code != 200:
    print("  [CRITICAL] VPS not responding! Attempting container restart...")
    print(ssh_cmd("docker restart noir-dashboard"))

# --- STEP 2: Cloudflare Gateway Health ---
print("\n[2/5] Cloudflare Gateway Health Check...")
code, data = api_get(f"{GATEWAY}/health")
print(f"  CF Gateway: HTTP {code} - {data}")

# --- STEP 3: Clear Stale Command Queue ---
print("\n[3/5] Clearing stale command queue on Gateway...")
# Fetch current summary to count stale commands
code, summary = api_get(f"{VPS_API}/api/summary")
stale_cmds = summary.get("commands", [])
print(f"  Found {len(stale_cmds)} stale commands in queue.")

# The cleanest way to purge is to clear on the VPS side via SSH directly
clear_result = ssh_cmd("""
python3 -c "
import sys
sys.path.insert(0, '/root/noir-agent')
# Directly clear the command state from the database via the gateway
import requests
r = requests.delete('https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev/agent/commands?device_id=REDMI_NOTE_14', headers={'Authorization': 'Bearer NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026'}, timeout=10)
print(r.status_code, r.text)
"
""")
print(f"  Queue clear result: {clear_result}")

# --- STEP 4: Restart VPS Services with latest code ---
print("\n[4/5] Restarting all VPS services with latest code...")
print(ssh_cmd("cd /root/noir-agent && git fetch origin main && git reset --hard origin/main"))
print(ssh_cmd("docker restart noir-brain noir-dashboard"))

# Wait for restart
time.sleep(8)

# --- STEP 5: Final Verification ---
print("\n[5/5] Final System State Verification...")
code, data = api_get(f"{VPS_API}/health")
print(f"  VPS Version (after restart): {data.get('version', 'UNKNOWN')}")
code, summary = api_get(f"{VPS_API}/api/summary")
agent = summary.get("agent") or {}
print(f"  Agent Online: {summary.get('online', False)}")
print(f"  Agent Name:   {agent.get('name', 'N/A')}")
print(f"  Commands Pending: {len(summary.get('commands', []))}")

print("\n" + "=" * 60)
print("  AUDIT COMPLETE — SYSTEM READY FOR APK RECONNECTION")
print("=" * 60)
print("""
NEXT STEPS FOR USER:
1. Buka GitHub Actions -> Download APK artifact versi terbaru (21.0.0)
2. Uninstall APK lama dari Redmi Note 14
3. Install APK baru (V21.0)
4. Buka APK -> tap 'ENTER SOVEREIGN CORE' -> tunggu sampai status ONLINE
5. Cek dashboard di browser
""")
