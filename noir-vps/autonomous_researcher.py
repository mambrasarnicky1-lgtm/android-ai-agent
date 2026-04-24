#!/usr/bin/env python3
"""
NOIR SOVEREIGN v17.0 — AUTONOMOUS RESEARCHER
============================================
Otoritas Belajar Otonom: AI Agent menganalisis kode sendiri,
mencari dokumentasi terbaru, dan menyusun Proposal Evolusi.
Hanya memiliki izin BELAJAR, bukan EKSEKUSI (kecuali diizinkan USER).
"""

import os, json, logging, time, sys, requests
from pathlib import Path
from dotenv import load_dotenv

# Load env from root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RESEARCHER] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("NoirResearcher")

GATEWAY  = os.environ.get("NOIR_GATEWAY_URL", "").rstrip("/")
API_KEY  = os.environ.get("NOIR_API_KEY", "")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

class AutonomousResearcher:
    def __init__(self):
        self.knowledge_base = {}
        self.proposals = []

    def scan_project_for_weakness(self):
        """Menganalisis kode proyek sendiri untuk menemukan celah atau inefisiensi."""
        log.info("🔍 Scanning internal architecture for optimization...")
        weaknesses = []
        
        # Contoh scan file krusial
        target_files = [
            "../mobile_app/main.py",
            "../noir-vps/brain.py",
            "../noir-gateway/src/index.ts"
        ]
        
        for file_path in target_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    prompt = f"Analyze this code for performance bottlenecks, security risks, and technical debt. Focus on Android and Cloudflare best practices. Code:\n\n{content[:4000]}"
                    
                    analysis = self._query_ai(prompt)
                    weaknesses.append({"file": file_path, "analysis": analysis})
            except Exception as e:
                log.error(f"Failed to scan {file_path}: {e}")
        
        return weaknesses

    def search_tech_trends(self):
        """Mencari update terbaru tentang Android, Python, dan AI."""
        log.info("🌐 Researching latest tech documentation and trends...")
        # Simulasi riset otonom via AI (bisa dikembangkan dengan scraper nyata)
        prompt = "Riset update terbaru (April 2026) mengenai Android Accessibility Service, Kivy Android 13+ compatibility, dan Cloudflare Workers D1 optimization. Berikan ringkasan teknis."
        return self._query_ai(prompt)

    def _query_ai(self, prompt: str):
        if not GEMINI_KEY: return "Error: Gemini Key missing"
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            resp = requests.post(url, json={
                "contents": [{"parts": [{"text": prompt}]}]
            }, timeout=30)
            data = resp.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"AI Query Failed: {e}"

    def generate_evolution_proposal(self, weaknesses, trends):
        """Menyusun proposal upgrade berdasarkan hasil riset."""
        log.info("🧬 Synthesizing Evolution Proposal...")
        prompt = f"Berdasarkan kelemahan internal berikut: {weaknesses}\n\nDan tren teknologi terbaru: {trends}\n\nSusunlah satu Proposal Evolusi v17.1 yang mencakup perbaikan keamanan dan fitur baru. Format sebagai JSON."
        
        proposal_raw = self._query_ai(prompt)
        # Mencoba mengekstrak JSON dari response AI
        try:
            json_match = json.loads(proposal_raw[proposal_raw.find("{"):proposal_raw.rfind("}")+1])
            return json_match
        except:
            return {"title": "Evolution v17.1 Proposal", "summary": proposal_raw}

    def submit_to_gateway(self, proposal):
        """Kirim proposal ke Dashboard untuk persetujuan USER."""
        try:
            requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "action": {"type": "evolution_proposal", "proposal": proposal},
                "description": f"New Evolution Proposal: {proposal.get('title', 'v17.1')}"
            }, timeout=10)
            log.info("✅ Proposal submitted to Gateway.")
        except Exception as e:
            log.error(f"Failed to submit proposal: {e}")

    def poll_directives(self):
        """Mengecek apakah USER memberikan arahan pembelajaran khusus via Gateway."""
        try:
            r = requests.get(f"{GATEWAY}/agent/poll?device_id=RESEARCHER_CORE", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                commands = r.json().get("commands", [])
                for cmd in commands:
                    action = cmd.get("action", {})
                    if action.get("type") == "set_learning_target":
                        target = action.get("target", "General Tech")
                        log.info(f"🎯 NEW LEARNING DIRECTIVE: {target}")
                        self.current_target = target
                        # Report back
                        requests.post(f"{GATEWAY}/agent/command_result", headers=HEADERS, json={
                            "command_id": cmd.get("id"),
                            "result": json.dumps({"success": True, "message": f"Target set to: {target}"})
                        })
        except: pass

    def run_learning_cycle(self):
        # 🎯 HIGH-VALUE TARGETS (HVT) Defined by User
        self.hvt_list = [
            "Coding & Syntax Optimization (Python/Typescript/Kotlin)",
            "Advanced Problem Solving & Logical Reasoning Algorithms",
            "Cyber Security: Offensive & Defensive Persistence Techniques",
            "Human Communication: Slang, Typo-Resistance, and Contextual Nuance",
            "Meta-AI: Self-Architecture & Neural Network Optimization"
        ]
        self.hvt_index = 0
        
        from catalyst import SovereignCatalyst
        self.catalyst = SovereignCatalyst()

        while True:
            self.current_target = self.hvt_list[self.hvt_index % len(self.hvt_list)]
            log.info(f"--- 🌑 Starting HVT Cycle [Target: {self.current_target}] ---")
            
            # 1. Poll for New User Directives (Override if any)
            self.poll_directives()
            
            # 2. Intelligence Synthesis (Noir Catalyst)
            intelligence = self.catalyst.absorb_and_synthesize(self.current_target)
            
            # 3. Internal Scan
            weaknesses = self.scan_project_for_weakness()
            
            # 4. Final Evolution Proposal
            proposal = self.generate_evolution_proposal(weaknesses, f"HVT Intelligence Synthesized: {json.dumps(intelligence)}")
            
            # 5. Reporting
            self.submit_to_gateway(proposal)
            
            log.info(f"--- 💤 Cycle Complete. Readiness: {intelligence.get('readiness_score', 0)}% ---")
            
            # Move to next target for next hour
            self.hvt_index += 1
            time.sleep(3600) 

if __name__ == "__main__":
    researcher = AutonomousResearcher()
    researcher.run_learning_cycle()
