import paramiko
import time

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('8.215.23.17', username='root', password='N!colay_No1r.Ai@Agent#Secure')

def run(cmd, desc=None):
    if desc: print(f"\n[*] {desc}")
    i, o, e = s.exec_command(cmd)
    out = o.read().decode().strip()
    err = e.read().decode().strip()
    if out: print(out)
    if err and 'warning' not in err.lower(): print(f"  ERR: {err[:200]}")
    return out

print("="*60)
print("NOIR v21.0.4 — FINAL SYNC + CLEAN RESTART")
print("="*60)

# 1. Pull latest fix (no python-multipart)
run("cd /root/noir-agent && git fetch --all && git reset --hard origin/main", 
    "Pulling v21.0.4 (no python-multipart)...")

# 2. Purge pycache
run("find /root/noir-agent -name '__pycache__' -exec rm -rf {} + 2>/dev/null; echo 'cache purged'",
    "Purging pycache...")

# 3. Stop & remove old container
run("docker stop noir-dashboard 2>/dev/null; docker rm noir-dashboard 2>/dev/null; echo 'old container removed'",
    "Removing old container...")

# 4. Ensure screenshots dir exists
run("mkdir -p /root/noir-agent/noir-ui/screenshots && chmod 777 /root/noir-agent/noir-ui/screenshots",
    "Creating screenshots dir...")

# 5. Start fresh
run("""docker run -d \
  --name noir-dashboard \
  --restart unless-stopped \
  -p 80:80 \
  -v /root/noir-agent:/app \
  -w /app/noir-ui \
  --env-file /root/noir-agent/.env \
  noir-agent-base:latest \
  gunicorn --bind 0.0.0.0:80 --workers 1 -k uvicorn.workers.UvicornWorker --timeout 120 web_server:app""",
    "Starting noir-dashboard fresh...")

time.sleep(8)

# 6. Check status
run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", "Status:")

# 7. Logs
run("docker logs noir-dashboard --tail=25 2>&1", "Startup logs:")

# 8. Health
hc = run("curl -s -o /dev/null -w '%{http_code}' http://localhost:80/health", "HTTP Health check:")
print(f"\n>>> Dashboard health: HTTP {hc}")
if hc == "200":
    print(">>> [OK] DASHBOARD RUNNING PERFECTLY")
else:
    print(">>> [WARN] Not yet healthy — checking again...")
    time.sleep(5)
    hc2 = run("curl -s http://localhost:80/health")
    print(hc2)

s.close()
print("\n" + "="*60)
print("DEPLOYMENT v21.0.4 COMPLETE")
print("="*60)
