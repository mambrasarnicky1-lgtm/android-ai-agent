import os, json, logging, uuid
from datetime import datetime

log = logging.getLogger("EvolutionEngine")

class SovereignEvolutionEngine:
    """
    Sistem Pengembangan Diri Otonom v1.0
    Mengelola siklus evolusi kode dan skill secara otonom dengan kontrol mutlak User.
    """
    
    EVO_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "evolution")
    PENDING_FILE = os.path.join(EVO_DIR, "pending_proposals.json")
    HISTORY_FILE = os.path.join(EVO_DIR, "evolution_history.json")

    def __init__(self):
        os.makedirs(self.EVO_DIR, exist_ok=True)
        self.pending = self.load_data(self.PENDING_FILE, [])
        self.history = self.load_data(self.HISTORY_FILE, [])

    def load_data(self, path, default):
        if os.path.exists(path):
            with open(path, 'r') as f: return json.load(f)
        return default

    def save_data(self, path, data):
        with open(path, 'w') as f: json.dump(data, f, indent=4)

    def propose_evolution(self, title, description, changes, complexity=5):
        """Mendaftarkan proposal evolusi baru untuk persetujuan User."""
        proposal = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "description": description,
            "changes": changes, # Bisa berupa diff, path file baru, atau config
            "complexity": complexity,
            "status": "PENDING_APPROVAL"
        }
        
        self.pending.append(proposal)
        self.save_data(self.PENDING_FILE, self.pending)
        log.info(f"✨ New Evolution Proposal registered: {title} ({proposal['id']})")
        return proposal["id"]

    def approve_evolution(self, proposal_id):
        """Menerapkan evolusi setelah mendapat izin mutlak dari User."""
        for i, prop in enumerate(self.pending):
            if prop["id"] == proposal_id:
                log.info(f"🚀 USER APPROVED EVOLUTION: {prop['title']}")
                
                # EXECUTION LOGIC (Placeholder for real code injection/hot-swap)
                success = self._execute_modification(prop)
                
                if success:
                    prop["status"] = "APPLIED"
                    prop["applied_at"] = datetime.now().isoformat()
                    self.history.append(prop)
                    self.pending.pop(i)
                    self.save_data(self.PENDING_FILE, self.pending)
                    self.save_data(self.HISTORY_FILE, self.history)
                    return True
        return False

    def _execute_modification(self, proposal):
        """Logika teknis untuk menerapkan perubahan (Hot-fix, New File, etc)."""
        try:
            # AUTHORITY SHIELD (v19.5): Lindungi kewenangan mutlak User
            if "new_file" in proposal["changes"]:
                path = proposal["changes"]["new_file"]["path"]
                content = proposal["changes"]["new_file"]["content"]
                
                # Cek jika file tujuan mengandung blok otoritas mutlak
                if os.path.exists(path):
                    with open(path, 'r') as f: current = f.read()
                    if "PROTECTED_AUTHORITY_BLOCK" in current:
                        # Jika konten baru tidak menyertakan blok pelindung, batalkan!
                        if "PROTECTED_AUTHORITY_BLOCK" not in content:
                            log.critical(f"⚠️ PERCOBAAN PELANGGARAN OTORITAS: AI mencoba menghapus Kill-Switch di {path}. DIBLOKIR!")
                            return False
                
                with open(path, "w") as f: f.write(content)
                log.info(f"✅ Created/Updated evolution file: {path}")
            
            return True
        except Exception as e:
            log.error(f"Evolution execution failed: {e}")
            return False

evolution_engine = SovereignEvolutionEngine()
