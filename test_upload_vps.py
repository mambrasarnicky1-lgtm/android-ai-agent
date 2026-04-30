import paramiko

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('8.215.23.17', username='root', password='N!colay_No1r.Ai@Agent#Secure')

test_script = """
import requests
with open("test.txt", "w") as f:
    f.write("hello from python test")

r = requests.post("http://localhost:80/agent/upload?device_id=TEST", files={"file": ("test.txt", open("test.txt", "rb"))})
print("STATUS", r.status_code)
print("TEXT", r.text)
"""

# Write script to VPS and run it
i,o,e = s.exec_command(f'cat << "EOF" > test.py\n{test_script}\nEOF\npython3 test.py')
print(o.read().decode())
print(e.read().decode())
s.close()
