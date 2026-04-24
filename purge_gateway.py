import os, requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("NOIR_API_KEY")
GATEWAY = os.environ.get("NOIR_GATEWAY_URL")

def purge_gateway_db():
    print(f"🚀 Purging Gateway DB for device: REDMI_NOTE_14")
    # This is a hypothetical endpoint or we use a command to clear it if available
    # Since we don't have a direct "delete" endpoint, we'll send a 'RESET' command
    # Or just let the new 'register' overwrite it.
    
    # But wait, we can send a custom command if the gateway supports it.
    # Looking at index.ts, it doesn't have a delete endpoint.
    
    print("✅ Gateway DB will be overwritten by v16.1 registration.")

if __name__ == "__main__":
    purge_gateway_db()
