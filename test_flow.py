import requests
import time

URL = "http://8.215.23.17:80"
HEADERS = {"Authorization": "Bearer NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026", "Content-Type": "application/json"}

print("1. Dashboard queues command...")
r = requests.post(f"{URL}/api/command", json={"action": {"type": "location"}, "target_device": "REDMI_NOTE_14"})
cid = r.json().get("command_id")
print("Queued:", cid)

print("\n2. Agent polls for commands...")
r = requests.post(f"{URL}/agent/poll?device_id=REDMI_NOTE_14&client_type=main", headers=HEADERS, json={"stats": {}})
cmds = r.json().get("commands", [])
print("Agent got:", cmds)

print("\n3. Agent submits result...")
r = requests.post(f"{URL}/agent/result", headers=HEADERS, json={
    "command_id": cid, "device_id": "REDMI_NOTE_14", "success": True, "output": "GPS OK", "data": {"lat": 1.23, "lon": 4.56, "accuracy": 10}
})
print("Result submit:", r.status_code, r.text)

print("\n4. Dashboard fetches result...")
r = requests.get(f"{URL}/api/command/result/{cid}")
print("Final state:", r.text)
