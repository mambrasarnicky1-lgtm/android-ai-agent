import paramiko
import os

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('8.215.23.17', username='root', password='N!colay_No1r.Ai@Agent#Secure')

print("="*60)
print("NOIR SOVEREIGN VPS — DEPLOYMENT VERIFICATION v21.0.3")
print("="*60)

# 1. Git status
print("\n[1] GIT STATUS:")
i,o,e = s.exec_command('cd /root/noir-agent && git log --oneline -5')
print(o.read().decode())

# 2. Container status
print("\n[2] DOCKER CONTAINERS:")
i,o,e = s.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
print(o.read().decode())

# 3. Duplicate/conflicting route check
print("\n[3] DUPLICATE API ROUTES (potential conflicts):")
i,o,e = s.exec_command('cd /root/noir-agent && grep -n "@app" noir-ui/web_server.py | sort')
print(o.read().decode())

# 4. Old pycache check
print("\n[4] PYCACHE (cache lama):")
i,o,e = s.exec_command('find /root/noir-agent -name "__pycache__" -type d 2>/dev/null')
print(o.read().decode() or "None found")

# 5. Screenshots dir
print("\n[5] SCREENSHOTS DIR (media storage):")
i,o,e = s.exec_command('ls -lh /root/noir-agent/noir-ui/screenshots/ 2>/dev/null | tail -10')
print(o.read().decode() or "Empty or not found")

# 6. Gunicorn workers
print("\n[6] GUNICORN/UVICORN CONFIG:")
i,o,e = s.exec_command('docker inspect noir-dashboard --format "{{.Config.Cmd}}" 2>/dev/null')
print(o.read().decode())

# 7. Port conflicts
print("\n[7] PORT STATUS:")
i,o,e = s.exec_command('ss -tlnp | grep -E ":80|:8000|:5000"')
print(o.read().decode())

# 8. .env file loaded
print("\n[8] ENV KEYS LOADED:")
i,o,e = s.exec_command('cd /root/noir-agent && grep -v "^#" .env | grep -v "^$" | cut -d= -f1')
print(o.read().decode())

# 9. Check for old duplicate assets endpoints
print("\n[9] DUPLICATE ENDPOINTS CHECK:")
i,o,e = s.exec_command('cd /root/noir-agent && grep -n "api/asset" noir-ui/web_server.py')
print(o.read().decode())

s.close()
print("\n[AUDIT COMPLETE]")
