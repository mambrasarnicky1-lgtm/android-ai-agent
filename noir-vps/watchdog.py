import os, subprocess, time, logging
from evolution_engine import evolution_engine

log = logging.getLogger("SovereignWatchdog")

class SovereignWatchdog:
    """
    Sistem Auto-Healing & Self-Diagnostics v1.0.
    Mendeteksi kegagalan layanan dan mengusulkan perbaikan otonom.
    """
    
    def __init__(self):
        self.check_interval = 300 # 5 menit

    def run_diagnostics(self):
        log.info("🔍 Running Sovereign System Diagnostics...")
        issues = []
        
        # 1. Check Docker Services
        try:
            r = subprocess.run(["docker-compose", "ps", "--format", "json"], capture_output=True, text=True)
            if r.returncode != 0:
                issues.append({"type": "DOCKER_DOWN", "detail": "Docker service not responding."})
        except: pass
        
        # 2. Check Key Ports (8000 for Brain, 8888 for UI)
        import socket
        for port in [8000, 8888]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0:
                    issues.append({"type": "PORT_CLOSED", "port": port})
        
        if issues:
            self.propose_healing(issues)
        else:
            log.info("✅ All systems operational.")

    def propose_healing(self, issues):
        """Menyusun proposal perbaikan berdasarkan isu yang ditemukan."""
        title = f"Auto-Healing: Resolve {len(issues)} System Issues"
        description = "Mendeteksi kegagalan layanan berikut dan mengusulkan pemulihan mandiri:\n"
        
        for issue in issues:
            description += f"- {issue['type']}: {issue.get('detail', issue.get('port'))}\n"
            
        # Tentukan tindakan perbaikan
        changes = {"actions": []}
        for issue in issues:
            if issue["type"] == "DOCKER_DOWN":
                changes["actions"].append("docker-compose up -d --build")
            if issue["type"] == "PORT_CLOSED" and issue["port"] == 8888:
                changes["actions"].append("python3 fix_vps_server.py")
        
        evolution_engine.propose_evolution(
            title=title,
            description=description,
            changes=changes,
            complexity=2
        )
        log.info(f"🚨 Auto-Healing Proposal created for {len(issues)} issues.")

if __name__ == "__main__":
    watchdog = SovereignWatchdog()
    watchdog.run_diagnostics()
