"""
NOIR SOVEREIGN BACKGROUND SERVICE v14.0
=======================================
This service runs in a separate process to ensure the agent stays online 
even when the main UI is closed or killed by the system.
"""

import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIG (Unified Standard v14) ---
# Note: In Android service, we might need to find the .env file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Fallback to defaults
GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def noir_log(message, level="INFO"):
    print(f"[SERVICE-{level}] {message}")
    try:
        session.post(
            f"{GATEWAY_URL}/agent/log",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"device_id": DEVICE_ID, "level": level, "message": f"[BG-SERVICE] {message}"},
            timeout=5
        )
    except: pass

def run_service():
    noir_log("Background Service ACTIVE")
    
    poll_interval = 5
    while True:
        try:
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
                    # In a real service, we would notify the main app or execute 
                    # non-UI commands directly here.
                    poll_interval = 2
                else:
                    poll_interval = min(poll_interval + 2, 30)
            
            time.sleep(poll_interval)
            
        except Exception as e:
            noir_log(f"Service Loop Error: {e}", level="WARNING")
            time.sleep(30)

if __name__ == '__main__':
    run_service()
