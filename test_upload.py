import requests

with open("test.txt", "w") as f:
    f.write("hello world")

r = requests.post("http://127.0.0.1/agent/upload?device_id=TEST", files={"file": ("test.txt", open("test.txt", "rb"), "text/plain")})
print(r.status_code)
print(r.text)
