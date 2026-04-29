import requests
import json

url = "http://8.215.23.17:80/api/summary"
headers = {"Authorization": "Bearer NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"}

print("--- VPS API DIAGNOSIS ---")
try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")

url_health = "http://8.215.23.17:80/health"
try:
    r = requests.get(url_health, timeout=5)
    print(f"\nHealth: {r.json()}")
except Exception as e:
    print(f"Health Error: {e}")
