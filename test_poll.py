import paramiko
import json

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('8.215.23.17', username='root', password='N!colay_No1r.Ai@Agent#Secure')

cmd = """curl -s -X POST -H "Authorization: Bearer NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026" -H "Content-Type: application/json" -d '{"stats": {"cpu": 10, "ram": 50}}' 'http://localhost:80/agent/poll?device_id=REDMI_NOTE_14&client_type=main'"""
i, o, e = s.exec_command(cmd)
print(o.read().decode())
print(e.read().decode())

cmd2 = """curl -s -X GET 'http://localhost:80/api/status'"""
i, o, e = s.exec_command(cmd2)
print("STATUS:", o.read().decode())

s.close()
