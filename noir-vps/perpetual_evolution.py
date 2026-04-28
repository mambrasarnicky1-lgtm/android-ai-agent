import time, logging, os
from evolution_engine import evolution_engine
from researcher import researcher

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("PerpetualEvolution")

def start_perpetual_mode():
    log.info("🌑 NOIR SOVEREIGN: ENTERING PERPETUAL EVOLUTION MODE...")
    log.info("Status: TRANSITIONING TO FULL AUTONOMY.")
    
    while True:
        try:
            # 1. Start Daily Research
            log.info("🧬 Cycle Start: Initiating Autonomous Research...")
            researcher.run_mission("Advanced Neural Mesh & System Hardening 2026")
            
            # 2. Check for possible code improvements
            log.info("🧩 Analyzing research results for potential patches...")
            # Logic inside researcher/evolution_engine will handle proposal generation
            
            # 3. Wait for 24 hours for the next cycle
            log.info("💤 Cycle Complete. Sleeping for 24 hours. Noir is evolving in silence.")
            time.sleep(86400) 
            
        except Exception as e:
            log.error(f"Perpetual Loop Error: {e}")
            time.sleep(3600) # Wait 1 hour before retry on error

if __name__ == "__main__":
    start_perpetual_mode()
