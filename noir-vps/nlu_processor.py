import os, json, logging, re
from ai_router import AIRouter

log = logging.getLogger("NLUProcessor")

class NLUProcessor:
    """Mesin Pemrosesan Bahasa Alami untuk menormalisasi dan mengekstrak intent."""
    
    @staticmethod
    def normalize_input(text: str) -> dict:
        """Menormalisasi input dengan pendekatan hybrid (Local Mapping + AI)."""
        raw_text = text.lower().strip()
        
        # 1. LOCAL FAST-MAPPING (Indonesian Context)
        local_mapping = {
            "ss": "TAKE_SCREENSHOT", "screenshot": "TAKE_SCREENSHOT", "foto": "TAKE_SCREENSHOT",
            "baterai": "GET_BATTERY", "batere": "GET_BATTERY", "battery": "GET_BATTERY",
            "info": "GET_STATUS", "status": "GET_STATUS", "noir": "GET_STATUS",
            "matiin": "SYSTEM_ACTION", "nyalain": "SYSTEM_ACTION", "hidupkan": "SYSTEM_ACTION",
            "wifi": "WIFI_TOGGLE", "data": "DATA_TOGGLE", "bluetooth": "BT_TOGGLE"
        }
        
        for key, intent in local_mapping.items():
            if key in raw_text:
                log.info(f"⚡ NLU: Local Match Found -> {intent}")
                return {
                    "original": text,
                    "normalized": raw_text,
                    "intent": intent,
                    "entities": {},
                    "slang_detected": True
                }

        # 2. AI DEEP NORMALIZATION (DISABLED in v16 Stabilization)
        log.info(f"🚫 NLU: AI Normalization Disabled to save tokens -> {text}")
        return {"original": text, "normalized": text, "intent": "UNKNOWN", "entities": {}, "slang_detected": False}

    @staticmethod
    def extract_pattern(normalized_text: str):
        """Mengekstrak pola struktur kalimat untuk pembelajaran otonom."""
        # Contoh: "Tolong nyalakan lampu" -> "ACTION_REQUEST(verb=nyalakan, target=lampu)"
        prompt = f"Analyze the grammatical structure of this normalized sentence and return a pattern template: '{normalized_text}'"
        pattern = AIRouter.query_gemini(prompt)
        return pattern
