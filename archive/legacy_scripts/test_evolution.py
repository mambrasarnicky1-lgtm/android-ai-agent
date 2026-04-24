import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "noir-vps"))
from evolution_engine import evolution_engine

def main():
    print("🧪 Testing Sovereign Evolution Proposal...")
    
    # Simulate a proposal for a new 'HealthCheck' skill
    proposal_id = evolution_engine.propose_evolution(
        title="Auto-Diagnostics Skill v1.0",
        description="Menambahkan kemampuan diagnosa mandiri pada agen saat koneksi tidak stabil.",
        changes={
            "new_file": {
                "path": "noir-vps/self_diag.py",
                "content": "import socket\ndef check(): return socket.gethostname()"
            }
        },
        complexity=3
    )
    
    print(f"✅ Proposal Created! ID: {proposal_id}")
    print(f"Check 'knowledge/evolution/pending_proposals.json' to see it.")
    print(f"Run 'evolution_engine.approve_evolution(\"{proposal_id}\")' to apply it.")

if __name__ == "__main__":
    main()
