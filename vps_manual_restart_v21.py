import paramiko

host = '8.215.23.17'
port = 22
username = 'root'
password = 'N!colay_No1r.Ai@Agent#Secure'

def run_remote(cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, timeout=60)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        ssh.close()
        return out if out else err
    except Exception as e:
        return f"SSH Error: {e}"

print("=== MANUAL RESTART OF V21.0 SERVICES ===")

# 1. Force kill and restart services that need update
services = ["noir-brain", "noir-dashboard", "noir-healer", "noir-researcher", "noir-telegram"]
for svc in services:
    print(f"Restarting {svc}...")
    run_remote(f"docker restart {svc}")

# 2. Verify Healer is running self_healer.py
# Since we updated the code via git, restarting the container should pick up the new file
# BUT if the 'command' in docker-compose changed, restart won't pick that up.
# We need to manually run the new command for the healer.
print("Re-creating noir-healer with new entry point...")
run_remote("docker stop noir-healer; docker rm noir-healer")
healer_cmd = (
    "docker run -d --name noir-healer --restart always "
    "--network noir-net "
    "-v /root/noir-agent/.env:/app/.env "
    "-v /root/noir-agent/noir-vps:/app/noir-vps "
    "noir-agent-base:latest python noir-vps/self_healer.py"
)
print(run_remote(healer_cmd))

# 3. Check Status
status_cmd = "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'"
print(run_remote(status_cmd))

print("=== RESTART COMPLETE ===")
