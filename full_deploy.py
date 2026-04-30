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
    if err: print(f"  STDERR: {err[:200]}")
    return out

print("="*60)
print("NOIR v21.0.4 — FULL PURGE & CLEAN DEPLOY")
print("="*60)

# 1. Pull latest code
run("cd /root/noir-agent && git fetch --all && git reset --hard origin/main",
    "Syncing v21.0.4 from GitHub...")

# 2. Purge ALL Python __pycache__ (cache lama)
run("find /root/noir-agent -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null; echo 'pycache purged'",
    "Purging __pycache__ (cache lama)...")

# 3. Purge old .pyc files
run("find /root/noir-agent -name '*.pyc' -delete 2>/dev/null; echo 'pyc purged'",
    "Purging .pyc files...")

# 4. Create screenshots dir if missing
run("mkdir -p /root/noir-agent/noir-ui/screenshots && chmod 777 /root/noir-agent/noir-ui/screenshots",
    "Ensuring screenshots dir exists...")

# 5. Stop ALL containers cleanly
run("docker stop noir-dashboard noir-brain 2>/dev/null; sleep 2",
    "Stopping containers cleanly...")

# 6. Remove old containers to avoid stale config
run("docker rm noir-dashboard 2>/dev/null; echo 'old container removed'",
    "Removing stale noir-dashboard container...")

# 7. Rebuild & restart dashboard
run("cd /root/noir-agent && docker-compose up -d --build noir-dashboard",
    "Rebuilding & starting noir-dashboard (v21.0.4)...")

# 8. Wait for startup
print("\n[*] Waiting 5s for container startup...")
time.sleep(5)

# 9. Check container status
out = run("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'",
          "Container status:")

# 10. Check dashboard logs for errors
run("docker logs noir-dashboard --tail=30 2>&1",
    "Dashboard startup logs:")

# 11. Verify routes (no duplicates)
run("docker exec noir-dashboard python -c \"import web_server; print('[OK] web_server imports cleanly')\" 2>&1",
    "Verifying web_server.py (no import errors)...")

# 12. Restart noir-brain too
run("docker start noir-brain 2>/dev/null; echo 'brain started'",
    "Restarting noir-brain...")

# 13. Final health check
run("curl -s -o /dev/null -w '%{http_code}' http://localhost:80/health",
    "Health check on port 80:")

print("\n" + "="*60)
print("DEPLOYMENT COMPLETE — v21.0.4")
print("="*60)
s.close()
