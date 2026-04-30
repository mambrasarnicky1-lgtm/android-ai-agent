import requests

with open("test2.txt", "w") as f:
    f.write("hello from multipart with data")

r = requests.post("http://8.215.23.17:80/agent/upload?device_id=TEST", files={"file": ("test2.txt", open("test2.txt", "rb"), "text/plain")}, data={"device_id": "TEST_DATA"})
print(r.status_code)
print(r.text)
