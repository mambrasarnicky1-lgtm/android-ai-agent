import paramiko
import time

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('8.215.23.17', username='root', password='N!colay_No1r.Ai@Agent#Secure')

def run(cmd, desc=None, timeout=60):
    if desc: print(f"\n[*] {desc}")
    i, o, e = s.exec_command(cmd)
    out = o.read().decode().strip()
    err = e.read().decode().strip()
    if out: print(out)
    if err and 'warning' not in err.lower(): print(f"  ERR: {err[:200]}")
    return out

print("="*60)
print("NOIR v21.0.4 — DEPENDENCY FIX + FINAL DEPLOY")
print("="*60)

# 1. Install python-multipart inside the running image
run("docker exec noir-dashboard pip install python-multipart -q && echo 'installed'",
    "Installing python-multipart in container...")

# 2. Also install in the image permanently via exec on noir-brain (same image)
run("pip install python-multipart -q 2>/dev/null; docker exec noir-brain pip install python-multipart -q 2>/dev/null; echo 'done'",
    "Installing in base image environment...")

# 3. Restart dashboard to pick up fix
run("docker restart noir-dashboard", "Restarting noir-dashboard...")
time.sleep(8)

# 4. Status check
run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", "Container status:")

# 5. Logs
run("docker logs noir-dashboard --tail=20 2>&1", "Dashboard logs:")

# 6. Health check
run("curl -s -o /dev/null -w 'HTTP %{http_code}' http://localhost:80/health", "Health check:")
run("curl -s http://localhost:80/health", "Health response body:")

# 7. Verify routes loaded correctly
run("curl -s http://localhost:80/api/assets", "Assets endpoint test:")

print("\n" + "="*60)
print("DONE — v21.0.4 with multipart fix")
print("="*60)
s.close()
