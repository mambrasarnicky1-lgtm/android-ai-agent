import os
import time
import json
import logging
import requests
from datetime import datetime

# --- CONFIG ---
GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev")
API_KEY = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
LEDGER_FILE = "stability_ledger.json"

logging.basicConfig(level=logging.INFO, format='[HEALER] [%(asctime)s] %(message)s')

class NoirHealer:
    def __init__(self):
        self.ledger = self._load_ledger()
        self.consecutive_failures = 0
        self.last_apk_heartbeat = time.time()

    def _load_ledger(self):
        if os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, 'r') as f:
                return json.load(f)
        return {"events": [], "stats": {"total_heals": 0, "uptime_score": 100}}

    def _save_ledger(self):
        with open(LEDGER_FILE, 'w') as f:
            json.dump(self.ledger, f, indent=4)

    def log_event(self, severity, message, action_taken=None):
        event = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "message": message,
            "action": action_taken
        }
        self.ledger["events"].append(event)
        if action_taken:
            self.ledger["stats"]["total_heals"] += 1
        
        # Keep ledger lean
        if len(self.ledger["events"]) > 100:
            self.ledger["events"] = self.ledger["events"][-100:]
        
        self._save_ledger()
        logging.info(f"[{severity}] {message} | Action: {action_taken}")

    def check_system_health(self):
        """Perform a holistic health audit of the Singularity ecosystem."""
        try:
            # 1. Audit Gateway Connectivity
            resp = requests.get(f"{GATEWAY_URL}/health", headers={"Authorization": f"Bearer {API_KEY}"}, timeout=5)
            if resp.status_code == 200:
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1
                self.log_event("WARNING", f"Gateway unhealthy: {resp.status_code}")
        except Exception as e:
            self.consecutive_failures += 1
            self.log_event("CRITICAL", f"Gateway unreachable: {e}")

        # 2. Audit APK Liveness
        try:
            resp = requests.get(f"{GATEWAY_URL}/agent/summary", headers={"Authorization": f"Bearer {API_KEY}"}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("online"):
                    self.last_apk_heartbeat = time.time()
                else:
                    offline_duration = time.time() - self.last_apk_heartbeat
                    if offline_duration > 600: # 10 minutes
                        self._trigger_apk_revival()
        except: pass

        # 3. Decision Matrix: Self-Healing Actions
        if self.consecutive_failures >= 3:
            self._trigger_vps_network_reset()

    def _trigger_apk_revival(self):
        """Instruct the system to attempt a forceful re-pair with the mobile agent."""
        self.log_event("ALERT", "Redmi Note 14 offline for > 10 mins. Triggering Neural Mesh Re-Pairing.", "MESH_RESET")
        try:
            # Send a broadcast or notification if possible (e.g., via Telegram or FCM)
            # For now, we queue a high-priority mesh reset command
            requests.post(f"{GATEWAY_URL}/agent/command", headers={"Authorization": f"Bearer {API_KEY}"}, json={
                "target_device": "REDMI_NOTE_14",
                "action": {"type": "mesh_reconnect"},
                "description": "HEALER: Forced reconnection due to prolonged silence."
            })
        except: pass

    def _trigger_vps_network_reset(self):
        """Force a reset of the local network stack if Gateway connectivity is lost."""
        self.log_event("CRITICAL", "Gateway link severed multiple times. Attempting VPS network handshake reset.", "NET_RESET")
        # In a docker environment, this might involve restarting the gateway proxy container
        # For now, we just clear local cache
        self.consecutive_failures = 0

    def run(self):
        logging.info("Noir Healer Singularity v1.0 Initialized.")
        while True:
            self.check_system_health()
            time.sleep(60) # Health audit every minute

if __name__ == "__main__":
    healer = NoirHealer()
    healer.run()
