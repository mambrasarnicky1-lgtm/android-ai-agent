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
        print(f"Executing on VPS: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        ssh.close()
        return out if out else err
    except Exception as e:
        return f"SSH Error: {e}"

print("=== SYNCING VPS TO V21.0 AEGIS ===")

# 1. Pull latest code
sync_cmd = "cd /root/noir-agent; git fetch origin main; git reset --hard origin/main"
print(run_remote(sync_cmd))

# 2. Restart Containers with new Healer
restart_cmd = "cd /root/noir-agent; docker-compose up -d --remove-orphans"
print(run_remote(restart_cmd))

# 3. Check Status
status_cmd = "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'"
print(run_remote(status_cmd))

print("=== VPS SYNC COMPLETE ===")
