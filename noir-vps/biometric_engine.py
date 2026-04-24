import json
import time
import math
from typing import List, Dict

class BiometricSecurityEngine:
    """
    NEURAL MESH BIOMETRIC ANALYZER v18.0 [SENTINEL]
    Role: Detects unauthorized usage by analyzing behavioral interaction patterns.
    """
    
    def __init__(self):
        self.master_profile = None # The USER's golden pattern
        self.sensitivity = 0.85     # Threshold for 'Authorized' (0-1)
        
    def learn_master_profile(self, patterns: List[Dict]):
        """Learns the unique timing and spatial behavior of the Sovereign."""
        if not patterns: return
        
        avg_interval = sum(p['interval'] for p in patterns) / len(patterns)
        self.master_profile = {
            "avg_interval": avg_interval,
            "patterns": patterns,
            "learned_at": time.time()
        }
        print(f"[SENTINEL] Master Profile Learned. Base Latency: {avg_interval:.4f}s")

    def verify_interaction(self, current_patterns: List[Dict]) -> Dict:
        """Compares current behavior against the master profile."""
        if not self.master_profile:
            return {"authorized": True, "confidence": 1.0, "reason": "Learning Phase"}
            
        avg_curr = sum(p['interval'] for p in current_patterns) / len(current_patterns)
        diff = abs(avg_curr - self.master_profile['avg_interval'])
        
        # Calculate behavioral similarity score
        similarity = 1.0 - min(diff / self.master_profile['avg_interval'], 1.0)
        
        authorized = similarity >= self.sensitivity
        
        return {
            "authorized": authorized,
            "confidence": round(similarity, 4),
            "threat_level": "CRITICAL" if not authorized else "NONE",
            "action_taken": "FINANCIAL_BLACKOUT" if not authorized else "CONTINUE"
        }

if __name__ == "__main__":
    # --- SIMULATION ---
    engine = BiometricSecurityEngine()
    
    # 1. Simulate the REAL USER (Learning)
    real_user_data = [
        {"interval": 0.12, "pos": (100, 200)},
        {"interval": 0.15, "pos": (110, 210)},
        {"interval": 0.11, "pos": (95, 195)}
    ]
    engine.learn_master_profile(real_user_data)
    
    # 2. Simulate the REAL USER interacting (Verification)
    test_auth = engine.verify_interaction([
        {"interval": 0.13, "pos": (102, 202)},
        {"interval": 0.14, "pos": (108, 208)}
    ])
    print(f"\n[MATCH] Real User: {test_auth}")
    
    # 3. Simulate an INTRUDER (Verification)
    # Intruder has slower, more hesitant intervals (0.5s)
    test_threat = engine.verify_interaction([
        {"interval": 0.55, "pos": (500, 500)},
        {"interval": 0.48, "pos": (510, 510)}
    ])
    print(f"\n[THREAT] Intruder Detected: {test_threat}")
