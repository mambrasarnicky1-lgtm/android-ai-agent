"""
NOIR SOVEREIGN BACKGROUND SERVICE v14.3.00
=======================================
Synchronized background engine with Autonomous Sentinel and Shizuku Bridge.
"""

import os
import time
import requests
import threading
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIG (Unified Standard v14.3.00) ---
GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14_ELITE_V16")
OFFLINE_LOG_FILE = os.path.join(os.path.dirname(__file__), "service_offline.log")

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def noir_log(message, level="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] [SERVICE-{level}] {message}"
    print(formatted_msg)
    
    # Persistent Offline Log
    try:
        with open(OFFLINE_LOG_FILE, "a") as f:
            f.write(formatted_msg + "\n")
    except: pass

    def _send():
        try:
            session.post(
                f"{GATEWAY_URL}/agent/log",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"device_id": DEVICE_ID, "level": level, "message": f"[BG-SERVICE] {message}"},
                timeout=5
            )
        except: pass
    threading.Thread(target=_send, daemon=True).start()

def run_service():
    noir_log("🌑 NOIR ELITE SERVICE v16.0.03: INITIALIZING...")
    
    # Process Purge: Kill old ghosts if this is a fresh start
    try:
        os.system("pkill -f org.noir.agent.noir_smc")
    except: pass

    poll_interval = 5
    while True:
        try:
            # Connectivity Check
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                is_online = True
            except:
                is_online = False

            if not is_online:
                noir_log("Offline state. Retrying in 30s...", level="WARNING")
                time.sleep(30)
                continue

            headers = {"Authorization": f"Bearer {API_KEY}"}
            resp = session.get(
                f"{GATEWAY_URL}/agent/poll",
                headers=headers,
                params={"device_id": DEVICE_ID},
                timeout=20
            )

            if resp.status_code == 200:
                data = resp.json()
                commands = data.get("commands", [])
                if commands:
                    noir_log(f"Received {len(commands)} background commands")
                    poll_interval = 2
                    for cmd in commands:
                        try:
                            action = cmd.get("action", {})
                            atype = action.get("type") or action.get("action", "")
                            params = action.get("params", action)
                            if atype == "shell":
                                shell_cmd = params.get("cmd", "")
                                import subprocess
                                subprocess.run(shell_cmd, shell=True, timeout=15)
                                noir_log(f"Executed BG Shell: {shell_cmd}")
                        except Exception as ce:
                            noir_log(f"BG Exec Error: {ce}", level="WARNING")
                else:
                    poll_interval = min(poll_interval + 2, 30)
            
            time.sleep(poll_interval)
            
        except Exception as e:
            noir_log(f"Service Loop Error: {e}", level="WARNING")
            time.sleep(30)

if __name__ == '__main__':
    run_service()
