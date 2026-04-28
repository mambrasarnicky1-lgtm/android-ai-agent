import requests, os, time

API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
GATEWAY = "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev"

def initiate_sovereignty():
    print("[INIT] NOIR SOVEREIGN: INITIATING GLOBAL OPERATION PROTOCOL...")
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    # 1. Trigger Initial Telegram Greeting
    try:
        requests.post(f"{GATEWAY}/agent/command", headers=headers, json={
            "device_id": "TELEGRAM_BOT",
            "action": {"type": "broadcast", "message": "🌑 **NOIR SOVEREIGN V19.5 OMEGA AKTIF!**\nCommander, saya telah mengambil alih seluruh fungsi operasional otonom. Melakukan audit sistem pertama..."}
        }, timeout=10)
        print("[+] Telegram Greeting Sent.")
    except Exception as e: 
        print(f"[-] Telegram Failed: {e}")

    # 2. Trigger First Vision Audit on Mobile
    try:
        requests.post(f"{GATEWAY}/agent/command", headers=headers, json={
            "device_id": "REDMI_NOTE_14",
            "action": {"type": "vision_audit", "desc": "Initial Sovereignty Audit"}
        }, timeout=10)
        print("[+] Vision Sentinel Audit Triggered.")
    except Exception as e:
        print(f"[-] Mobile Failed: {e}")

    # 3. Trigger Neural Mesh Sync
    try:
        requests.post(f"{GATEWAY}/agent/command", headers=headers, json={
            "device_id": "NOIR_PC_MASTER",
            "action": {"type": "mesh_sync", "desc": "Initial Neural Mesh Handshake"}
        }, timeout=10)
        print("[+] Neural Mesh Sync Triggered.")
    except Exception as e:
        print(f"[-] PC Failed: {e}")

    print("[SUCCESS] MISSION STARTED: Noir Sovereign is now operational across all nodes.")

if __name__ == "__main__":
    initiate_sovereignty()
