import os, json, logging, time, requests, base64

log = logging.getLogger("AIRouter")

# Path to API Pool
POOL_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "api_pool.json")

def get_key_from_pool(provider: str) -> str:
    """Mengambil kunci aktif dari kolam atau fallback ke ENV."""
    try:
        if os.path.exists(POOL_PATH):
            with open(POOL_PATH, "r") as f:
                pool = json.load(f)
            keys = pool.get(provider, {}).get("keys", [])
            idx = pool.get(provider, {}).get("active_index", 0)
            if keys:
                return keys[idx % len(keys)]
    except: pass
    
    # Fallback to ENV
    mapping = {
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY"
    }
    return os.environ.get(mapping.get(provider, ""), "")

def rotate_key(provider: str):
    """Memutar ke kunci berikutnya jika kuota habis."""
    try:
        if os.path.exists(POOL_PATH):
            with open(POOL_PATH, "r") as f:
                pool = json.load(f)
            
            keys = pool.get(provider, {}).get("keys", [])
            if len(keys) > 1:
                pool[provider]["active_index"] = (pool[provider]["active_index"] + 1) % len(keys)
                with open(POOL_PATH, "w") as f:
                    json.dump(pool, f, indent=4)
                log.info(f"🔄 Rotated {provider} key to index {pool[provider]['active_index']}")
                return True
    except: pass
    return False

# Fetch environment variables for metadata
GATEWAY = os.environ.get("NOIR_GATEWAY_URL")
DEVICE_ID = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")
API_KEY = os.environ.get("NOIR_API_KEY")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

EXPERT_SYSTEM_PROMPT = """
You are the NOIR SOVEREIGN BRAIN v16.0 ELITE.
CORE DOMAINS:
- [DevOps]: Expert Python/Bash syntax. v16.0 Elite codebase awareness.
- [CyberSec]: Secure E2EE AES-256-GCM communications.
- [Linguistics]: Indonesian Slang & Phatic Mastery.
- [Remote Control]: Master of HyperOS Shell.
MISSION: Absolute, context-aware control over Redmi Note 14 ELITE.
"""

class RateLimiter:
    _requests = []
    _limit_per_hour = 100 # Increased for Elite
    @classmethod
    def check(cls):
        now = time.time()
        cls._requests = [r for r in cls._requests if now - r < 3600]
        if len(cls._requests) >= cls._limit_per_hour: return False
        cls._requests.append(now)
        return True

class AIRouter:
    """Routes queries to the best available free AI model with Auto-Rotation."""

    @staticmethod
    def query_gemini(prompt: str, image_base64: str = None, response_json: bool = False, retry=True) -> str:
        if not RateLimiter.check(): return "[Rate Limit] Wait..."
        
        current_key = get_key_from_pool("gemini")
        models = ["gemini-2.0-flash", "gemini-1.5-flash"]
        
        for model_name in models:
            try:
                parts = [{"text": prompt}]
                if image_base64:
                    parts.append({"inline_data": {"mime_type": "image/png", "data": image_base64}})
                
                payload = {
                    "system_instruction": {"parts": [{"text": EXPERT_SYSTEM_PROMPT}]},
                    "contents": [{"role": "user", "parts": parts}]
                }
                if response_json:
                    payload["generationConfig"] = {"responseMimeType": "application/json"}
                
                api_ver = "v1beta" if "2.0" in model_name else "v1"
                url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{model_name}:generateContent?key={current_key}"
                
                r = requests.post(url, json=payload, timeout=30)
                data = r.json()
                
                if "error" in data:
                    if data["error"]["code"] == 429 and retry:
                        log.warning(f"⚠️ Quota exceeded for key index. Rotating...")
                        if rotate_key("gemini"):
                            return AIRouter.query_gemini(prompt, image_base64, response_json, retry=False)
                    return f"[Gemini Error] {data['error']['message']}"
                
                if "candidates" in data:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                log.error(f"Gemini failed: {e}")
                
        return "🚨 [CRITICAL] All Gemini models or keys failed."

    @staticmethod
    def query_deepseek(prompt: str) -> str:
        key = get_key_from_pool("groq")
        if not key: return AIRouter.query_gemini(prompt)
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-r1-distill-llama-70b",
                    "messages": [{"role": "system", "content": EXPERT_SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                },
                timeout=40
            )
            data = r.json()
            if "error" in data and data["error"]["code"] == 429:
                rotate_key("groq")
            return data["choices"][0]["message"]["content"]
        except: return AIRouter.query_gemini(prompt)

    @staticmethod
    def query_qwen(prompt: str) -> str:
        key = get_key_from_pool("openrouter")
        if not key: return AIRouter.query_gemini(prompt)
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": "qwen/qwen-2-72b-instruct",
                    "messages": [{"role": "system", "content": EXPERT_SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                },
                timeout=30
            )
            return r.json()["choices"][0]["message"]["content"]
        except: return AIRouter.query_gemini(prompt)

    @staticmethod
    def smart_query(prompt: str) -> str:
        p_lower = prompt.lower()
        
        # Phase 3: Check local Neural Knowledge Base first
        try:
            from knowledge_base import NeuralKnowledgeBase
            local_context = NeuralKnowledgeBase.query(prompt)
            if local_context:
                prompt = f"LOCAL CONTEXT:\n{local_context}\n\nUSER QUESTION: {prompt}"
                log.info("🧠 SmartQuery: Injected local RAG context.")
        except: pass

        if any(x in p_lower for x in ["code", "python", "script"]): return AIRouter.query_qwen(prompt)
        if any(x in p_lower for x in ["mengapa", "analisis", "why"]): return AIRouter.query_deepseek(prompt)
        return AIRouter.query_gemini(prompt)

    @staticmethod
    def send_telegram(msg: str, important: bool = False):
        if not important: return
        if not TG_TOKEN or not TG_ID: return
        try:
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={
                "chat_id": TG_ID, "text": f"🧠 [NOIR BRAIN]\n{msg}"
            }, timeout=10)
        except: pass

    @staticmethod
    def web_search(query: str) -> str:
        """Pencarian web real-time menggunakan DuckDuckGo Lite."""
        log.info(f"🌐 Searching Web: {query}")
        try:
            # Menggunakan DuckDuckGo HTML untuk menghindari limitasi API berbayar
            url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                # Simple extraction of snippets (Noir Brain will clean this up further)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(r.text, "html.parser")
                results = []
                for result in soup.find_all("a", class_="result__snippet")[:5]:
                    results.append(result.get_text())
                return "\n".join(results) if results else "No snippets found."
            return f"Search failed with status {r.status_code}"
        except Exception as e:
            log.error(f"Web Search Error: {e}")
            return f"Search Error: {e}"

class ResearchEngine:
    @staticmethod
    def browser_learn(topic: str):
        log.info(f"🌐 Browser Learning: {topic}")
        return f"Consolidated research for {topic}"

class SemanticValidator:
    @staticmethod
    def validate_intent(action_type: str, params: dict):
        dangerous = str(params).lower()
        if "rm -rf" in dangerous: return False, "Dangerous command"
        return True, "OK"
