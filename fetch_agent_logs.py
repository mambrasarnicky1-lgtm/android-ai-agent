import requests, os, json
from dotenv import load_dotenv

load_dotenv(r"c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\.env")
gateway = os.environ.get("NOIR_GATEWAY_URL")
api_key = os.environ.get("NOIR_API_KEY")

r = requests.get(
    f"{gateway}/agent/logs", 
    params={"device_id": "REDMI_NOTE_14_ELITE_V16"}, 
    headers={"Authorization": f"Bearer {api_key}"}
)

with open(r"c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\agent_logs.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(r.json(), indent=2, ensure_ascii=False))
print("Logs saved to agent_logs.json")
