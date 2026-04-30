import requests

URL = "http://8.215.23.17"
print(requests.post(f"{URL}/api/command", json={"action": {"type": "location"}, "target_device": "REDMI_NOTE_14"}).text)
print(requests.get(f"{URL}/api/status").text)
