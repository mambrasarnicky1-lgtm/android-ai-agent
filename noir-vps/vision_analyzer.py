import os, json, logging
import base64
from ai_router import AIRouter
from catalyst import catalyst
from datetime import datetime

log = logging.getLogger("VisionAnalyzer")

class ScreenVisionIntelligence:
    """Modul AI baru untuk menganalisis konteks layar secara visual."""
    
    @staticmethod
    def analyze_screen(image_path: str):
        log.info("👁️ Vision Intelligence: Analyzing current screen state...")
        
        if not os.path.exists(image_path):
            return {"error": "Screen image not found."}
            
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
            prompt = """
            Analyze this Android screenshot. Identify:
            1. What app is currently open?
            2. Are there any sensitive elements (passwords, banking interfaces)?
            3. What is the overall context of the screen?
            
            Return ONLY a valid JSON:
            {
                "app_detected": "App Name",
                "is_sensitive": true/false,
                "context": "Short description of what is happening"
            }
            """
            
            # Memanfaatkan kemampuan multimodal & native JSON Gemini 2.0 Flash
            response = AIRouter.query_gemini(prompt, image_base64=encoded_string, response_json=True)
            result = json.loads(response)
            
            # 4. Integrate into Catalyst Knowledge
            catalyst.absorb_skill("Vision_Screen_Analysis", {"app": result.get("app_detected"), "complexity": 3})
            
            # --- NEW: Temporal Memory Storage ---
            ScreenVisionIntelligence.save_to_memory(result)
            
            return result
        except Exception as e:
            log.error(f"Vision Analysis Failed: {e}")
            return {"error": str(e)}

    @staticmethod
    def save_to_memory(analysis: dict):
        """Menyimpan ringkasan layar ke memori temporal."""
        memory_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "temporal_memory.json")
        try:
            memory_data = {"memory": []}
            if os.path.exists(memory_path):
                with open(memory_path, "r") as f:
                    memory_data = json.load(f)
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "app": analysis.get("app_detected"),
                "context": analysis.get("context"),
                "sensitive": analysis.get("is_sensitive", False)
            }
            
            memory_data["memory"].append(entry)
            memory_data["memory"] = memory_data["memory"][-100:]
            memory_data["last_update"] = datetime.now().isoformat()
            
            with open(memory_path, "w") as f:
                json.dump(memory_data, f, indent=4)
        except Exception as e:
            log.error(f"Failed to save to temporal memory: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = ScreenVisionIntelligence.analyze_screen(sys.argv[1])
        print(json.dumps(res, indent=2))
