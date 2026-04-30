import paramiko
import time

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('8.215.23.17', username='root', password='N!colay_No1r.Ai@Agent#Secure')

def run(cmd, desc=None, timeout=30):
    if desc: print(f"\n[*] {desc}")
    i, o, e = s.exec_command(cmd)
    o.channel.settimeout(timeout)
    out = o.read().decode().strip()
    err = e.read().decode().strip()
    if out: print(out)
    if err and 'warning' not in err.lower(): print(f"  ERR: {err[:300]}")
    return out

print("="*60)
print("NOIR v21.0.4 — DOCKER RUN DEPLOY (bypass docker-compose bug)")
print("="*60)

# 1. Get the image name used previously
run("docker images | grep noir", "Available images:")

# 2. Inspect old container to get its image
run("docker inspect noir-dashboard --format '{{.Config.Image}}' 2>/dev/null || echo 'no old container'",
    "Getting old image name...")

# 3. Get all image IDs
imgs = run("docker images --format '{{.Repository}}:{{.Tag}}\t{{.ID}}' | grep -v none", "All images:")

# 4. Find the correct image
run("docker images --format '{{.Repository}}:{{.Tag}}' | grep noir", "Noir images:")

# 5. Run dashboard with direct docker run using same image as noir-brain
img_out = run("docker inspect noir-brain --format '{{.Config.Image}}'", "Getting noir-brain image:")
image = img_out.strip() if img_out.strip() else "noir-agent-base:latest"
print(f"\n[*] Using image: {image}")

# 6. Start dashboard container
run(f"""docker run -d \
  --name noir-dashboard \
  --restart always \
  -p 80:80 \
  -v /root/noir-agent:/app \
  -w /app/noir-ui \
  --env-file /root/noir-agent/.env \
  {image} \
  gunicorn --bind 0.0.0.0:80 --workers 2 -k uvicorn.workers.UvicornWorker web_server:app 2>&1""",
    "Starting noir-dashboard container...")

time.sleep(6)

# 7. Status check
run("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'",
    "Container status:")

# 8. Check logs
run("docker logs noir-dashboard --tail=40 2>&1",
    "Dashboard logs (last 40 lines):")

# 9. Health check
run("curl -s -o /dev/null -w '%{http_code}' http://localhost:80/health",
    "Health check port 80:")

run("curl -s http://localhost:80/health", "Health response:")

s.close()
print("\n[DONE]")
