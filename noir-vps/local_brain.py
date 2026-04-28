import os, logging, torch
from transformers import pipeline

log = logging.getLogger("LocalBrain")

class LocalAI:
    """Local LLM Fallback (v18.4 Phase 5)."""
    _pipe = None
    _model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

    @classmethod
    def _init_model(cls):
        if cls._pipe is None:
            log.info(f"Loading Local LLM: {cls._model_id}...")
            try:
                cls._pipe = pipeline(
                    "text-generation", 
                    model=cls._model_id, 
                    torch_dtype=torch.float32, 
                    device_map="auto"
                )
            except Exception as e:
                log.error(f"Local AI Load Error: {e}")

    @classmethod
    def query(cls, prompt: str, max_new_tokens: int = 150):
        cls._init_model()
        if not cls._pipe: return "[Local AI unavailable]"
        
        # Simple Chat Format
        formatted_prompt = f"<|system|>\nYou are Noir Sovereign, a helpful AI agent.</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
        
        outputs = cls._pipe(
            formatted_prompt, 
            max_new_tokens=max_new_tokens, 
            do_sample=True, 
            temperature=0.7, 
            top_k=50, 
            top_p=0.95
        )
        return outputs[0]["generated_text"].split("<|assistant|>\n")[-1].strip()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing Local AI...")
    print(LocalAI.query("Hello, who are you?"))
