import requests, os

API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
GATEWAY = "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev"

def trigger():
    print("Initiating Global Self-Evolution Protocol...")
    
    # 1. Trigger Knowledge Refresh
    resp1 = requests.post(f"{GATEWAY}/agent/command", headers={"Authorization": f"Bearer {API_KEY}"}, json={
        "action": {"type": "knowledge_refresh"},
        "description": "Triggered Autonomous Knowledge Sync"
    })
    
    # 2. Trigger Research Mission
    resp2 = requests.post(f"{GATEWAY}/agent/command", headers={"Authorization": f"Bearer {API_KEY}"}, json={
        "action": {"type": "start_mission", "topic": "Advanced HyperOS Background Persistence Techniques 2026"},
        "description": "Autonomous Research: HyperOS Persistence"
    })
    
    # 3. Trigger Full Audit
    resp3 = requests.post(f"{GATEWAY}/agent/command", headers={"Authorization": f"Bearer {API_KEY}"}, json={
        "action": {"type": "full_audit"},
        "description": "Triggered Global System Audit"
    })
    
    print(f"Status: R1={resp1.status_code}, R2={resp2.status_code}, R3={resp3.status_code}")
    print("Self-Evolution Engine: ENGAGED.")

if __name__ == "__main__":
    trigger()
