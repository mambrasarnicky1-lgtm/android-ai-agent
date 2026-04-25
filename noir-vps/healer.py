#!/usr/bin/env python3
"""
NOIR SOVEREIGN HEALER (v17.2 APEX)
==================================
Autonomous Self-Repair: Memantau log sistem secara real-time,
mendiagnosis error via AI, dan menyusun patch otomatis.
"""

import os, json, logging, time, requests, subprocess, sys

# v17.2: Unified Path Normalization
sys.path.append(os.path.join(os.path.dirname(__file__)))

from ai_router import AIRouter

log = logging.getLogger("SovereignHealer")

class SovereignHealer:
    def __init__(self):
        self.log_path = "/root/noir-agent/logs/brain.log"
        self.gateway = os.environ.get("NOIR_GATEWAY_URL")
        self.api_key = os.environ.get("NOIR_API_KEY")

    def scan_for_errors(self):
        """Memindai log untuk mencari Traceback atau Fatal Error."""
        if not os.path.exists(self.log_path): return None
        
        try:
            with open(self.log_path, "r") as f:
                lines = f.readlines()
                # Ambil 50 baris terakhir
                recent = "".join(lines[-50:])
                if "Traceback" in recent or "Error" in recent:
                    log.warning("⚠️ Critical Error detected in Brain logs!")
                    return recent
        except: pass
        return None

    def diagnose_and_propose_fix(self, error_context):
        """Mengirim error ke Catalyst/Gemini untuk mendapatkan solusi."""
        prompt = f"""
        DIAGNOSTIC REQUEST: Critical Error in Noir Sovereign Brain.
        Context: {error_context}
        
        Analyze the traceback and provide a surgical fix. 
        Format as JSON: {{"diagnosis": "...", "fix_code": "...", "risk_level": "low/high"}}
        """
        
        fix_proposal = AIRouter.query_gemini(prompt)
        try:
            proposal_json = json.loads(fix_proposal[fix_proposal.find("{"):fix_proposal.rfind("}")+1])
            self._submit_proposal(proposal_json)
        except:
            log.error("Failed to parse AI Fix Proposal.")

    def _submit_proposal(self, proposal):
        """Kirim proposal perbaikan ke Dashboard (One-Click Heal)."""
        requests.post(f"{self.gateway}/agent/command", headers={"Authorization": f"Bearer {self.api_key}"}, json={
            "action": {"type": "self_heal_proposal", "proposal": proposal},
            "description": f"🔴 SELF-HEAL: {proposal.get('diagnosis')[:50]}"
        })

    def run_watchdog(self):
        log.info("🛡️ Sovereign Healer Watchdog Active.")
        while True:
            err = self.scan_for_errors()
            if err:
                self.diagnose_and_propose_fix(err)
            time.sleep(300) # Scan every 5 mins

if __name__ == "__main__":
    healer = SovereignHealer()
    healer.run_watchdog()
