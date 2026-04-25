"""
NOIR SOVEREIGN BACKGROUND SERVICE v17.1 SENTINEL
===============================================
Synchronized background engine with Autonomous Sentinel and Shizuku Bridge.
"""

import os
import time
import requests
import threading
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIG (Unified Standard v17.1) ---
GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")
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
    noir_log("NOIR ELITE SERVICE v17.2.2 [OMEGA-FIX]: INITIALIZING...")
    
    # WARN-03 FIX: Kill old ghosts using updated package domain
    try:
        os.system("pkill -f org.noir.sovereign")
        os.system("pkill -f org.noir.agent")
    except: pass

    # WARN-01 FIX: Wait 6s for Android network init before first poll
    time.sleep(6)


    poll_interval = 10
    while True:
        try:
            # 1. Connectivity Check
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                is_online = True
            except:
                is_online = False

            if not is_online:
                time.sleep(30)
                continue

            # 2. Unified Poll (Shared with main.py)
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
                    # Note: Service only handles light background tasks.
                    # Complex tasks (vision, etc) are handled by main.py
                    for cmd in commands:
                        try:
                            action = cmd.get("action", {})
                            atype = action.get("type", "")
                            if atype == "shell":
                                import subprocess
                                subprocess.run(action.get("cmd", ""), shell=True, timeout=15)
                        except: pass
                    poll_interval = 5
                else:
                    poll_interval = min(poll_interval + 2, 30)
            
            time.sleep(poll_interval)
            
        except Exception as e:
            time.sleep(30)

if __name__ == '__main__':
    run_service()
