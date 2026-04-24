import requests
import json
import os
from dotenv import load_dotenv

# Load env from root
load_dotenv(".env")

GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID   = "REDMI_NOTE_14_ELITE_V16"

def check_status():
    print(f"--- NOIR V16 DIAGNOSTICS ---")
    print(f"Target Device: {DEVICE_ID}")
    print(f"Gateway: {GATEWAY_URL}")
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        # Check Agent Registration
        r = requests.get(f"{GATEWAY_URL}/agent/summary", headers=headers, timeout=10)
        data = r.json()
        
        if data.get("online"):
            print("Status: [ONLINE] ✅")
            print(f"Last Seen: {data['agent']['last_seen']}")
            print(f"Stats: {data['agent'].get('stats', {})}")
        else:
            print("Status: [OFFLINE] ❌ (Waiting for APK install...)")
            
        # Check Logs
        rl = requests.get(f"{GATEWAY_URL}/agent/logs?device_id={DEVICE_ID}", headers=headers, timeout=10)
        logs = rl.json()
        if logs:
            print(f"\nRecent Logs (V16):")
            for log in logs[:5]:
                print(f"[{log['level']}] {log['message']}")
        else:
            print("\nLogs: No data yet.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_status()
